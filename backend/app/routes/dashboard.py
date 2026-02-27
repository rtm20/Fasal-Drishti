"""
FasalDrishti - Dashboard Analytics Routes
"""

import logging
from collections import Counter
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.routes.analyze import scan_history
from app.data.disease_db import DISEASE_DATABASE, CROP_DISEASES, LANGUAGE_MAP

logger = logging.getLogger("fasaldrishti.dashboard")

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total = len(scan_history)
    
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

    # Calculate stats
    disease_counter = Counter(s["disease_name"] for s in scan_history if s["disease_key"] != "healthy")
    crop_counter = Counter(s["crop"] for s in scan_history)
    severity_counter = Counter(s["severity"] for s in scan_history)
    
    avg_confidence = sum(s["confidence"] for s in scan_history) / total

    top_diseases = [
        {"name": name, "count": count}
        for name, count in disease_counter.most_common(5)
    ]

    return {
        "total_scans": total,
        "diseases_detected": len(disease_counter),
        "crops_analyzed": len(crop_counter),
        "average_confidence": round(avg_confidence, 1),
        "top_diseases": top_diseases,
        "severity_distribution": {
            "none": severity_counter.get("none", 0),
            "mild": severity_counter.get("mild", 0),
            "moderate": severity_counter.get("moderate", 0),
            "severe": severity_counter.get("severe", 0),
        },
        "crop_distribution": dict(crop_counter),
        "recent_scans": sorted(scan_history, key=lambda x: x["timestamp"], reverse=True)[:10],
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
