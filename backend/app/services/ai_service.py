"""
FasalDrishti - AI Crop Disease Detection Pipeline
==================================================
Production-grade multi-stage pipeline using AWS services:

  Stage 1: Image Preprocessing (validate, resize, optimize)
  Stage 2: Bedrock Claude 3 Vision — crop identification + disease analysis
  Stage 3: Disease Database enrichment (treatments, costs, prevention)
  Stage 4: Amazon Translate — multilingual output
  Stage 5: S3 archival (optional) — store scan for analytics

Graceful fallback chain:
  Bedrock Vision → Rekognition Labels → Local Disease DB (demo mode)
"""

import base64
import json
import logging
import re
import time
from typing import Optional
from io import BytesIO

from app.data.disease_db import DISEASE_DATABASE, CROP_DISEASES
from app.config import get_settings

logger = logging.getLogger("fasaldrishti.ai")
settings = get_settings()

# ============================================================
# CIRCUIT BREAKER — skip Bedrock after repeated failures
# ============================================================
_bedrock_circuit = {
    "failures": 0,
    "last_failure_time": 0,
    "open": False,  # True = skip Bedrock entirely
}
BEDROCK_CIRCUIT_THRESHOLD = 2   # failures before opening
BEDROCK_CIRCUIT_RESET_SECS = 300  # retry after 5 minutes

def _bedrock_circuit_is_open() -> bool:
    """Check if we should skip Bedrock (circuit is open)."""
    if not _bedrock_circuit["open"]:
        return False
    # Check if enough time has passed to retry
    elapsed = time.time() - _bedrock_circuit["last_failure_time"]
    if elapsed > BEDROCK_CIRCUIT_RESET_SECS:
        logger.info("Bedrock circuit breaker reset — will retry")
        _bedrock_circuit["open"] = False
        _bedrock_circuit["failures"] = 0
        return False
    return True

def _bedrock_circuit_record_failure():
    """Record a Bedrock failure; open circuit if threshold reached."""
    _bedrock_circuit["failures"] += 1
    _bedrock_circuit["last_failure_time"] = time.time()
    if _bedrock_circuit["failures"] >= BEDROCK_CIRCUIT_THRESHOLD:
        _bedrock_circuit["open"] = True
        logger.warning(f"Bedrock circuit breaker OPEN after {_bedrock_circuit['failures']} failures. Will retry in {BEDROCK_CIRCUIT_RESET_SECS}s")

def _bedrock_circuit_record_success():
    """Reset circuit breaker on success."""
    _bedrock_circuit["failures"] = 0
    _bedrock_circuit["open"] = False

# ============================================================
# AWS CLIENT FACTORY (lazy, cached)
# ============================================================
_clients: dict = {}


def _get_aws_client(service: str):
    """Get or create a cached boto3 client for an AWS service."""
    if service not in _clients:
        try:
            import boto3
            from botocore.config import Config
            # Short timeouts for Bedrock to avoid blocking WhatsApp webhook
            if service == "bedrock-runtime":
                svc_config = Config(
                    connect_timeout=5,
                    read_timeout=10,
                    retries={"max_attempts": 0},
                )
            else:
                svc_config = Config(
                    connect_timeout=5,
                    read_timeout=10,
                    retries={"max_attempts": 1},
                )
            kwargs = {"region_name": settings.aws_region, "config": svc_config}
            if settings.aws_access_key_id:
                kwargs["aws_access_key_id"] = settings.aws_access_key_id
            if settings.aws_secret_access_key:
                kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
            _clients[service] = boto3.client(service, **kwargs)
        except Exception as e:
            logger.warning(f"Could not create {service} client: {e}")
            return None
    return _clients[service]


def get_bedrock_client():
    return _get_aws_client("bedrock-runtime")


def get_translate_client():
    return _get_aws_client("translate")


def get_rekognition_client():
    return _get_aws_client("rekognition")


def get_s3_client():
    return _get_aws_client("s3")


