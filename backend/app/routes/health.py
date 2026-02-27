"""
FasalDrishti - Health Check Route
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "FasalDrishti API",
        "version": "1.0.0",
    }
