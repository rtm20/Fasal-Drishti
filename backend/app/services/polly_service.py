"""
FasalDrishti - Amazon Polly Voice Service
==========================================
Generates voice (audio) responses for WhatsApp farmers who
may not be able to read text. Especially valuable for:
  - Illiterate or semi-literate farmers
  - Hands-free listening while working in the field
  - Reinforcing text advice with audio

AWS Service: Amazon Polly
Why: Neural text-to-speech that supports Indian languages (Hindi, Tamil,
     Telugu, etc.) with natural-sounding voices. Converts treatment advice
     into MP3 audio that can be sent back via WhatsApp as a voice note.

How it works:
  1. After AI analysis produces text advice → format it for speech
  2. Call Polly synthesize_speech() with appropriate voice + language
  3. Get MP3 audio bytes back
  4. Upload to S3 with a pre-signed URL (so WhatsApp can fetch it)
  5. Send the audio URL back to the farmer via WhatsApp

Supported voices for Indian languages:
  - Hindi:   Aditi (standard), Kajal (neural)
  - English: Aditi, Kajal
  - Tamil:   (via English voice with Tamil text — Polly auto-detects)
"""

import base64
import logging
import time
from typing import Optional

from app.config import get_settings

logger = logging.getLogger("fasaldrishti.polly")
settings = get_settings()

_polly_client = None


def _get_polly_client():
    """Get or create a cached boto3 Polly client."""
    global _polly_client
    if _polly_client is None:
        try:
            import boto3
            kwargs = {"region_name": settings.aws_region}
            if settings.aws_access_key_id:
                kwargs["aws_access_key_id"] = settings.aws_access_key_id
            if settings.aws_secret_access_key:
                kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
            _polly_client = boto3.client("polly", **kwargs)
        except Exception as e:
            logger.warning(f"Could not create Polly client: {e}")
    return _polly_client


# ============================================================
# VOICE ID MAPPING BY LANGUAGE
# ============================================================

# Amazon Polly voice IDs for Indian languages
# See: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html
POLLY_VOICES = {
    "hi": {"VoiceId": "Kajal", "LanguageCode": "hi-IN", "Engine": "neural"},
    "en": {"VoiceId": "Kajal", "LanguageCode": "en-IN", "Engine": "neural"},
    "ta": {"VoiceId": "Kajal", "LanguageCode": "en-IN", "Engine": "neural"},  # Tamil → English voice
    "te": {"VoiceId": "Kajal", "LanguageCode": "en-IN", "Engine": "neural"},  # Telugu → English voice  
    "kn": {"VoiceId": "Kajal", "LanguageCode": "en-IN", "Engine": "neural"},  # Kannada → English voice
    "mr": {"VoiceId": "Kajal", "LanguageCode": "hi-IN", "Engine": "neural"},  # Marathi → Hindi voice
    "bn": {"VoiceId": "Kajal", "LanguageCode": "en-IN", "Engine": "neural"},  # Bengali → English voice
    "gu": {"VoiceId": "Kajal", "LanguageCode": "hi-IN", "Engine": "neural"},  # Gujarati → Hindi voice
    "pa": {"VoiceId": "Kajal", "LanguageCode": "hi-IN", "Engine": "neural"},  # Punjabi → Hindi voice
}

# Fallback voice if language not in mapping
DEFAULT_VOICE = {"VoiceId": "Kajal", "LanguageCode": "en-IN", "Engine": "neural"}


# ============================================================
# TEXT-TO-SPEECH SYNTHESIS
# ============================================================

