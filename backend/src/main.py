import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from src.agents.mistral_utils import AgentError, AgentTimeoutError
from src.api.v1.audit_events import router as audit_events_router
from src.api.v1.auth import router as auth_router
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
from src.middleware.auth import verify_token
from src.middleware.rate_limit import get_rate_limit_key

logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=get_rate_limit_key,
    enabled=settings.rate_limit_enabled,
)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Manage async engine lifecycle."""
    yield
    await engine.dispose()


app = FastAPI(
    title="Entre Deux API",
    description="FHIR-native AI companion for chronic condition patients",
    version="0.4.0",
    lifespan=lifespan,
)

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Handle rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Trop de requetes. Veuillez patienter avant de reessayer.",
            "code": "RATE_LIMIT_EXCEEDED",
        },
    )


@app.exception_handler(AgentTimeoutError)
async def agent_timeout_handler(
    request: Request, exc: AgentTimeoutError
) -> JSONResponse:
    """Handle AI agent timeout errors."""
    logger.warning("Agent timeout: %s", exc)
    return JSONResponse(
        status_code=504,
        content={
            "detail": "Le service d'IA met trop de temps a repondre.",
            "code": "AI_TIMEOUT",
        },
    )


@app.exception_handler(AgentError)
async def agent_error_handler(request: Request, exc: AgentError) -> JSONResponse:
    """Handle AI agent errors."""
    logger.error("Agent error: %s", exc)
    return JSONResponse(
        status_code=502,
        content={
            "detail": "Le service d'IA est temporairement indisponible.",
            "code": "AI_UNAVAILABLE",
        },
    )


app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(
    patients_router, prefix="/api/v1", dependencies=[Depends(verify_token)]
)
app.include_router(
    observations_router, prefix="/api/v1", dependencies=[Depends(verify_token)]
)
app.include_router(
    questionnaire_responses_router,
    prefix="/api/v1",
    dependencies=[Depends(verify_token)],
)
app.include_router(
    compositions_router, prefix="/api/v1", dependencies=[Depends(verify_token)]
)
app.include_router(
    consents_router, prefix="/api/v1", dependencies=[Depends(verify_token)]
)
app.include_router(
    audit_events_router, prefix="/api/v1", dependencies=[Depends(verify_token)]
)