# ============================================================
# STAGE 1: IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image_base64: str, media_type: str = "image/jpeg") -> tuple[str, str, dict]:
    """
    Validate and optimize the image for AI analysis.
    Returns: (processed_base64, media_type, metadata)
    """
    metadata = {"original_size_bytes": len(image_base64) * 3 // 4}

    try:
        from PIL import Image
        image_bytes = base64.b64decode(image_base64)
        img = Image.open(BytesIO(image_bytes))

        metadata["original_width"] = img.width
        metadata["original_height"] = img.height
        metadata["format"] = img.format or "JPEG"

        # Resize if too large (Bedrock max ~20MB, but we want fast analysis)
        MAX_DIM = 1024
        if img.width > MAX_DIM or img.height > MAX_DIM:
            img.thumbnail((MAX_DIM, MAX_DIM), Image.LANCZOS)
            metadata["resized"] = True
            metadata["new_width"] = img.width
            metadata["new_height"] = img.height

        # Convert RGBA → RGB (JPEG doesn't support alpha)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Re-encode as JPEG with good quality
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=90, optimize=True)
        processed_bytes = buffer.getvalue()
        processed_base64 = base64.b64encode(processed_bytes).decode("utf-8")

        metadata["processed_size_bytes"] = len(processed_bytes)
        logger.info(
            f"Image preprocessed: {metadata['original_size_bytes']}B → {metadata['processed_size_bytes']}B, "
            f"{img.width}x{img.height}"
        )
        return processed_base64, "image/jpeg", metadata

    except ImportError:
        logger.warning("Pillow not installed — skipping image preprocessing")
        return image_base64, media_type, metadata
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e} — using original")
        return image_base64, media_type, metadata


# ============================================================
# STAGE 2A: BEDROCK CLAUDE 3 VISION (PRIMARY)
# ============================================================

# Detailed prompt engineered for agricultural accuracy
CROP_ANALYSIS_PROMPT = """You are FasalDrishti, an expert AI agricultural pathologist specializing in Indian crop diseases.
You have deep knowledge of plant pathology, especially diseases affecting crops in India.

TASK: Analyze the provided crop image carefully and produce a detailed diagnosis.

STEP 1 — IDENTIFY THE CROP:
Look at leaf shape, size, color, stem structure, fruit/flower if visible.
Common Indian crops: Tomato, Rice (Paddy), Wheat, Cotton, Potato, Chili (Mirch), Onion,
Sugarcane, Maize, Soybean, Mustard, Groundnut, Mango, Banana, Grape.

STEP 2 — ASSESS PLANT HEALTH:
- Is the plant Healthy or Diseased?
- If diseased, what visual symptoms do you observe?
  (spots, lesions, discoloration, wilting, mold, deformation, necrosis, mosaic patterns, etc.)

STEP 3 — DIAGNOSE THE DISEASE:
Based on symptoms, identify the most likely disease.
Consider: fungal, bacterial, viral, nutrient deficiency, pest damage.

STEP 4 — RATE SEVERITY:
- "none" = healthy plant
- "mild" = early stage, <20% leaf area affected
- "moderate" = 20-50% affected, spreading
- "severe" = >50% affected, significant damage, yield loss likely

STEP 5 — MATCH TO KNOWN DATABASE KEY (if applicable):
tomato_early_blight, tomato_late_blight, tomato_leaf_curl,
rice_blast, rice_brown_spot,
wheat_leaf_rust, wheat_yellow_rust,
cotton_bacterial_blight,
potato_late_blight,
chili_anthracnose,
onion_purple_blotch,
healthy

If the disease doesn't match any above, use "unknown_disease" and provide the full name.

IMPORTANT: Respond ONLY with valid JSON. No markdown, no code blocks, no explanation text.

{
    "crop": "exact crop name (lowercase)",
    "is_healthy": false,
    "disease_key": "database_key or unknown_disease",
    "disease_name": "Full disease name in English",
    "disease_cause": "Fungal / Bacterial / Viral / Nutrient / Pest / Unknown",
    "confidence": 87,
    "severity": "moderate",
    "symptoms_observed": [
        "Detailed symptom 1 visible in image",
        "Detailed symptom 2 visible in image",
        "Detailed symptom 3 visible in image"
    ],
    "affected_area_percent": 35,
    "spread_risk": "high",
    "immediate_action_needed": true,
    "additional_notes": "Any extra observations about the image, environment, etc."
}
"""


