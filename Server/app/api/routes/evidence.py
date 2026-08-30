from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.ai.embeddings.generator import create_embeddings_batch
from app.api.dependencies import get_current_user
from app.core.logging import logger
from app.db.session import SessionLocal, get_db
from app.models.artifact import Artifact
from app.models.evidence import Evidence
from app.models.user import User
from app.pipelines.embedding_generation import prepare_artifact_text
from app.pipelines.entity_extraction import extract_entities
from app.pipelines.ingestion import ingest
from app.pipelines.relationship_discovery import discover_relationships
from app.pipelines.timeline_reconstruction import build_timeline
from app.repositories.artifact_repository import ArtifactRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.entity_repository import EntityRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.relationship_repository import RelationshipRepository
from app.repositories.timeline_repository import TimelineRepository
from app.schemas.artifact import ArtifactResponse
from app.schemas.evidence import EvidenceCreate, EvidenceResponse
from app.services.storage_service import StorageService

router = APIRouter()

MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB payload protection


def _run_evidence_pipeline(
    db: Session,
    evidence_id: str,
    case_id: str,
    file_path: str,
    file_type: str | None,
):
    """
    Executes parsing, batch embeddings, entity extraction, cross-file relationships, and timeline.
    """
    # Step 1: Ingest and parse
    parsed_items = ingest(
        file_path=file_path,
        evidence_type_hint=file_type,
    )

    # Step 2: Batch generate embeddings
    texts_for_embedding = [
        prepare_artifact_text({
            "artifact_type": item.get("artifact_type", "UNKNOWN"),
            "content": item.get("content", {}),
            "timestamp": item.get("timestamp"),
            "raw_data": item.get("raw_data"),
        })
        for item in parsed_items
    ]
    embeddings = create_embeddings_batch(texts_for_embedding)

    artifact_records = []
    artifact_dicts_for_pipeline = []

    for idx, item in enumerate(parsed_items):
        art_id = str(uuid4())
        art_type = item.get("artifact_type", "UNKNOWN")
        content = item.get("content", {})
        raw_data = item.get("raw_data")
        ts = item.get("timestamp")
        emb = embeddings[idx] if idx < len(embeddings) else None

        artifact_records.append({
            "id": art_id,
            "evidence_id": evidence_id,
            "artifact_type": art_type,
            "content": content,
            "raw_data": raw_data,
            "timestamp": ts,
            "parser_stage": "INDEXED",
            "embedding": emb,
        })

        artifact_dicts_for_pipeline.append({
            "id": art_id,
            "evidence_id": evidence_id,
            "case_id": case_id,
            "artifact_type": art_type,
            "content": content,
            "raw_data": raw_data,
            "timestamp": ts,
        })

    if artifact_records:
        ArtifactRepository.bulk_create(db, artifact_records)

    # Step 3: Extract Entities & Cross-File Relationship Discovery
    extracted_entities = extract_entities(artifact_dicts_for_pipeline, case_id)
    if extracted_entities:
        EntityRepository.bulk_create(db, extracted_entities)

    all_case_entities = EntityRepository.get_by_case(db, case_id)
    entity_dicts_for_discovery = [
        {
            "id": e.id,
            "case_id": e.case_id,
            "artifact_id": e.artifact_id,
            "entity_type": e.entity_type,
            "value": e.value,
        }
        for e in all_case_entities
    ]

    discovered_rels = discover_relationships(entity_dicts_for_discovery, artifact_dicts_for_pipeline, case_id)
    if discovered_rels:
        RelationshipRepository.bulk_create(db, discovered_rels)

    # Step 4: Reconstruct Chronological Timeline
    timeline_events = build_timeline(artifact_dicts_for_pipeline, case_id)
    if timeline_events:
        TimelineRepository.bulk_create(db, timeline_events)


def _process_evidence_background(
    evidence_id: str,
    case_id: str,
    file_path: str,
    file_type: str | None,
):
    """
    Background worker task to run the complete forensic pipeline without blocking HTTP requests.
    """
    db = SessionLocal()
    try:
        _run_evidence_pipeline(
            db=db,
            evidence_id=evidence_id,
            case_id=case_id,
            file_path=file_path,
            file_type=file_type,
        )
        EvidenceRepository.update_status(
            db,
            evidence_id=evidence_id,
            status="COMPLETED",
        )
        logger.info("Evidence %s processed successfully in background.", evidence_id)
    except Exception as e:
        logger.error("Background evidence processing failed for %s: %s", evidence_id, e, exc_info=True)
        try:
            db.rollback()
            db.query(Artifact).filter(Artifact.evidence_id == evidence_id).delete()
            db.commit()
        except Exception:
            db.rollback()

        EvidenceRepository.update_status(
            db,
            evidence_id=evidence_id,
            status="FAILED",
            error_message=f"Ingestion failed: {str(e)[:150]}",
        )
    finally:
        db.close()


