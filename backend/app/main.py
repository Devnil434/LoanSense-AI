import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, metrics, predict, risk
from app.core.config import get_settings
from app.core.database import Base, engine
from app.models import models  # noqa: F401  (ensures models are registered)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("loansense")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured. LoanSense AI backend starting up.")
    yield
    logger.info("LoanSense AI backend shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Loan Approval & Credit Risk Assessment Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(predict.router, prefix=settings.API_V1_PREFIX)
app.include_router(risk.router, prefix=settings.API_V1_PREFIX)
app.include_router(metrics.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
        "api_prefix": settings.API_V1_PREFIX,
    }