def format_diagnosis_for_speech(analysis_result: dict, language: str = "hi") -> str:
    """
    Convert the structured analysis result into natural speech text.
    Formats it as a friendly, easy-to-understand advisory.
    """
    analysis = analysis_result.get("analysis", {})
    treatment = analysis_result.get("treatment", {})
    
    crop = analysis.get("crop", "crop")
    disease_name = analysis.get("disease_name", "Unknown")
    hindi_name = analysis.get("hindi_name", "")
    severity = analysis.get("severity", "moderate")
    confidence = analysis.get("confidence", 0)
    is_healthy = analysis.get("is_healthy", False)
    description = analysis.get("description_translated", analysis.get("description", ""))
    
    if language == "hi":
        # Hindi speech
        if is_healthy:
            speech = (
                f"नमस्ते किसान भाई। फसल दृष्टि का विश्लेषण पूरा हुआ। "
                f"आपकी {crop} की फसल स्वस्थ है। "
                f"कोई बीमारी नहीं पाई गई। फसल अच्छी दिख रही है। "
                f"नियमित देखभाल जारी रखें।"
            )
        else:
            speech = (
                f"नमस्ते किसान भाई। फसल दृष्टि का विश्लेषण पूरा हुआ। "
                f"आपकी {crop} की फसल में {hindi_name or disease_name} बीमारी पाई गई है। "
                f"गंभीरता का स्तर {severity} है। "
            )
            # Add first chemical treatment
            chemicals = treatment.get("chemical", [])
            if chemicals:
                first = chemicals[0]
                speech += (
                    f"इलाज: {first.get('name', '')} का प्रयोग करें। "
                    f"मात्रा: {first.get('dosage', '')}। "
                )
            # Add first organic treatment
            organics = treatment.get("organic", [])
            if organics:
                speech += f"जैविक उपचार: {organics[0]}। "
            
            speech += "कृपया जल्द से जल्द उपचार शुरू करें।"
    else:
        # English speech (default for all other languages)
        if is_healthy:
            speech = (
                f"Hello farmer. FasalDrishti analysis is complete. "
                f"Your {crop} crop is healthy. "
                f"No disease was detected. The crop looks good. "
                f"Continue regular care."
            )
        else:
            speech = (
                f"Hello farmer. FasalDrishti analysis is complete. "
                f"Your {crop} crop has been diagnosed with {disease_name}. "
                f"Severity level is {severity}. "
                f"Confidence of detection is {confidence} percent. "
            )
            chemicals = treatment.get("chemical", [])
            if chemicals:
                first = chemicals[0]
                speech += (
                    f"Recommended treatment: {first.get('name', '')}. "
                    f"Dosage: {first.get('dosage', '')}. "
                )
            organics = treatment.get("organic", [])
            if organics:
                speech += f"Organic alternative: {organics[0]}. "
            
            speech += "Please start treatment as soon as possible."
    
    return speech


