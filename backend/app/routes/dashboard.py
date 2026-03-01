"""
FasalDrishti - Dashboard Analytics Routes
Powered by Amazon DynamoDB for persistent scan data.
"""

import logging
from collections import Counter
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.services.dynamodb_service import get_scan_stats, get_recent_scans
from app.data.disease_db import DISEASE_DATABASE, CROP_DISEASES, LANGUAGE_MAP

logger = logging.getLogger("fasaldrishti.dashboard")

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats():
    """Get dashboard statistics from DynamoDB"""
    try:
        # Try DynamoDB first
        db_stats = await get_scan_stats()
        recent = await get_recent_scans(limit=10)

        total = db_stats.get("total_scans", 0)

        if total == 0:
            return {
                "total_scans": 0,
                "diseases_detected": 0,
                "crops_analyzed": 0,
                "average_confidence": 0,
                "top_diseases": [],
                "severity_distribution": {"mild": 0, "moderate": 0, "severe": 0},
                "crop_distribution": {},
                "recent_scans": [],
            }

        return {
            "total_scans": total,
            "diseases_detected": db_stats.get("diseases_detected", 0),
            "crops_analyzed": db_stats.get("crops_analyzed", 0),
            "average_confidence": db_stats.get("average_confidence", 0),
            "top_diseases": db_stats.get("top_diseases", []),
            "severity_distribution": db_stats.get("severity_distribution", {"mild": 0, "moderate": 0, "severe": 0}),
            "crop_distribution": db_stats.get("crop_distribution", {}),
            "recent_scans": recent,
        }
    except Exception as e:
        logger.warning(f"DynamoDB dashboard query failed: {e}")
        return {
            "total_scans": 0,
            "diseases_detected": 0,
            "crops_analyzed": 0,
            "average_confidence": 0,
            "top_diseases": [],
            "severity_distribution": {"mild": 0, "moderate": 0, "severe": 0},
            "crop_distribution": {},
            "recent_scans": [],
            "note": "DynamoDB temporarily unavailable",
        }


@router.get("/supported")
async def get_supported_info():
    """Get info about supported crops, diseases, and languages"""
    return {
        "crops": list(CROP_DISEASES.keys()),
        "diseases": {
            key: {
                "name": val["disease_name"],
                "hindi_name": val["hindi_name"],
                "crop": val["crop"],
            }
            for key, val in DISEASE_DATABASE.items()
        },
        "languages": LANGUAGE_MAP,
        "total_diseases": len(DISEASE_DATABASE) - 1,  # Exclude healthy
        "total_crops": len(CROP_DISEASES),
        "total_languages": len(LANGUAGE_MAP),
    }