@router.post(
    "/upload",
    response_model=EvidenceResponse,
    status_code=201,
    summary="Upload evidence file with decoupled background processing",
)
async def upload_evidence_file(
    background_tasks: BackgroundTasks,
    case_id: str = Form(..., description="Target Case ID"),
    file: UploadFile = File(..., description="Raw Evidence File"),
    file_type: str | None = Form(None, description="Optional evidence category hint (e.g., WHATSAPP, CALL, EMAIL)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify case exists and check authorization
    case = CaseRepository.get_by_id(db, case_id)
    if not case:
        raise HTTPException(
            status_code=404,
            detail=f"Case with ID '{case_id}' not found.",
        )

    if current_user.role != "ADMIN" and case.owner_id and case.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: this case belongs to another investigator.",
        )

    evidence_id = str(uuid4())

    try:
        # Step 1: Save raw evidence with streaming SHA-256 calculation
        storage_meta = await StorageService.save_upload_file(
            case_id=case_id,
            upload_file=file,
            evidence_id=evidence_id,
        )

        if storage_meta["file_size"] > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds maximum allowed size of {MAX_UPLOAD_SIZE // (1024 * 1024)}MB.",
            )

        detected_type = file_type or file.content_type or "UNKNOWN"

        # Step 2: Create initial Evidence record in DB
        evidence = Evidence(
            id=evidence_id,
            case_id=case_id,
            filename=storage_meta["filename"],
            file_type=detected_type,
            file_path=storage_meta["file_path"],
            file_hash=storage_meta["file_hash"],
            file_size=storage_meta["file_size"],
            status="PROCESSING",
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)

        # Step 3: Dispatch pipeline to background task
        background_tasks.add_task(
            _process_evidence_background,
            evidence_id=evidence_id,
            case_id=case_id,
            file_path=storage_meta["file_path"],
            file_type=detected_type,
        )

        return evidence

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evidence upload staging failed for {evidence_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Evidence file staging failed. Please verify file format and disk space.",
        )


@router.post(
    "/{evidence_id}/reprocess",
    response_model=EvidenceResponse,
    summary="Reprocess an existing evidence file in background",
)
async def reprocess_evidence(
    evidence_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    evidence = EvidenceRepository.get_by_id(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    case = CaseRepository.get_by_id(db, evidence.case_id)
    if case and current_user.role != "ADMIN" and case.owner_id and case.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if not evidence.file_path or not Path(evidence.file_path).exists():
        raise HTTPException(status_code=400, detail="Stored raw evidence file no longer exists on disk.")

    evidence.status = "PROCESSING"
    evidence.error_message = None
    db.commit()
    db.refresh(evidence)

    # Clean previous partial artifacts
    db.query(Artifact).filter(Artifact.evidence_id == evidence_id).delete()
    db.commit()

    background_tasks.add_task(
        _process_evidence_background,
        evidence_id=evidence_id,
        case_id=evidence.case_id,
        file_path=evidence.file_path,
        file_type=evidence.file_type,
    )

    return evidence


@router.delete(
    "/{evidence_id}",
    summary="Delete an evidence item and all derived artifacts",
)
async def delete_evidence(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    evidence = EvidenceRepository.get_by_id(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    case = CaseRepository.get_by_id(db, evidence.case_id)
    if case and current_user.role != "ADMIN" and case.owner_id and case.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Clean disk file if present
    if evidence.file_path:
        try:
            Path(evidence.file_path).unlink(missing_ok=True)
        except Exception:
            pass

    db.delete(evidence)
    db.commit()
    return {"message": "Evidence deleted successfully."}


@router.post(
    "/",
    response_model=EvidenceResponse,
    summary="Register evidence metadata record",
)
async def create_evidence(
    evidence: EvidenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = CaseRepository.get_by_id(db, evidence.case_id)
    if not case:
        raise HTTPException(
            status_code=404,
            detail=f"Case with ID '{evidence.case_id}' not found.",
        )
    return EvidenceRepository.create(
        db,
        evidence,
    )


@router.get(
    "/case/{case_id}",
    response_model=list[EvidenceResponse],
    summary="Get all evidence items for a case",
)
async def get_evidence_by_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Sweep and fail stale processing records older than 3 minutes
    cutoff = datetime.utcnow() - timedelta(minutes=3)
    stale_items = (
        db.query(Evidence)
        .filter(Evidence.case_id == case_id, Evidence.status == "PROCESSING", Evidence.uploaded_at < cutoff)
        .all()
    )
    if stale_items:
        for item in stale_items:
            item.status = "FAILED"
            item.error_message = "Processing timed out or was interrupted. Click reprocess to retry."
        db.commit()

    return EvidenceRepository.get_by_case(
        db,
        case_id,
    )


@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse,
    summary="Get evidence item by ID",
)
async def get_evidence(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    evidence = EvidenceRepository.get_by_id(
        db,
        evidence_id,
    )
    if not evidence:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found",
        )
    return evidence


@router.get(
    "/{evidence_id}/artifacts",
    response_model=list[ArtifactResponse],
    summary="Get all parsed artifacts for an evidence item",
)
async def get_evidence_artifacts(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    evidence = EvidenceRepository.get_by_id(db, evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found",
        )
    return ArtifactRepository.get_by_evidence(db, evidence_id)