from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import (
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting TraceLens Evidence Intelligence Engine....")
    yield
    # Shutdown
    print("Shutting down TraceLens Engine")


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
app.include_router(cases.router, prefix="/api/cases", tags=["Cases"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(entities.router, prefix="/api/entities", tags=["Entities"])
app.include_router(relationships.router, prefix="/api/relationships", tags=["Relationships"])
app.include_router(timelines.router, prefix="/api/timelines", tags=["Timelines"])
app.include_router(investigations.router, prefix="/api/investigations", tags=["Investigations"])
app.include_router(search.router, prefix="/api/search", tags=["Semantic Search"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "application": "TraceLens",
        "status": "running",
        "version": settings.APP_VERSION,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
    }