async def synthesize_speech(
    text: str,
    language: str = "hi",
    output_format: str = "mp3",
) -> Optional[bytes]:
    """
    Convert text to speech audio using Amazon Polly.
    
    Args:
        text: The text to speak (max 3000 chars for neural voices)
        language: Language code (hi, en, ta, te, etc.)
        output_format: Audio format (mp3, ogg_vorbis, pcm)
    
    Returns:
        Audio bytes (MP3) or None on failure
    """
    try:
        client = _get_polly_client()
        if not client:
            logger.warning("Polly client unavailable")
            return None

        # Get voice config for language
        voice_config = POLLY_VOICES.get(language, DEFAULT_VOICE)
        
        # Truncate text if too long (Polly neural limit: 3000 chars)
        if len(text) > 3000:
            text = text[:2950] + "..."

        start_time = time.time()
        
        response = client.synthesize_speech(
            Text=text,
            OutputFormat=output_format,
            VoiceId=voice_config["VoiceId"],
            LanguageCode=voice_config["LanguageCode"],
            Engine=voice_config["Engine"],
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Read the audio stream
        audio_bytes = response["AudioStream"].read()
        
        logger.info(
            f"Polly synthesis: {len(text)} chars → {len(audio_bytes)} bytes, "
            f"voice={voice_config['VoiceId']}, lang={voice_config['LanguageCode']}, "
            f"latency={latency_ms}ms"
        )
        
        return audio_bytes

    except Exception as e:
        logger.warning(f"Polly synthesis failed: {e}")
        return None


async def generate_voice_advisory(
    analysis_result: dict,
    language: str = "hi",
) -> Optional[bytes]:
    """
    High-level function: takes analysis result, produces audio advisory.
    This is the main entry point called from the WhatsApp handler.
    
    Flow: analysis_result → format text → Polly TTS → MP3 bytes
    """
    try:
        # Format the diagnosis into natural speech text
        speech_text = format_diagnosis_for_speech(analysis_result, language)
        
        # Synthesize speech
        audio_bytes = await synthesize_speech(speech_text, language)
        
        if audio_bytes:
            logger.info(
                f"Voice advisory generated: {len(audio_bytes)} bytes for language={language}"
            )
        
        return audio_bytes
        
    except Exception as e:
        logger.warning(f"Voice advisory generation failed: {e}")
        return None


async def upload_voice_to_s3(audio_bytes: bytes, scan_id: str, language: str = "hi") -> Optional[str]:
    """
    Upload the voice MP3 to S3 and return a public URL.
    Sets the object to public-read so WhatsApp users can access directly
    without presigned URL signature issues.
    """
    try:
        import boto3
        
        s3_kwargs = {"region_name": settings.aws_region}
        if settings.aws_access_key_id:
            s3_kwargs["aws_access_key_id"] = settings.aws_access_key_id
        if settings.aws_secret_access_key:
            s3_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
        
        client = boto3.client("s3", **s3_kwargs)
        
        if not settings.s3_bucket_name:
            return None

        from datetime import datetime
        date_prefix = datetime.utcnow().strftime("%Y/%m/%d")
        key = f"voice/{date_prefix}/{scan_id}.mp3"

        # First, ensure bucket allows public access for voice files
        # Set the bucket policy to allow public read on voice/* if not already set
        try:
            import json as _json
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadVoice",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{settings.s3_bucket_name}/voice/*"
                    }
                ]
            }
            # Try to get existing policy and merge, otherwise set new
            try:
                existing = _json.loads(client.get_bucket_policy(Bucket=settings.s3_bucket_name)["Policy"])
                # Check if our statement already exists
                sids = [s.get("Sid") for s in existing.get("Statement", [])]
                if "PublicReadVoice" not in sids:
                    existing["Statement"].append(policy["Statement"][0])
                    client.put_bucket_policy(Bucket=settings.s3_bucket_name, Policy=_json.dumps(existing))
                    logger.info("Added PublicReadVoice policy to S3 bucket")
            except client.exceptions.from_code("NoSuchBucketPolicy"):
                client.put_bucket_policy(Bucket=settings.s3_bucket_name, Policy=_json.dumps(policy))
                logger.info("Set S3 bucket policy for public voice access")
            except Exception:
                # Policy might already exist or we lack permissions — try without
                pass
        except Exception:
            pass

        # Upload the file
        client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=key,
            Body=audio_bytes,
            ContentType="audio/mpeg",
            CacheControl="max-age=86400",
        )
        
        # Return direct public URL (no signature needed)
        public_url = f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{key}"
        
        logger.info(f"Voice uploaded to S3: {key}")
        return public_url
        
    except Exception as e:
        logger.warning(f"S3 voice upload failed: {e}")
        return None


# ============================================================
# STATUS
# ============================================================

def get_polly_status() -> dict:
    """Check Polly service availability."""
    client = _get_polly_client()
    if not client:
        return {"available": False, "error": "Client not created"}
    try:
        # Quick check: describe a voice
        response = client.describe_voices(
            LanguageCode="hi-IN",
            Engine="neural",
        )
        voices = [v["Id"] for v in response.get("Voices", [])]
        return {
            "available": True,
            "hindi_voices": voices,
            "supported_languages": list(POLLY_VOICES.keys()),
        }
    except Exception as e:
        return {"available": False, "error": str(e)}
