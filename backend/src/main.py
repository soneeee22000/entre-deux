from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.audit_events import router as audit_events_router
from src.api.v1.compositions import router as compositions_router
from src.api.v1.consents import router as consents_router
from src.api.v1.health import router as health_router
from src.api.v1.observations import router as observations_router
from src.api.v1.patients import router as patients_router
from src.api.v1.questionnaire_responses import (
    router as questionnaire_responses_router,
)
from src.config.settings import settings
from src.db.engine import engine


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Manage async engine lifecycle."""
    yield
    await engine.dispose()


app = FastAPI(
    title="Entre Deux API",
    description="FHIR-native AI companion for chronic condition patients",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(patients_router, prefix="/api/v1")
app.include_router(observations_router, prefix="/api/v1")
app.include_router(questionnaire_responses_router, prefix="/api/v1")
app.include_router(compositions_router, prefix="/api/v1")
app.include_router(consents_router, prefix="/api/v1")
app.include_router(audit_events_router, prefix="/api/v1")