async def _invoke_bedrock_bearer_token(request_body: dict) -> Optional[dict]:
    """
    Call Bedrock using the API Key (Bearer Token) instead of IAM SigV4.
    This bypasses INVALID_PAYMENT_INSTRUMENT issues from Marketplace.
    
    Uses HTTP POST to:
      https://bedrock-runtime.{region}.amazonaws.com/model/{model}/invoke
    with header: Authorization: Bearer {api-key}
    """
    bearer_token = settings.aws_bearer_token_bedrock
    if not bearer_token:
        return None

    import urllib.request
    import urllib.error

    # Strip the "apac." cross-region prefix for the direct API endpoint
    model_id = settings.bedrock_model_id
    # URL-encode the model ID (it contains slashes in ARN format sometimes)
    import urllib.parse
    encoded_model = urllib.parse.quote(model_id, safe="")

    url = f"https://bedrock-runtime.{settings.aws_region}.amazonaws.com/model/{encoded_model}/invoke"

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    body_bytes = json.dumps(request_body).encode("utf-8")

    req = urllib.request.Request(url, data=body_bytes, headers=headers, method="POST")

    try:
        start_time = time.time()
        with urllib.request.urlopen(req, timeout=8) as resp:
            latency_ms = int((time.time() - start_time) * 1000)
            response_body = json.loads(resp.read())
            return {"body": response_body, "latency_ms": latency_ms}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        logger.error(f"Bedrock Bearer Token API error {e.code}: {error_body[:500]}")
        return None
    except Exception as e:
        logger.error(f"Bedrock Bearer Token request failed: {e}")
        return None


async def analyze_image_with_bedrock(image_base64: str, media_type: str = "image/jpeg") -> Optional[dict]:
    """
    Send image to Amazon Bedrock Claude 3 Sonnet for comprehensive crop disease analysis.
    Uses vision capabilities for multi-stage identification:
      crop type → health status → disease diagnosis → severity rating
    
    Auth strategy:
      1. Try standard IAM SigV4 (boto3 invoke_model)
      2. If IAM fails (e.g. INVALID_PAYMENT_INSTRUMENT) → try Bearer Token API Key
    """

    # Build the multimodal request (shared by both auth methods)
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1500,
        "temperature": 0.1,  # Low temperature for consistent agricultural analysis
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": CROP_ANALYSIS_PROMPT,
                    },
                ],
            }
        ],
    }

    # --- Circuit Breaker Check ---
    if _bedrock_circuit_is_open():
        logger.info("Bedrock circuit breaker is OPEN — skipping Bedrock entirely")
        return None

    response_body = None
    latency_ms = 0
    auth_method = "iam"

    # --- Method 1: Standard IAM SigV4 via boto3 ---
    try:
        client = get_bedrock_client()
        if client:
            start_time = time.time()
            response = client.invoke_model(
                modelId=settings.bedrock_model_id,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json",
            )
            latency_ms = int((time.time() - start_time) * 1000)
            response_body = json.loads(response["body"].read())
            auth_method = "iam"
            logger.info(f"Bedrock IAM auth succeeded in {latency_ms}ms")
            _bedrock_circuit_record_success()
    except Exception as iam_err:
        logger.warning(f"Bedrock IAM auth failed: {iam_err}")
        response_body = None

    # --- Method 2: Bearer Token API Key (fallback) ---
    if response_body is None and settings.aws_bearer_token_bedrock:
        logger.info("Trying Bedrock Bearer Token auth...")
        bearer_result = await _invoke_bedrock_bearer_token(request_body)
        if bearer_result:
            response_body = bearer_result["body"]
            latency_ms = bearer_result["latency_ms"]
            auth_method = "bearer_token"
            logger.info(f"Bedrock Bearer Token auth succeeded in {latency_ms}ms")
            _bedrock_circuit_record_success()

    if response_body is None:
        _bedrock_circuit_record_failure()
        logger.error("Bedrock analysis failed with both IAM and Bearer Token")
        return None

    try:
        result_text = response_body["content"][0]["text"]
        input_tokens = response_body.get("usage", {}).get("input_tokens", 0)
        output_tokens = response_body.get("usage", {}).get("output_tokens", 0)

        logger.info(
            f"Bedrock response: {latency_ms}ms, tokens={input_tokens}+{output_tokens}, auth={auth_method}"
        )

        # Robust JSON extraction — handles markdown-wrapped responses too
        result = _extract_json(result_text)
        if result:
            result["_meta"] = {
                "engine": "bedrock",
                "model": settings.bedrock_model_id,
                "latency_ms": latency_ms,
                "tokens": input_tokens + output_tokens,
                "auth_method": auth_method,
            }
            logger.info(
                f"Bedrock diagnosis: crop={result.get('crop')}, "
                f"disease={result.get('disease_name')}, "
                f"confidence={result.get('confidence')}%, "
                f"severity={result.get('severity')}"
            )
            return result
        else:
            logger.warning(f"Could not parse JSON from Bedrock response: {result_text[:300]}")
            return None

    except Exception as e:
        logger.error(f"Bedrock response parsing failed: {e}")
        return None


