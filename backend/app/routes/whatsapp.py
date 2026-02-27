"""
FasalDrishti - WhatsApp Webhook Handler
Supports BOTH Meta Cloud API and Twilio WhatsApp Sandbox.
Provider is selected via WHATSAPP_PROVIDER env var ("meta" or "twilio").
"""

import base64
import logging
import json
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Query, Response
from fastapi.responses import PlainTextResponse, JSONResponse

from app.services.ai_service import analyze_crop_image, get_pipeline_status
from app.config import get_settings

logger = logging.getLogger("fasaldrishti.whatsapp")
settings = get_settings()

router = APIRouter()


# ============================================================
# USER SESSION STORE & LANGUAGE CONFIG
# ============================================================

# In-memory store: phone_number -> {"language": "hi", "language_set": True}
user_sessions: dict[str, dict] = {}

# Supported languages with display info
SUPPORTED_LANGUAGES = {
    "1": {"code": "en", "name": "English", "native": "English", "flag": "🇬🇧"},
    "2": {"code": "hi", "name": "Hindi", "native": "हिंदी", "flag": "🇮🇳"},
    "3": {"code": "ta", "name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳"},
    "4": {"code": "te", "name": "Telugu", "native": "తెలుగు", "flag": "🇮🇳"},
    "5": {"code": "kn", "name": "Kannada", "native": "ಕನ್ನಡ", "flag": "🇮🇳"},
    "6": {"code": "bn", "name": "Bengali", "native": "বাংলা", "flag": "🇮🇳"},
    "7": {"code": "mr", "name": "Marathi", "native": "मराठी", "flag": "🇮🇳"},
    "8": {"code": "pa", "name": "Punjabi", "native": "ਪੰਜਾਬੀ", "flag": "🇮🇳"},
    "9": {"code": "gu", "name": "Gujarati", "native": "ગુજરાતી", "flag": "🇮🇳"},
}

# Quick-lookup: language code -> language name mapping
LANG_CODE_TO_NAME = {v["code"]: v["native"] for v in SUPPORTED_LANGUAGES.values()}


def get_user_language(phone: str) -> str:
    """Get user's chosen language code. Returns empty string if not set."""
    session = user_sessions.get(phone, {})
    if session.get("language_set"):
        return session.get("language", "")
    return ""


def set_user_language(phone: str, lang_code: str):
    """Set user's language preference."""
    user_sessions[phone] = {"language": lang_code, "language_set": True}
    logger.info(f"Language set for {phone}: {lang_code}")


def get_language_menu() -> str:
    """Return language selection menu shown to new users."""
    menu = """🌱 *Welcome to FasalDrishti!*
🌱 *FasalDrishti में आपका स्वागत है!*

🗣️ *Please choose your language / अपनी भाषा चुनें:*

"""
    for num, lang in SUPPORTED_LANGUAGES.items():
        menu += f"{num}. {lang['flag']} {lang['native']} ({lang['name']})\n"

    menu += """\n👉 *Reply with the number (1-9)*
👉 *नंबर भेजें (1-9)*

Example: Send *2* for हिंदी"""
    return menu


