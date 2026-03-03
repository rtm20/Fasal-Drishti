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
    "ml": {"VoiceId": "Kajal", "LanguageCode": "en-IN", "Engine": "neural"},  # Malayalam → English voice
    "or": {"VoiceId": "Kajal", "LanguageCode": "en-IN", "Engine": "neural"},  # Odia → English voice
}

# Fallback voice if language not in mapping
DEFAULT_VOICE = {"VoiceId": "Kajal", "LanguageCode": "en-IN", "Engine": "neural"}


# ============================================================
# TEXT-TO-SPEECH SYNTHESIS
# ============================================================

def format_diagnosis_for_speech(analysis_result: dict, language: str = "hi") -> str:
    """
    Convert the structured analysis result into a SHORT, warm, buddy-like
    voice advisory.  This is NOT a verbatim read-out of the text message —
    it is a concise spoken summary that sounds like a knowledgeable friend
    giving quick advice in the field.

    Design principles:
      • Keep it under ~30 seconds of speech (~120 words)
      • Conversational tone — like a fellow farmer or agronomist friend
      • Lead with crop identification
      • Healthy → quick cheer + encouragement (5-10 sec)
      • Diseased → name the problem, one key action, one organic tip (~25 sec)
      • Use SSML for natural pauses and prosody
    """
    analysis = analysis_result.get("analysis", {})
    treatment = analysis_result.get("treatment", {})

    crop = analysis.get("crop", "crop").capitalize()
    crop_hindi = analysis.get("crop_hindi", "")
    disease_name = analysis.get("disease_name", "Unknown")
    hindi_name = analysis.get("hindi_name", "")
    severity = analysis.get("severity", "moderate")
    is_healthy = analysis.get("is_healthy", False)

    # Hindi-belt languages
    hindi_belt = {"hi", "mr", "gu", "pa"}

    severity_hi = {"mild": "हल्की", "moderate": "मध्यम", "severe": "गंभीर", "none": "कोई नहीं"}
    severity_en = {"mild": "mild", "moderate": "moderate", "severe": "serious", "none": "none"}

    if language in hindi_belt:
        crop_display = crop_hindi if crop_hindi else crop

        if is_healthy:
            speech = (
                f'<speak>'
                f'<prosody rate="95%">'
                f'नमस्ते भाई! <break time="300ms"/>'
                f'ये तो {crop_display} की फसल है, और सुनो — '
                f'<emphasis level="strong">बिल्कुल स्वस्थ है!</emphasis> <break time="400ms"/>'
                f'कोई बीमारी नहीं है। बहुत बढ़िया काम कर रहे हो! <break time="200ms"/>'
                f'ऐसे ही देखभाल करते रहो। '
                f'</prosody>'
                f'</speak>'
            )
        else:
            sev_word = severity_hi.get(severity, severity)
            speech = (
                f'<speak>'
                f'<prosody rate="95%">'
                f'नमस्ते भाई! <break time="300ms"/>'
                f'ये {crop_display} की फसल है। <break time="200ms"/>'
                f'देखो, इसमें <emphasis level="strong">{hindi_name or disease_name}</emphasis> '
                f'की समस्या दिख रही है। <break time="200ms"/>'
                f'स्थिति {sev_word} है, तो थोड़ा ध्यान देना ज़रूरी है। <break time="400ms"/>'
            )
            # One key treatment — keep it short
            chemicals = treatment.get("chemical", [])
            if chemicals:
                first = chemicals[0]
                t_name = first.get("name_translated", first.get("name", ""))
                t_dosage = first.get("dosage_translated", first.get("dosage", ""))
                speech += (
                    f'सबसे पहले, <emphasis level="moderate">{t_name}</emphasis> '
                    f'लगाओ, {t_dosage}। <break time="300ms"/>'
                )
            # One organic tip
            organics = treatment.get("organic_translated", treatment.get("organic", []))
            if organics:
                speech += f'और हाँ, देसी उपाय — {organics[0]}। <break time="300ms"/>'

            speech += (
                f'जितनी जल्दी हो सके शुरू कर दो भाई। '
                f'बाक़ी पूरी जानकारी मैसेज में भेज दी है, वो पढ़ लेना। '
                f'</prosody>'
                f'</speak>'
            )
    else:
        # English speech (for en, ta, te, kn, bn, ml, or)
        if is_healthy:
            speech = (
                f'<speak>'
                f'<prosody rate="95%">'
                f'Hey there! <break time="300ms"/>'
                f'So I checked your {crop} crop, and guess what — '
                f'<emphasis level="strong">it looks perfectly healthy!</emphasis> <break time="400ms"/>'
                f'No disease at all. You are doing a great job! <break time="200ms"/>'
                f'Just keep doing what you are doing. '
                f'</prosody>'
                f'</speak>'
            )
        else:
            sev_word = severity_en.get(severity, severity)
            speech = (
                f'<speak>'
                f'<prosody rate="95%">'
                f'Hey! <break time="300ms"/>'
                f'So this is your {crop} crop. <break time="200ms"/>'
                f'I found <emphasis level="strong">{disease_name}</emphasis> here. <break time="200ms"/>'
                f'The condition looks {sev_word}, so let us act quickly. <break time="400ms"/>'
            )
            chemicals = treatment.get("chemical", [])
            if chemicals:
                first = chemicals[0]
                t_name = first.get("name_translated", first.get("name", ""))
                t_dosage = first.get("dosage_translated", first.get("dosage", ""))
                speech += (
                    f'First thing — apply <emphasis level="moderate">{t_name}</emphasis>, '
                    f'{t_dosage}. <break time="300ms"/>'
                )
            organics = treatment.get("organic_translated", treatment.get("organic", []))
            if organics:
                speech += f'For a natural option, try {organics[0]}. <break time="300ms"/>'

            speech += (
                f'Start as soon as you can. '
                f'I have sent you all the details in the text message, check that out too. '
                f'</prosody>'
                f'</speak>'
            )

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
        
        # Use SSML if the text contains <speak> tags (for natural prosody)
        text_type = "ssml" if text.strip().startswith("<speak>") else "text"
        
        response = client.synthesize_speech(
            Text=text,
            TextType=text_type,
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