def _extract_json(text: str) -> Optional[dict]:
    """Robustly extract JSON from AI response (handles markdown wrapping)."""
    # Strip markdown code blocks if present
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find a JSON object in the text
    # Use a balanced brace matcher for nested JSON
    brace_depth = 0
    start_idx = None
    for i, ch in enumerate(text):
        if ch == '{':
            if brace_depth == 0:
                start_idx = i
            brace_depth += 1
        elif ch == '}':
            brace_depth -= 1
            if brace_depth == 0 and start_idx is not None:
                try:
                    return json.loads(text[start_idx:i+1])
                except json.JSONDecodeError:
                    start_idx = None

    return None


# ============================================================
# STAGE 2B: REKOGNITION LABELS (SECONDARY FALLBACK)
# ============================================================

async def analyze_image_with_rekognition(image_base64: str) -> Optional[dict]:
    """
    Use Amazon Rekognition DetectLabels as a lightweight fallback.
    Identifies plant type and visual keywords (spots, lesions, wilting)
    that can be mapped to diseases in our database.
    """
    try:
        client = get_rekognition_client()
        if not client:
            return None

        image_bytes = base64.b64decode(image_base64)

        response = client.detect_labels(
            Image={"Bytes": image_bytes},
            MaxLabels=25,
            MinConfidence=50.0,
            Features=["GENERAL_LABELS"],
        )

        labels = []
        for label in response.get("Labels", []):
            labels.append({
                "name": label["Name"].lower(),
                "confidence": label["Confidence"],
                "parents": [p["Name"].lower() for p in label.get("Parents", [])],
            })

        logger.info(f"Rekognition labels: {[l['name'] for l in labels[:10]]}")

        # Map Rekognition labels to crop identification
        crop = _identify_crop_from_labels(labels)
        disease_key, disease_name, confidence = _identify_disease_from_labels(labels, crop)

        if crop:
            return {
                "crop": crop,
                "is_healthy": disease_key == "healthy",
                "disease_key": disease_key,
                "disease_name": disease_name,
                "disease_cause": "Unknown",
                "confidence": int(confidence),
                "severity": "moderate" if disease_key != "healthy" else "none",
                "symptoms_observed": [l["name"] for l in labels if l["name"] in
                    {"spot", "lesion", "blight", "rust", "mold", "wilt", "discoloration",
                     "yellowing", "brown", "rot", "fungus", "insect", "pest", "damage"}],
                "affected_area_percent": 0,
                "spread_risk": "unknown",
                "immediate_action_needed": disease_key != "healthy",
                "additional_notes": f"Identified via Rekognition label detection. Labels: {', '.join(l['name'] for l in labels[:8])}",
                "_meta": {"engine": "rekognition"},
            }
        return None

    except Exception as e:
        logger.warning(f"Rekognition analysis failed: {e}")
        return None


def _identify_crop_from_labels(labels: list) -> Optional[str]:
    """Map Rekognition labels to known crop types."""
    crop_keywords = {
        "tomato": ["tomato", "solanum"],
        "rice": ["rice", "paddy", "grain"],
        "wheat": ["wheat", "grain", "cereal"],
        "cotton": ["cotton"],
        "potato": ["potato"],
        "chili": ["chili", "pepper", "capsicum"],
        "onion": ["onion", "allium"],
        "maize": ["corn", "maize"],
        "sugarcane": ["sugarcane"],
        "soybean": ["soybean"],
    }
    label_names = {l["name"] for l in labels}
    for crop, keywords in crop_keywords.items():
        if any(kw in name for name in label_names for kw in keywords):
            return crop

    # Check for generic plant/leaf labels
    if label_names & {"plant", "leaf", "vegetation", "flora", "flower", "fruit"}:
        return "unknown_crop"
    return None