def get_language_set_confirmation(lang_code: str) -> str:
    """Confirmation message after language is set."""
    lang_name = LANG_CODE_TO_NAME.get(lang_code, lang_code)
    msgs = {
        "en": f"""✅ Language set to *English*

🌱 *Welcome to FasalDrishti — AI Crop Doctor!*

I help you identify crop diseases instantly.

📸 *How to use:*
1. Take a photo of the affected leaf/fruit
2. Send it here on WhatsApp
3. Get in 30 seconds:
   ✅ Disease identification
   💊 Treatment advice
   💰 Cost per acre

🌾 *Supported crops:* Tomato, Rice, Wheat, Cotton, Potato, Chili, Onion

📸 Send a crop photo now to get started!

🗣️ Type *lang* anytime to change language""",
        "hi": f"""✅ भाषा *हिंदी* सेट हो गई

🌱 *FasalDrishti — AI फसल डॉक्टर में आपका स्वागत है!*

मैं आपकी फसल की बीमारी तुरंत पहचानने में मदद करता हूं।

📸 *कैसे इस्तेमाल करें:*
1. प्रभावित पत्ती/फल की फोटो लें
2. यहां WhatsApp पर भेजें
3. 30 सेकंड में पाएं:
   ✅ बीमारी की पहचान
   💊 इलाज की सलाह
   💰 प्रति एकड़ खर्च

🌾 *समर्थित फसलें:* टमाटर, धान, गेहूं, कपास, आलू, मिर्च, प्याज

📸 अभी फसल की फोटो भेजें!

🗣️ भाषा बदलने के लिए *lang* टाइप करें""",
        "ta": f"""✅ மொழி *தமிழ்* அமைக்கப்பட்டது

🌱 *FasalDrishti — AI பயிர் மருத்துவர்!*

📸 பாதிக்கப்பட்ட இலை/பழத்தின் புகைப்படம் அனுப்புங்கள்.
30 வினாடிகளில் நோய் கண்டறிதல் + சிகிச்சை பெறுங்கள்!

🗣️ மொழி மாற்ற *lang* டைப் செய்யவும்""",
        "te": f"""✅ భాష *తెలుగు* సెట్ చేయబడింది

🌱 *FasalDrishti — AI పంట వైద్యుడు!*

📸 ప్రభావిత ఆకు/పండు ఫోటో పంపండి.
30 సెకన్లలో వ్యాధి నిర్ధారణ + చికిత్స పొందండి!

🗣️ భాష మార్చడానికి *lang* టైప్ చేయండి""",
        "kn": f"""✅ ಭಾಷೆ *ಕನ್ನಡ* ಹೊಂದಿಸಲಾಗಿದೆ

🌱 *FasalDrishti — AI ಬೆಳೆ ವೈದ್ಯ!*

📸 ಪೀಡಿತ ಎಲೆ/ಹಣ್ಣಿನ ಫೋಟೋ ಕಳುಹಿಸಿ.
30 ಸೆಕೆಂಡುಗಳಲ್ಲಿ ರೋಗ ಪತ್ತೆ + ಚಿಕಿತ್ಸೆ ಪಡೆಯಿರಿ!

🗣️ ಭಾಷೆ ಬದಲಿಸಲು *lang* ಟೈಪ್ ಮಾಡಿ""",
        "bn": f"""✅ ভাষা *বাংলা* সেট হয়েছে

🌱 *FasalDrishti — AI ফসল ডাক্তার!*

📸 আক্রান্ত পাতা/ফলের ছবি পাঠান।
30 সেকেন্ডে রোগ নির্ণয় + চিকিৎসা পান!

🗣️ ভাষা পরিবর্তন করতে *lang* টাইপ করুন""",
        "mr": f"""✅ भाषा *मराठी* सेट झाली

🌱 *FasalDrishti — AI पीक डॉक्टर!*

📸 प्रभावित पानाचा/फळाचा फोटो पाठवा.
30 सेकंदात रोग ओळख + उपचार मिळवा!

🗣️ भाषा बदलण्यासाठी *lang* टाइप करा""",
        "pa": f"""✅ ਭਾਸ਼ਾ *ਪੰਜਾਬੀ* ਸੈੱਟ ਹੋ ਗਈ

🌱 *FasalDrishti — AI ਫ਼ਸਲ ਡਾਕਟਰ!*

📸 ਪ੍ਰਭਾਵਿਤ ਪੱਤੇ/ਫਲ ਦੀ ਫੋਟੋ ਭੇਜੋ।
30 ਸਕਿੰਟਾਂ ਵਿੱਚ ਰੋਗ ਪਛਾਣ + ਇਲਾਜ ਪ੍ਰਾਪਤ ਕਰੋ!

🗣️ ਭਾਸ਼ਾ ਬਦਲਣ ਲਈ *lang* ਟਾਈਪ ਕਰੋ""",
        "gu": f"""✅ ભાષા *ગુજરાતી* સેટ થઈ

🌱 *FasalDrishti — AI પાક ડૉક્ટર!*

📸 અસરગ્રસ્ત પાન/ફળનો ફોટો મોકલો.
30 સેકન્ડમાં રોગ ઓળખ + સારવાર મેળવો!

🗣️ ભાષા બદલવા *lang* ટાઈપ કરો""",
    }
    return msgs.get(lang_code, msgs["en"])


# ============================================================
# MULTILINGUAL RESPONSE HELPERS
# ============================================================

