from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.ai.embeddings.generator import create_embedding
from app.api.dependencies import get_current_user
from app.core.logging import logger
from app.db.session import get_db
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


@router.post(
    "/upload",
    response_model=EvidenceResponse,
    status_code=201,
    summary="Upload evidence file with end-to-end forensic processing (parsing, entities, timeline, vectors)",
)
async def upload_evidence_file(
    case_id: str = Form(..., description="Target Case ID"),
    file: UploadFile = File(..., description="Raw Evidence File"),
    file_type: str | None = Form(None, description="Optional evidence category hint (e.g., WHATSAPP, CALL, EMAIL)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify case exists
    case = CaseRepository.get_by_id(db, case_id)
    if not case:
        raise HTTPException(
            status_code=404,
            detail=f"Case with ID '{case_id}' not found.",
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

        # Step 3: Run parsing pipeline
        parsed_items = ingest(
            file_path=storage_meta["file_path"],
            evidence_type_hint=file_type,
        )

        # Step 4: Persist parsed artifacts with pgvector embeddings
        artifact_records = []
        artifact_dicts_for_pipeline = []

        for item in parsed_items:
            art_id = str(uuid4())
            art_type = item.get("artifact_type", "UNKNOWN")
            content = item.get("content", {})
            raw_data = item.get("raw_data")
            ts = item.get("timestamp")

            text_for_embedding = prepare_artifact_text({
                "artifact_type": art_type,
                "content": content,
                "timestamp": ts,
                "raw_data": raw_data,
            })
            embedding = create_embedding(text_for_embedding)

            artifact_records.append({
                "id": art_id,
                "evidence_id": evidence_id,
                "artifact_type": art_type,
                "content": content,
                "raw_data": raw_data,
                "timestamp": ts,
                "parser_stage": "INDEXED",
                "embedding": embedding,
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

        # Step 5: Extract Entities & Cross-File Relationship Discovery
        extracted_entities = extract_entities(artifact_dicts_for_pipeline, case_id)
        if extracted_entities:
            EntityRepository.bulk_create(db, extracted_entities)

        # Query all case entities so newly uploaded evidence links with previously uploaded files
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

        # Step 6: Reconstruct Chronological Timeline
        timeline_events = build_timeline(artifact_dicts_for_pipeline, case_id)
        if timeline_events:
            TimelineRepository.bulk_create(db, timeline_events)

        # Step 7: Mark evidence as COMPLETED
        EvidenceRepository.update_status(
            db,
            evidence_id=evidence_id,
            status="COMPLETED",
        )
        db.refresh(evidence)
        return evidence

    except Exception as e:
        logger.error(f"Evidence processing failed for {evidence_id}: {e}", exc_info=True)
        db.rollback()

        # Atomic cleanup: Remove partial artifacts to prevent broken records
        try:
            db.query(Artifact).filter(Artifact.evidence_id == evidence_id).delete()
            db.commit()
        except Exception:
            db.rollback()

        # Update evidence record to FAILED
        EvidenceRepository.update_status(
            db,
            evidence_id=evidence_id,
            status="FAILED",
            error_message="Evidence processing encountered an internal error during parsing or entity extraction.",
        )

        raise HTTPException(
            status_code=500,
            detail="Evidence processing failed. Please verify file integrity and encoding.",
        )


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