def _identify_disease_from_labels(labels: list, crop: Optional[str]) -> tuple[str, str, float]:
    """Map Rekognition labels to possible diseases."""
    label_names = {l["name"] for l in labels}
    disease_indicators = label_names & {
        "spot", "blight", "rust", "mold", "wilt", "rot", "fungus",
        "lesion", "discoloration", "yellowing", "browning", "damage",
        "insect", "pest", "mildew", "necrosis",
    }
    if not disease_indicators:
        return "healthy", "Healthy Plant", 75.0

    # Try to match crop-specific diseases
    if crop and crop in CROP_DISEASES:
        diseases_for_crop = CROP_DISEASES[crop]
        # Default to first disease for this crop
        default_key = diseases_for_crop[0] if diseases_for_crop else "healthy"
        disease_info = DISEASE_DATABASE.get(default_key, {})
        return default_key, disease_info.get("disease_name", "Unknown Disease"), 65.0

    return "unknown_disease", "Possible Disease Detected", 55.0


# ============================================================
# STAGE 2C: LOCAL FALLBACK (DEMO MODE)
# ============================================================

def fallback_analysis(image_base64: str = None) -> dict:
    """
    Fallback when all AWS services are unavailable.
    Returns a simulated analysis from the disease database for demo.
    """
    import random

    disease_keys = [k for k in DISEASE_DATABASE.keys() if k != "healthy"]
    selected_key = random.choice(disease_keys)
    disease = DISEASE_DATABASE[selected_key]

    return {
        "crop": disease["crop"].lower(),
        "is_healthy": False,
        "disease_key": selected_key,
        "disease_name": disease["disease_name"],
        "disease_cause": disease.get("category", "Unknown"),
        "confidence": random.randint(82, 96),
        "severity": disease["severity_typical"],
        "symptoms_observed": disease["symptoms"][:3],
        "affected_area_percent": random.randint(20, 60),
        "spread_risk": "moderate",
        "immediate_action_needed": True,
        "additional_notes": "⚠️ Demo mode — AWS Bedrock not connected. "
                           "Real AI analysis requires AWS credentials. "
                           "Disease shown is for demonstration purposes.",
        "_meta": {"engine": "fallback_demo"},
    }


# ============================================================
# STAGE 3: AMAZON TRANSLATE
# ============================================================

async def translate_text(text: str, target_lang: str = "hi") -> str:
    """Translate text using Amazon Translate."""
    try:
        client = get_translate_client()
        if not client:
            return text

        result = client.translate_text(
            Text=text[:5000],  # Translate API max 5000 chars
            SourceLanguageCode="en",
            TargetLanguageCode=target_lang,
        )
        return result["TranslatedText"]
    except Exception as e:
        logger.warning(f"Translation failed ({target_lang}): {e}")
        return text


async def translate_fields(fields: dict[str, str], target_lang: str) -> dict[str, str]:
    """Translate multiple text fields at once (batch)."""
    translated = {}
    for key, text in fields.items():
        if text:
            translated[key] = await translate_text(text, target_lang)
        else:
            translated[key] = text
    return translated


# ============================================================
# STAGE 4: S3 ARCHIVAL (scan image + result)
# ============================================================

async def archive_scan_to_s3(
    image_base64: str,
    result: dict,
    phone_number: str = "web",
    scan_id: str = "",
) -> Optional[str]:
    """
    Archive the scan image and result JSON to S3 for analytics.
    Returns the S3 key or None if archival fails/is disabled.
    """
    try:
        client = get_s3_client()
        if not client or not settings.s3_bucket_name:
            return None

        import uuid
        from datetime import datetime

        if not scan_id:
            scan_id = str(uuid.uuid4())[:8]

        date_prefix = datetime.utcnow().strftime("%Y/%m/%d")
        safe_phone = phone_number.replace("+", "").replace(":", "_")

        # Upload image
        image_key = f"scans/{date_prefix}/{safe_phone}/{scan_id}.jpg"
        client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=image_key,
            Body=base64.b64decode(image_base64),
            ContentType="image/jpeg",
            Metadata={
                "scan_id": scan_id,
                "phone": safe_phone,
                "crop": result.get("analysis", {}).get("crop", "unknown"),
                "disease": result.get("analysis", {}).get("disease_key", "unknown"),
            },
        )

        # Upload analysis JSON
        result_key = f"scans/{date_prefix}/{safe_phone}/{scan_id}_result.json"
        client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=result_key,
            Body=json.dumps(result, default=str, ensure_ascii=False),
            ContentType="application/json",
        )

        logger.info(f"Scan archived to S3: {image_key}")
        return image_key

    except Exception as e:
        logger.warning(f"S3 archival failed (non-blocking): {e}")
        return None