# UI labels per language
I18N = {
    "en": {
        "result_header": "🌱 *FasalDrishti Analysis Result*",
        "disease": "🔍 *Disease:*",
        "severity": "*Severity:*",
        "confidence": "📊 *Confidence:*",
        "description": "📝 *Description:*",
        "treatment": "💊 *Recommended Treatment:*",
        "dosage": "Dosage",
        "method": "Method",
        "cost": "Cost",
        "per_acre": "/acre",
        "organic": "🌿 *Organic Options:*",
        "prevention": "🛡️ *Prevention:*",
        "footer": "📸 Send another photo or type 'help'",
        "welcome": """🌱 *Welcome to FasalDrishti — AI Crop Doctor!*

I help identify crop diseases instantly.

📸 *How to use:*
1. Take a photo of the affected leaf/fruit
2. Send it here
3. Get in 30 seconds:
   ✅ Disease identification
   💊 Treatment advice
   💰 Cost per acre

🌾 *Supported crops:* Tomato, Rice, Wheat, Cotton, Potato, Chili, Onion

📸 Send a crop photo now!
🗣️ Type *lang* to change language""",
        "help": """🆘 *Help*

📸 *Photo tips:*
• Take a close-up of the affected leaf
• Use good lighting
• Send both front and back of the leaf

🗣️ *Change language:* Type *lang*

❓ For issues, type 'support'""",
        "fallback": """🤖 I help identify crop diseases.

📸 Please send a *crop photo*.
Or type 'help' for assistance.
Or type *lang* to change language.""",
        "image_error": "🙏 Sorry, couldn't receive the photo. Please try again.",
        "system_error": "🙏 Something went wrong. Please try again.",
    },
    "hi": {
        "result_header": "🌱 *FasalDrishti विश्लेषण परिणाम*",
        "disease": "🔍 *बीमारी:*",
        "severity": "*गंभीरता:*",
        "confidence": "📊 *विश्वास स्तर:*",
        "description": "📝 *विवरण:*",
        "treatment": "💊 *अनुशंसित उपचार:*",
        "dosage": "खुराक",
        "method": "विधि",
        "cost": "खर्च",
        "per_acre": "/एकड़",
        "organic": "🌿 *जैविक विकल्प:*",
        "prevention": "🛡️ *बचाव के उपाय:*",
        "footer": "📸 एक और फोटो भेजें या 'help' टाइप करें",
        "welcome": """🌱 *FasalDrishti — AI फसल डॉक्टर में आपका स्वागत है!*

मैं आपकी फसल की बीमारी तुरंत पहचानने में मदद करता हूं।

📸 *कैसे इस्तेमाल करें:*
1. प्रभावित पत्ती/फल की फोटो लें
2. यहां भेजें
3. 30 सेकंड में पाएं:
   ✅ बीमारी की पहचान
   💊 इलाज की सलाह
   💰 प्रति एकड़ खर्च

🌾 *समर्थित फसलें:* टमाटर, धान, गेहूं, कपास, आलू, मिर्च, प्याज

📸 अभी फसल की फोटो भेजें!
🗣️ भाषा बदलने के लिए *lang* टाइप करें""",
        "help": """🆘 *सहायता*

📸 *फोटो भेजने के टिप्स:*
• प्रभावित पत्ती को करीब से फोटो लें
• अच्छी रोशनी में फोटो लें
• पत्ती का आगे और पीछे दोनों तरफ भेजें

🗣️ *भाषा बदलें:* *lang* टाइप करें

❓ समस्या हो तो 'support' टाइप करें""",
        "fallback": """🤖 मैं आपकी फसल की बीमारी पहचानने में मदद करता हूं।

📸 कृपया अपनी *फसल की फोटो* भेजें।
या 'help' टाइप करें मदद के लिए।
या भाषा बदलने के लिए *lang* टाइप करें।""",
        "image_error": "🙏 माफ कीजिए, फोटो प्राप्त नहीं हो सकी। कृपया फिर से भेजें।",
        "system_error": "🙏 कुछ गड़बड़ हो गई। कृपया दोबारा कोशिश करें।",
    },
    "ta": {
        "result_header": "🌱 *FasalDrishti பகுப்பாய்வு முடிவு*",
        "disease": "🔍 *நோய்:*",
        "severity": "*தீவிரம்:*",
        "confidence": "📊 *நம்பிக்கை:*",
        "description": "📝 *விளக்கம்:*",
        "treatment": "💊 *பரிந்துரைக்கப்பட்ட சிகிச்சை:*",
        "dosage": "அளவு",
        "method": "முறை",
        "cost": "செலவு",
        "per_acre": "/ஏக்கர்",
        "organic": "🌿 *இயற்கை விருப்பங்கள்:*",
        "prevention": "🛡️ *தடுப்பு:*",
        "footer": "📸 மற்றொரு புகைப்படம் அனுப்பவும் அல்லது 'help' டைப் செய்யவும்",
        "welcome": "🌱 *FasalDrishti — AI பயிர் மருத்துவர்!*\n\n📸 பாதிக்கப்பட்ட இலை/பழத்தின் புகைப்படம் அனுப்புங்கள்.\n30 வினாடிகளில் நோய் கண்டறிதல் + சிகிச்சை!\n\n🗣️ மொழி மாற்ற *lang* டைப் செய்யவும்",
        "help": "🆘 *உதவி*\n\n📸 புகைப்படம் அனுப்பவும்\n🗣️ மொழி மாற்ற *lang* டைப் செய்யவும்",
        "fallback": "📸 பயிர் புகைப்படம் அனுப்பவும் அல்லது 'help' டைப் செய்யவும்\n🗣️ மொழி மாற்ற *lang*",
        "image_error": "🙏 புகைப்படம் பெற இயலவில்லை. மீண்டும் முயற்சிக்கவும்.",
        "system_error": "🙏 ஏதோ தவறு நடந்தது. மீண்டும் முயற்சிக்கவும்.",
    },
    "te": {
        "result_header": "🌱 *FasalDrishti విశ్లేషణ ఫలితం*",
        "disease": "🔍 *వ్యాధి:*",
        "severity": "*తీవ్రత:*",
        "confidence": "📊 *నమ్మకం:*",
        "description": "📝 *వివరణ:*",
        "treatment": "💊 *సిఫార్సు చేసిన చికిత్స:*",
        "dosage": "మోతాదు",
        "method": "పద్ధతి",
        "cost": "ఖర్చు",
        "per_acre": "/ఎకరం",
        "organic": "🌿 *సేంద్రీయ ఎంపికలు:*",
        "prevention": "🛡️ *నివారణ:*",
        "footer": "📸 మరో ఫోటో పంపండి లేదా 'help' టైప్ చేయండి",
        "welcome": "🌱 *FasalDrishti — AI పంట వైద్యుడు!*\n\n📸 ప్రభావిత ఆకు/పండు ఫోటో పంపండి.\n30 సెకన్లలో వ్యాధి నిర్ధారణ + చికిత్స!\n\n🗣️ భాష మార్చడానికి *lang* టైప్ చేయండి",
        "help": "🆘 *సహాయం*\n\n📸 ఫోటో పంపండి\n🗣️ భాష మార్చడానికి *lang* టైప్ చేయండి",
        "fallback": "📸 పంట ఫోటో పంపండి లేదా 'help' టైప్ చేయండి\n🗣️ భాష మార్చడానికి *lang*",
        "image_error": "🙏 ఫోటో అందలేదు. మళ్ళీ ప్రయత్నించండి.",
        "system_error": "🙏 ఏదో తప్పు జరిగింది. మళ్ళీ ప్రయత్నించండి.",
    },
}

