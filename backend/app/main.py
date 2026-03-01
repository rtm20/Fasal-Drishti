"""
FasalDrishti - AI Crop Disease Detection Backend
Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app.routes.analyze import router as analyze_router
from app.routes.whatsapp import router as whatsapp_router
from app.routes.dashboard import router as dashboard_router
from app.routes.health import router as health_router
from app.config import get_settings

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fasaldrishti")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🌱 FasalDrishti Backend Starting...")
    logger.info(f"   Environment: {settings.app_env}")
    logger.info(f"   Region: {settings.aws_region}")
    logger.info(f"   Twilio SID set: {bool(settings.twilio_account_sid)}")
    logger.info(f"   Twilio SID value: {settings.twilio_account_sid[:8]}..." if settings.twilio_account_sid else "   Twilio SID value: EMPTY")
    logger.info(f"   Public URL: {settings.public_url or 'NOT SET'}")

    # Initialize DynamoDB tables (creates if not exist)
    try:
        from app.services.dynamodb_service import ensure_tables_exist
        table_status = ensure_tables_exist()  # sync function, no await
        logger.info(f"   DynamoDB tables: {table_status}")
    except Exception as e:
        logger.warning(f"   DynamoDB init skipped: {e}")

    # Log startup to CloudWatch
    try:
        from app.services.cloudwatch_service import cloudwatch_logger
        from app.services.ai_service import get_pipeline_status
        pipeline = get_pipeline_status()
        cloudwatch_logger.log_startup({
            "dynamodb": "initialized",
            "pipeline": pipeline.get("active_engine", "unknown"),
            "region": settings.aws_region,
        })
        logger.info("   CloudWatch logging: active")
    except Exception as e:
        logger.warning(f"   CloudWatch init skipped: {e}")

    yield
    logger.info("🛑 FasalDrishti Backend Shutting Down...")


app = FastAPI(
    title="FasalDrishti API",
    description="AI-Powered Crop Disease Detection for Indian Farmers",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "*",  # For hackathon demo - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(analyze_router, prefix="/api", tags=["Analysis"])
app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
async def root():
    return {
        "name": "FasalDrishti API",
        "version": "1.0.0",
        "status": "running",
        "description": "AI-Powered Crop Disease Detection for Indian Farmers",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", settings.app_port))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=(settings.app_env != "production"))