# ============================================================
# MAIN PIPELINE ORCHESTRATOR
# ============================================================

async def analyze_crop_image(
    image_base64: str,
    media_type: str = "image/jpeg",
    language: str = "en",
    phone_number: str = "web",
) -> dict:
    """
    FasalDrishti Core Pipeline
    ==========================
    Image → Preprocess → AI Analysis → DB Enrichment → Translation → Response

    Fallback chain:
      1. Amazon Bedrock Claude 3 Vision (best — real crop pathology AI)
      2. Amazon Rekognition DetectLabels (basic — label-based matching)
      3. Local disease database (demo — random selection for hackathon)
    """
    pipeline_start = time.time()

    # ── Stage 1: Preprocess ────────────────────────────────
    processed_b64, processed_type, img_meta = preprocess_image(image_base64, media_type)

    # ── Stage 2: AI Analysis (fallback chain) ──────────────
    ai_result = None
    analysis_engine = "fallback_demo"

    # Try Bedrock first (best quality)
    ai_result = await analyze_image_with_bedrock(processed_b64, processed_type)
    if ai_result:
        analysis_engine = "bedrock"
    else:
        # Try Rekognition as secondary
        logger.info("Bedrock unavailable — trying Rekognition")
        ai_result = await analyze_image_with_rekognition(processed_b64)
        if ai_result:
            analysis_engine = "rekognition"
        else:
            # Final fallback: demo mode
            logger.info("All AWS services unavailable — using demo fallback")
            ai_result = fallback_analysis(processed_b64)
            analysis_engine = "fallback_demo"

    # ── Stage 3: Disease DB Enrichment ─────────────────────
    disease_key = ai_result.get("disease_key", "healthy")
    # Handle unknown diseases not in our DB
    disease_info = DISEASE_DATABASE.get(disease_key)
    if not disease_info:
        # Try fuzzy matching by crop
        crop = ai_result.get("crop", "").lower()
        if crop in CROP_DISEASES and CROP_DISEASES[crop]:
            # Use the first disease for this crop as a close match
            disease_key = CROP_DISEASES[crop][0]
            disease_info = DISEASE_DATABASE[disease_key]
            logger.info(f"Mapped unknown disease to closest match: {disease_key}")
        else:
            disease_info = DISEASE_DATABASE.get("healthy", {})
            disease_key = "healthy"

    if ai_result.get("is_healthy", False):
        disease_info = DISEASE_DATABASE.get("healthy", disease_info)
        disease_key = "healthy"

    # ── Stage 4: Build response ────────────────────────────
    response = {
        "success": True,
        "analysis": {
            "crop": ai_result.get("crop", disease_info.get("crop", "unknown")).lower(),
            "crop_hindi": disease_info.get("crop_hindi", ""),
            "disease_key": disease_key,
            "disease_name": disease_info.get("disease_name", ai_result.get("disease_name", "Unknown")),
            "hindi_name": disease_info.get("hindi_name", ""),
            "scientific_name": disease_info.get("scientific_name", ""),
            "category": disease_info.get("category", ai_result.get("disease_cause", "")),
            "confidence": ai_result.get("confidence", 85),
            "severity": ai_result.get("severity", disease_info.get("severity_typical", "moderate")),
            "description": disease_info.get("description", ""),
            "description_hindi": disease_info.get("description_hindi", ""),
            "symptoms_observed": ai_result.get("symptoms_observed", disease_info.get("symptoms", [])[:3]),
            "all_symptoms": disease_info.get("symptoms", []),
            "is_healthy": ai_result.get("is_healthy", disease_key == "healthy"),
            "affected_area_percent": ai_result.get("affected_area_percent", 0),
            "spread_risk": ai_result.get("spread_risk", "unknown"),
            "immediate_action_needed": ai_result.get("immediate_action_needed", False),
        },
        "treatment": {
            "chemical": disease_info.get("treatments", []),
            "organic": disease_info.get("organic_treatments", []),
            "prevention": disease_info.get("prevention", []),
        },
        "metadata": {
            "analysis_engine": analysis_engine,
            "model_used": settings.bedrock_model_id if analysis_engine == "bedrock" else analysis_engine,
            "pipeline_latency_ms": int((time.time() - pipeline_start) * 1000),
            "image_preprocessed": img_meta.get("resized", False),
            "favorable_conditions": disease_info.get("favorable_conditions", ""),
            "ai_notes": ai_result.get("additional_notes", ""),
            # preserve raw engine meta for debugging
            "engine_meta": ai_result.get("_meta", {}),
        },
    }

    # ── Stage 5: Translation ───────────────────────────────
    if language != "en" and language in ["hi", "ta", "te", "kn", "mr", "bn", "gu", "pa"]:
        try:
            if language == "hi":
                # Hindi descriptions are pre-stored in the DB
                response["analysis"]["description_translated"] = disease_info.get(
                    "description_hindi", response["analysis"]["description"]
                )
            else:
                # Use Amazon Translate for other languages
                translated = await translate_text(
                    disease_info.get("description", ""), language
                )
                response["analysis"]["description_translated"] = translated

                # Also translate treatment names for non-Hindi
                for i, t in enumerate(response["treatment"]["chemical"]):
                    try:
                        translated_method = await translate_text(t.get("method", ""), language)
                        response["treatment"]["chemical"][i]["method_translated"] = translated_method
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"Translation stage failed: {e}")

    # ── Stage 6: S3 Archival (non-blocking) ────────────────
    try:
        s3_key = await archive_scan_to_s3(processed_b64, response, phone_number)
        if s3_key:
            response["metadata"]["s3_key"] = s3_key
    except Exception:
        pass  # Archival failure should never block response

    logger.info(
        f"Pipeline complete: engine={analysis_engine}, "
        f"crop={response['analysis']['crop']}, "
        f"disease={response['analysis']['disease_key']}, "
        f"confidence={response['analysis']['confidence']}%, "
        f"latency={response['metadata']['pipeline_latency_ms']}ms"
    )

    return response