# For languages without full I18N, fall back to English
def get_i18n(lang: str) -> dict:
    """Get i18n strings for a language, falling back to English."""
    return I18N.get(lang, I18N["en"])


def format_whatsapp_response(result: dict, lang: str = "hi") -> str:
    """Format analysis result as a multilingual WhatsApp message."""
    analysis = result["analysis"]
    treatment = result["treatment"]
    t = get_i18n(lang)

    severity_emoji = {
        "none": "🟢",
        "mild": "🟡",
        "moderate": "🟠",
        "severe": "🔴",
    }
    emoji = severity_emoji.get(analysis["severity"], "⚪")

    # Use translated description if available, else Hindi, else English
    description = (
        analysis.get("description_translated")
        or analysis.get("description_hindi")
        or analysis.get("description", "")
    )
    if lang == "en":
        description = analysis.get("description", "")
    elif lang == "hi":
        description = analysis.get("description_hindi", analysis.get("description", ""))

    # Disease name: for Hindi show hindi_name, for English show disease_name, others show both
    if lang == "hi":
        disease_display = f"{analysis.get('hindi_name', analysis['disease_name'])}"
        disease_sub = f"   _{analysis['disease_name']}_"
    elif lang == "en":
        disease_display = f"{analysis['disease_name']}"
        disease_sub = f"   _{analysis.get('hindi_name', '')}_" if analysis.get('hindi_name') else ""
    else:
        disease_display = f"{analysis['disease_name']}"
        disease_sub = f"   _{analysis.get('hindi_name', '')}_" if analysis.get('hindi_name') else ""

    msg = f"""{t['result_header']}

{t['disease']} {disease_display}
{disease_sub}

{emoji} {t['severity']} {analysis['severity'].upper()}
{t['confidence']} {analysis['confidence']}%

{t['description']}
{description}

{t['treatment']}"""

    for i, tr in enumerate(treatment.get("chemical", [])[:2], 1):
        msg += f"""
{i}. *{tr['name']}*
   └ {t['dosage']}: {tr['dosage']}
   └ {t['method']}: {tr['method']}
   └ {t['cost']}: ₹{tr['cost_per_acre']}{t['per_acre']}"""

    msg += f"\n\n{t['organic']}"
    for item in treatment.get("organic", [])[:2]:
        msg += f"\n• {item}"

    msg += f"\n\n{t['prevention']}"
    for p in treatment.get("prevention", [])[:3]:
        msg += f"\n• {p}"

    msg += f"\n\n---\n{t['footer']}"
    return msg


