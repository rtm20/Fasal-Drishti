"""
FasalDrishti - Image Analysis Routes
Core endpoint for crop disease detection.
"""

import base64
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from app.services.ai_service import (
    analyze_crop_image,
    get_disease_by_key,
    get_all_diseases,
    get_supported_crops,
)
from app.services.dynamodb_service import save_scan, get_recent_scans
from app.services.cloudwatch_service import cloudwatch_logger, publish_scan_metric

logger = logging.getLogger("fasaldrishti.analyze")

router = APIRouter()


def _flatten_result(result: dict, scan_id: str) -> dict:
    """Convert nested AI result to flat response for frontend."""
    analysis = result["analysis"]
    treatment = result["treatment"]
    metadata = result.get("metadata", {})
    return {
        "scan_id": scan_id,
        "success": True,
        # Core identification
        "disease": analysis["disease_key"],
        "disease_name": analysis["disease_name"],
        "hindi_name": analysis.get("hindi_name", ""),
        "scientific_name": analysis.get("scientific_name", ""),
        "crop": analysis["crop"],
        "category": analysis.get("category", ""),
        "is_healthy": analysis.get("is_healthy", False),
        # Confidence and severity
        "confidence": analysis["confidence"] / 100 if analysis["confidence"] > 1 else analysis["confidence"],
        "severity": analysis["severity"],
        # Descriptions
        "description": analysis.get("description_translated", analysis.get("description", "")),
        "description_hindi": analysis.get("description_hindi", ""),
        # Symptoms
        "symptoms": analysis.get("symptoms_observed", analysis.get("all_symptoms", [])),
        # Treatments (flatten chemical treatments)
        "treatments": [
            {
                "name": t["name"],
                "dosage": t.get("dosage", ""),
                "application": t.get("method", t.get("frequency", "")),
                "cost": f"\u20b9{t['cost_per_acre']}/acre" if t.get("cost_per_acre") else "",
            }
            for t in treatment.get("chemical", [])
        ],
        "organic_treatments": treatment.get("organic", []),
        "prevention": treatment.get("prevention", []),
        # Metadata
        "favorable_conditions": metadata.get("favorable_conditions", ""),
        "analysis_engine": metadata.get("analysis_engine", "fallback_demo"),
        "pipeline_latency_ms": metadata.get("pipeline_latency_ms", 0),
        "ai_notes": metadata.get("ai_notes", ""),
    }


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    language: str = Form(default="en"),
    crop_hint: Optional[str] = Form(default=None),
    latitude: Optional[float] = Form(default=None),
    longitude: Optional[float] = Form(default=None),
):
    """
    Analyze a crop image for disease detection.
    
    - **file**: Image file (JPEG, PNG)
    - **language**: Response language (en, hi, ta, te, kn, mr, bn, gu, pa)
    - **crop_hint**: Optional hint about the crop type
    - **latitude/longitude**: Optional location for nearby shop finder
    """
    try:
        # Validate file type
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload JPEG, PNG, or WebP images.",
            )

        # Read and encode image
        image_bytes = await file.read()
        
        # Check file size (max 10MB)
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Image too large. Maximum size is 10MB.",
            )

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        media_type = file.content_type or "image/jpeg"

        # Run AI analysis
        result = await analyze_crop_image(image_base64, media_type, language, "web")

        # Generate scan ID
        scan_id = str(uuid.uuid4())[:8]

        # Store scan record in DynamoDB (persistent)
        scan_record = {
            "scan_id": scan_id,
            "crop": result["analysis"]["crop"],
            "disease_key": result["analysis"]["disease_key"],
            "disease_name": result["analysis"]["disease_name"],
            "severity": result["analysis"]["severity"],
            "confidence": result["analysis"]["confidence"],
            "timestamp": datetime.utcnow().isoformat(),
            "location": {"lat": latitude, "lng": longitude} if latitude else None,
            "analysis_engine": result.get("metadata", {}).get("analysis_engine", "unknown"),
            "language": language,
            "source": "web",
        }
        try:
            await save_scan(scan_record)
        except Exception as db_err:
            logger.warning(f"DynamoDB save failed (non-blocking): {db_err}")

        # Publish metrics to CloudWatch
        try:
            latency = result.get("metadata", {}).get("pipeline_latency_ms", 0)
            publish_scan_metric(
                crop=scan_record["crop"],
                disease=scan_record["disease_key"],
                severity=scan_record["severity"],
                latency_ms=latency,
                analysis_method=scan_record.get("analysis_engine", "unknown"),
                success=True,
            )
            cloudwatch_logger.log_scan(
                scan_id=scan_id,
                crop=scan_record["crop"],
                disease=scan_record["disease_key"],
                severity=scan_record["severity"],
                confidence=scan_record["confidence"],
                analysis_method=scan_record.get("analysis_engine", "unknown"),
                latency_ms=latency,
                language=language,
            )
        except Exception:
            pass

        # Flatten response for frontend consumption
        analysis = result["analysis"]
        flat_response = _flatten_result(result, scan_id)

        logger.info(
            f"Scan {scan_id}: {analysis['disease_name']} "
            f"({analysis['confidence']}% confidence)"
        )

        return JSONResponse(content=flat_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/base64")
async def analyze_base64(
    request: dict,
):
    """
    Analyze a base64-encoded crop image.
    Alternative endpoint for WhatsApp/API integrations.
    """
    try:
        image_base64 = request.get("image_base64", "")
        language = request.get("language", "en")
        media_type = request.get("media_type", "image/jpeg")

        if not image_base64:
            raise HTTPException(status_code=400, detail="image_base64 is required")

        # Remove data URI prefix if present
        if "base64," in image_base64:
            image_base64 = image_base64.split("base64,")[1]

        result = await analyze_crop_image(image_base64, media_type, language)

        scan_id = str(uuid.uuid4())[:8]
        scan_record = {
            "scan_id": scan_id,
            "crop": result["analysis"]["crop"],
            "disease_key": result["analysis"]["disease_key"],
            "disease_name": result["analysis"]["disease_name"],
            "severity": result["analysis"]["severity"],
            "confidence": result["analysis"]["confidence"],
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_engine": result.get("metadata", {}).get("analysis_engine", "unknown"),
            "language": language,
            "source": "api",
        }
        try:
            await save_scan(scan_record)
        except Exception as db_err:
            logger.warning(f"DynamoDB save failed (non-blocking): {db_err}")

        try:
            latency = result.get("metadata", {}).get("pipeline_latency_ms", 0)
            publish_scan_metric(
                crop=scan_record["crop"],
                disease=scan_record["disease_key"],
                severity=scan_record["severity"],
                latency_ms=latency,
                analysis_method=scan_record.get("analysis_engine", "unknown"),
                success=True,
            )
        except Exception:
            pass

        flat_response = _flatten_result(result, scan_id)
        logger.info(
            f"Base64 scan {scan_id}: {result['analysis']['disease_name']} "
            f"({result['analysis']['confidence']}% confidence)"
        )
        return JSONResponse(content=flat_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Base64 analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diseases")
async def list_diseases():
    """Get all diseases in the database"""
    diseases = get_all_diseases()
    return {
        "total": len(diseases),
        "diseases": {
            key: {
                "disease_name": val["disease_name"],
                "hindi_name": val["hindi_name"],
                "crop": val["crop"],
                "category": val["category"],
                "severity_typical": val["severity_typical"],
            }
            for key, val in diseases.items()
        },
    }


@router.get("/diseases/{disease_key}")
async def get_disease(disease_key: str):
    """Get detailed info about a specific disease"""
    disease = get_disease_by_key(disease_key)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return disease


@router.get("/crops")
async def list_crops():
    """Get list of supported crops"""
    return {"crops": get_supported_crops()}


@router.get("/scans")
async def get_scan_history():
    """Get recent scan history from DynamoDB"""
    try:
        scans = await get_recent_scans(limit=50)
        return {
            "total": len(scans),
            "scans": scans,
        }
    except Exception as e:
        logger.warning(f"DynamoDB scan fetch failed: {e}")
        return {
            "total": 0,
            "scans": [],
            "note": "DynamoDB temporarily unavailable",
        }