# ============================================================
# UTILITY / PUBLIC API
# ============================================================

def get_disease_by_key(disease_key: str) -> Optional[dict]:
    """Get disease info by key from database."""
    return DISEASE_DATABASE.get(disease_key)


def get_all_diseases() -> dict:
    """Get all diseases in database."""
    return DISEASE_DATABASE


def get_supported_crops() -> list:
    """Get list of supported crops."""
    return list(CROP_DISEASES.keys())


def get_pipeline_status() -> dict:
    """Return the health/readiness of each pipeline stage."""
    bedrock_ok = get_bedrock_client() is not None
    rekognition_ok = get_rekognition_client() is not None
    translate_ok = get_translate_client() is not None
    s3_ok = get_s3_client() is not None
    polly_ok = _get_aws_client("polly") is not None
    dynamodb_ok = _get_aws_client("dynamodb") is not None
    cloudwatch_ok = _get_aws_client("cloudwatch") is not None

    return {
        "bedrock": {"available": bedrock_ok, "model": settings.bedrock_model_id},
        "rekognition": {"available": rekognition_ok},
        "translate": {"available": translate_ok},
        "s3": {"available": s3_ok, "bucket": settings.s3_bucket_name},
        "polly": {"available": polly_ok, "voice": "Kajal (hi-IN, neural)"},
        "dynamodb": {"available": dynamodb_ok, "tables": [settings.dynamodb_table_scans, settings.dynamodb_table_users]},
        "cloudwatch": {"available": cloudwatch_ok, "namespace": "FasalDrishti"},
        "disease_db": {"available": True, "diseases": len(DISEASE_DATABASE), "crops": len(CROP_DISEASES)},
        "active_engine": "bedrock" if bedrock_ok else ("rekognition" if rekognition_ok else "fallback_demo"),
    }