def get_text_response(text: str, lang: str = "hi") -> str:
    """Generate response for text messages in the user's language."""
    text_lower = text.lower().strip()
    t = get_i18n(lang)

    if any(w in text_lower for w in ["hi", "hello", "namaste", "नमस्ते", "हेलो", "hola"]):
        return t["welcome"]
    elif any(w in text_lower for w in ["help", "मदद", "सहायता", "உதவி", "సహాయం"]):
        return t["help"]
    else:
        return t["fallback"]


def _escape_xml(text: str) -> str:
    """Escape special XML characters for TwiML."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


# ============================================================
# WEBHOOK ENDPOINTS
# ============================================================

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """
    Webhook verification (works for both Meta and custom).
    GET /api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        logger.info("WhatsApp webhook verified successfully")
        return PlainTextResponse(content=hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def handle_webhook(request: Request):
    """
    Handle incoming WhatsApp messages.
    Auto-detects Meta vs Twilio from content-type header.
    - Meta sends application/json
    - Twilio sends application/x-www-form-urlencoded
    """
    content_type = request.headers.get("content-type", "")

    if "application/x-www-form-urlencoded" in content_type:
        return await _handle_twilio_webhook(request)
    return await _handle_meta_webhook(request)


@router.post("/twilio")
async def handle_twilio_shortcut(request: Request):
    """Alias for /webhook — Twilio-specific endpoint."""
    return await _handle_twilio_webhook(request)


# ============================================================
# META CLOUD API HANDLER
# ============================================================

async def _handle_meta_webhook(request: Request):
    """Process messages from Meta Cloud API."""
    try:
        body = await request.json()
        logger.info(f"Meta webhook received: {json.dumps(body)[:500]}")

        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return JSONResponse(content={"status": "no messages"})

        message = messages[0]
        from_number = message.get("from", "")
        msg_type = message.get("type", "")

        # --- Language selection flow ---
        user_lang = get_user_language(from_number)

        if not user_lang:
            # Check if user is selecting a language
            if msg_type == "text":
                text = message.get("text", {}).get("body", "").strip()
                if text in SUPPORTED_LANGUAGES:
                    lang_code = SUPPORTED_LANGUAGES[text]["code"]
                    set_user_language(from_number, lang_code)
                    await send_meta_message(from_number, get_language_set_confirmation(lang_code))
                    return JSONResponse(content={"status": "language_set"})
            # New user or invalid selection → show language menu
            await send_meta_message(from_number, get_language_menu())
            return JSONResponse(content={"status": "language_prompt"})

        # --- Language change command ---
        if msg_type == "text":
            text = message.get("text", {}).get("body", "").strip().lower()
            if text in ["lang", "language", "भाषा", "bhasha"]:
                # Reset language so they get the menu again
                user_sessions.pop(from_number, None)
                await send_meta_message(from_number, get_language_menu())
                return JSONResponse(content={"status": "language_menu"})
            # Check if user sent a number for language change
            if text in SUPPORTED_LANGUAGES:
                lang_code = SUPPORTED_LANGUAGES[text]["code"]
                set_user_language(from_number, lang_code)
                await send_meta_message(from_number, get_language_set_confirmation(lang_code))
                return JSONResponse(content={"status": "language_changed"})

        t = get_i18n(user_lang)

        if msg_type == "image":
            image_id = message.get("image", {}).get("id", "")
            image_base64 = await download_meta_media(image_id)

            if image_base64:
                result = await analyze_crop_image(image_base64, "image/jpeg", user_lang, from_number)
                response_text = format_whatsapp_response(result, user_lang)
                await send_meta_message(from_number, response_text)
            else:
                await send_meta_message(from_number, t["image_error"])

        elif msg_type == "text":
            text = message.get("text", {}).get("body", "")
            response = get_text_response(text, user_lang)
            await send_meta_message(from_number, response)

        return JSONResponse(content={"status": "processed"})

    except Exception as e:
        logger.error(f"Meta webhook error: {e}", exc_info=True)
        return JSONResponse(content={"status": "error", "detail": str(e)})


async def download_meta_media(media_id: str) -> Optional[str]:
    """Download media from Meta Graph API."""
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {settings.whatsapp_api_token}"}
            url_resp = await client.get(
                f"https://graph.facebook.com/v18.0/{media_id}",
                headers=headers,
            )
            media_url = url_resp.json().get("url")
            if not media_url:
                return None

            media_resp = await client.get(media_url, headers=headers)
            return base64.b64encode(media_resp.content).decode("utf-8")
    except Exception as e:
        logger.error(f"Meta media download failed: {e}")
        return None


async def send_meta_message(to: str, text: str):
    """Send message via Meta Graph API."""
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {settings.whatsapp_api_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": text},
            }
            resp = await client.post(
                f"https://graph.facebook.com/v18.0/{settings.whatsapp_phone_number_id}/messages",
                headers=headers,
                json=payload,
            )
            logger.info(f"Meta message sent to {to}: {resp.status_code}")
            return resp.json()
    except Exception as e:
        logger.error(f"Meta send failed: {e}")
        return None


# ============================================================
# TWILIO WHATSAPP SANDBOX HANDLER
# ============================================================

async def _handle_twilio_webhook(request: Request):
    """
    Process incoming Twilio WhatsApp webhook (form-encoded).
    Twilio sends:
      - Body: text content
      - NumMedia: number of media attachments
      - MediaUrl0: URL of first media
      - MediaContentType0: MIME type
      - From: "whatsapp:+91XXXXXXXXXX"
      - To: "whatsapp:+14155238886"
    
    We respond with TwiML XML so Twilio sends the reply automatically.
    """
    try:
        form = await request.form()
        body_text = str(form.get("Body", ""))
        num_media = int(str(form.get("NumMedia", "0")))
        from_number = str(form.get("From", ""))
        to_number = str(form.get("To", ""))

        logger.info(
            f"Twilio webhook: from={from_number}, media={num_media}, text='{body_text[:50]}'"
        )

        # --- Language selection flow ---
        user_lang = get_user_language(from_number)
        text_stripped = body_text.strip()

        if not user_lang:
            # Check if user is selecting a language (sent a number 1-9)
            if text_stripped in SUPPORTED_LANGUAGES:
                lang_code = SUPPORTED_LANGUAGES[text_stripped]["code"]
                set_user_language(from_number, lang_code)
                response_text = get_language_set_confirmation(lang_code)
            else:
                # New user or invalid selection → show language menu
                response_text = get_language_menu()

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{_escape_xml(response_text)}</Message>
</Response>"""
            return Response(content=twiml, media_type="application/xml")

        # --- Language change command ---
        if num_media == 0 and text_stripped.lower() in ["lang", "language", "भाषा", "bhasha"]:
            user_sessions.pop(from_number, None)
            response_text = get_language_menu()
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{_escape_xml(response_text)}</Message>
</Response>"""
            return Response(content=twiml, media_type="application/xml")

        # Check if user sent a language number while already having a language set
        if num_media == 0 and text_stripped in SUPPORTED_LANGUAGES:
            lang_code = SUPPORTED_LANGUAGES[text_stripped]["code"]
            set_user_language(from_number, lang_code)
            response_text = get_language_set_confirmation(lang_code)
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{_escape_xml(response_text)}</Message>
</Response>"""
            return Response(content=twiml, media_type="application/xml")

        t = get_i18n(user_lang)
        response_text = ""

        if num_media > 0:
            # Image message — download and analyze
            media_url = str(form.get("MediaUrl0", ""))
            media_type = str(form.get("MediaContentType0", "image/jpeg"))

            logger.info(f"Downloading Twilio media: {media_url}")
            image_base64 = await download_twilio_media(media_url)

            if image_base64:
                result = await analyze_crop_image(image_base64, media_type, user_lang, from_number)
                response_text = format_whatsapp_response(result, user_lang)
            else:
                response_text = t["image_error"]
        else:
            # Text message
            response_text = get_text_response(body_text, user_lang)

        # Return TwiML response (Twilio's XML reply format)
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{_escape_xml(response_text)}</Message>
</Response>"""

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error(f"Twilio webhook error: {e}", exc_info=True)
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>🙏 Something went wrong / कुछ गड़बड़ हो गई। Please try again / कृपया दोबारा कोशिश करें।</Message>
</Response>"""
        return Response(content=twiml, media_type="application/xml")


async def download_twilio_media(media_url: str) -> Optional[str]:
    """
    Download media from Twilio.
    Twilio media URLs require basic auth with account SID / auth token.
    """
    try:
        import httpx

        auth = None
        if settings.twilio_account_sid and settings.twilio_auth_token:
            auth = (settings.twilio_account_sid, settings.twilio_auth_token)

        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(media_url, auth=auth)
            if resp.status_code == 200:
                image_base64 = base64.b64encode(resp.content).decode("utf-8")
                logger.info(f"Twilio media downloaded: {len(resp.content)} bytes")
                return image_base64
            else:
                logger.error(f"Twilio media download HTTP {resp.status_code}")
                return None
    except Exception as e:
        logger.error(f"Twilio media download failed: {e}")
        return None


async def send_twilio_message(to: str, body: str):
    """Send a message via Twilio REST API (for proactive messaging)."""
    try:
        import httpx

        url = (
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{settings.twilio_account_sid}/Messages.json"
        )
        auth = (settings.twilio_account_sid, settings.twilio_auth_token)
        payload = {
            "From": settings.twilio_whatsapp_number,
            "To": to,
            "Body": body,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, data=payload, auth=auth)
            logger.info(f"Twilio message sent to {to}: {resp.status_code}")
            return resp.json()
    except Exception as e:
        logger.error(f"Twilio send failed: {e}")
        return None


# ============================================================
# STATUS & SIMULATION ENDPOINTS
# ============================================================

@router.get("/status")
async def whatsapp_status():
    """Return WhatsApp integration status and configuration info."""
    # Re-fetch settings to avoid stale module-level reference
    from app.config import get_settings as _gs
    import os
    s = _gs()
    
    provider = s.whatsapp_provider

    if provider == "twilio":
        configured = bool(s.twilio_account_sid and s.twilio_auth_token)
    else:
        configured = bool(s.whatsapp_api_token and s.whatsapp_phone_number_id)

    return {
        "status": "configured" if configured else "demo_mode",
        "provider": provider,
        "webhook_url": (
            f"{s.public_url}/api/whatsapp/webhook"
            if s.public_url
            else "/api/whatsapp/webhook"
        ),
        "public_url": s.public_url or "not_set",
        "verify_token_set": bool(s.whatsapp_verify_token),
        "provider_configured": configured,
        "twilio": {
            "account_sid_set": bool(s.twilio_account_sid),
            "auth_token_set": bool(s.twilio_auth_token),
            "whatsapp_number": s.twilio_whatsapp_number or "not_set",
        }
        if provider == "twilio"
        else None,
        "meta": {
            "api_token_set": bool(s.whatsapp_api_token),
            "phone_number_id_set": bool(s.whatsapp_phone_number_id),
        }
        if provider == "meta"
        else None,
        "supported_message_types": ["image", "text"],
        "default_language": "user_selected",
        "supported_languages": [f"{v['native']} ({v['name']})" for v in SUPPORTED_LANGUAGES.values()],
        "active_sessions": len(user_sessions),
        "features": [
            "Image-based crop disease detection",
            "Multilingual support (9 Indian languages)",
            "Language selection on first message",
            "Welcome & help text responses",
            "Media download & analysis",
            "Structured treatment recommendations",
            f"Provider: {provider.upper()}",
        ],
    }


@router.post("/simulate")
async def simulate_whatsapp(request: Request):
    """
    Simulate a WhatsApp conversation for demo/testing.
    Accepts JSON: { "type": "text"|"image", "text": "...", "image_base64": "..." }
    """
    try:
        body = await request.json()
        msg_type = body.get("type", "text")

        lang = body.get("language", "hi")

        if msg_type == "text":
            text = body.get("text", "")
            response = get_text_response(text, lang)
            return {"status": "ok", "response": response}

        elif msg_type == "image":
            image_base64 = body.get("image_base64", "")
            if image_base64:
                result = await analyze_crop_image(image_base64, "image/jpeg", lang, "simulate")
                response = format_whatsapp_response(result, lang)
                return {"status": "ok", "response": response, "analysis": result}
            return {"status": "error", "detail": "No image_base64 provided"}

        t = get_i18n(lang)
        return {"status": "ok", "response": t["fallback"]}

    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.post("/test")
async def test_whatsapp_message(request: Request):
    """
    Send a test message via the configured provider.
    Accepts JSON: { "to": "whatsapp:+91XXXXXXXXXX", "message": "..." }
    """
    try:
        body = await request.json()
        to = body.get("to", "")
        message = body.get("message", "🌱 FasalDrishti test — connection successful!")

        if not to:
            return {"status": "error", "detail": "Missing 'to' phone number"}

        provider = settings.whatsapp_provider

        if provider == "twilio":
            if not to.startswith("whatsapp:"):
                to = f"whatsapp:{to}"
            result = await send_twilio_message(to, message)
        else:
            to_clean = to.replace("whatsapp:", "").replace("+", "")
            result = await send_meta_message(to_clean, message)

        return {"status": "ok", "provider": provider, "result": result}

    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.get("/connect")
async def whatsapp_connect_info():
    """
    Return WhatsApp connection details for users.
    Provides wa.me link, QR code URL, sandbox join instructions, etc.
    """
    from app.config import get_settings as _gs
    s = _gs()

    # Extract phone number digits for wa.me link
    wa_number = s.twilio_whatsapp_number.replace("whatsapp:", "").replace("+", "")
    pre_filled_msg = "namaste"
    wa_me_link = f"https://wa.me/{wa_number}?text={pre_filled_msg}"

    # QR code via free API (no dependency needed)
    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={wa_me_link}"

    is_sandbox = "14155238886" in wa_number  # Twilio sandbox number

    return {
        "whatsapp_number": f"+{wa_number}",
        "whatsapp_number_display": f"+{wa_number[:2]} {wa_number[2:5]} {wa_number[5:8]} {wa_number[8:]}",
        "wa_me_link": wa_me_link,
        "qr_code_url": qr_api_url,
        "is_sandbox": is_sandbox,
        "sandbox_instructions": {
            "step_1": f"Save +{wa_number} in your contacts as 'FasalDrishti'",
            "step_2": "Open WhatsApp and find 'FasalDrishti' in contacts",
            "step_3": "Send 'join <your-sandbox-code>' (shown in Twilio Console)",
            "step_4": "Once joined, send any crop photo to get AI analysis in Hindi!",
        } if is_sandbox else None,
        "production_instructions": {
            "step_1": f"Save +{wa_number} in your contacts or scan the QR code",
            "step_2": "Open the chat and send 'namaste' to start",
            "step_3": "Send any crop photo to get instant AI analysis",
            "step_4": "Receive disease diagnosis + treatment in Hindi!",
        },
        "supported_commands": [
            {"command": "namaste / hi / hello", "desc": "Get welcome message & instructions"},
            {"command": "help / मदद", "desc": "Get usage tips & language options"},
            {"command": "📸 Send photo", "desc": "Get AI disease diagnosis + treatment plan"},
        ],
        "features": [
            "No app download needed — works in WhatsApp",
            "Send crop photo → get diagnosis in 30 seconds",
            "Hindi responses with treatment + dosage + cost",
            "Supports 7 crops and 12+ diseases",
            "Organic + chemical treatment options",
        ],
    }


@router.get("/pipeline")
async def pipeline_status():
    """Return the health/readiness of each stage in the AI analysis pipeline."""
    return get_pipeline_status()

