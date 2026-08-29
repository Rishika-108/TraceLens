from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import (
    auth,
    cases,
    entities,
    evidence,
    investigations,
    relationships,
    reports,
    search,
    timelines,
)
from app.core.config import settings
from app.core.logging import logger
from app.db.database import Base, engine
import app.models  # Ensure all model tables are registered


from pathlib import Path
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TraceLens Evidence Intelligence Platform v%s...", settings.APP_VERSION)
    try:
        # Ensure evidence storage path exists
        Path(settings.STORAGE_PATH).mkdir(parents=True, exist_ok=True)

        # On PostgreSQL, ensure pgvector extension exists before table creation
        if engine.dialect.name == "postgresql":
            from sqlalchemy import text
            try:
                with engine.connect() as conn:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    conn.commit()
                logger.info("PostgreSQL pgvector extension verified.")
            except Exception as ext_err:
                logger.warning("Notice on pgvector extension check: %s", ext_err)

        # Automatically ensure all tables exist in database on startup
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema synchronized successfully.")
    except Exception as e:
        logger.warning("Database schema init notice: %s", e)
    yield
    logger.info("Shutting down TraceLens Engine")


app = FastAPI(
    title="TraceLens",
    description="AI-assisted Digital Forensics Investigation Platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(cases.router, prefix="/api/cases", tags=["Cases"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(entities.router, prefix="/api/entities", tags=["Entities"])
app.include_router(relationships.router, prefix="/api/relationships", tags=["Relationships"])
app.include_router(timelines.router, prefix="/api/timelines", tags=["Timelines"])
app.include_router(investigations.router, prefix="/api/investigations", tags=["Investigations"])
app.include_router(search.router, prefix="/api/search", tags=["Semantic Search"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": engine.dialect.name,
    }


# Check for pre-built frontend distribution (optional unified deployment)
client_dist = Path(__file__).resolve().parent.parent.parent / "Client" / "dist"
if client_dist.exists() and (client_dist / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(client_dist), html=True), name="frontend")
else:
    @app.get("/", tags=["Health"])
    async def root():
        return {
            "application": "TraceLens",
            "status": "running",
            "version": settings.APP_VERSION,
        }