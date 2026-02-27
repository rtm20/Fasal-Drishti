# WhatsApp Integration — Setup Guide

FasalDrishti's core feature: **Farmers send a crop photo via WhatsApp → AI analyzes → treatment response is sent back — all in Hindi.**

This guide covers two integration options. **Twilio is recommended** for rapid demo/hackathon setup.

---

## Option A: Twilio WhatsApp Sandbox (Recommended — 10 min setup)

### Step 1: Create a Twilio Account

1. Go to [https://www.twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Sign up for a free account (no credit card required for sandbox)
3. Note your **Account SID** and **Auth Token** from the [Console Dashboard](https://console.twilio.com)

### Step 2: Activate WhatsApp Sandbox

1. In Twilio Console, go to **Messaging → Try it out → Send a WhatsApp message**
   - Direct link: [https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. You'll see a sandbox number (usually `+1 415 523 8886`) and a **join code** (e.g., `join <word>-<word>`)
3. Send the join code from your WhatsApp to the sandbox number
4. You'll get a confirmation: "You're connected to the sandbox!"

### Step 3: Expose Local Server (ngrok)

Twilio needs a public URL to send webhooks to your local server.

```bash
# Install ngrok (if not installed)
# Download from https://ngrok.com/download or:
choco install ngrok   # Windows (Chocolatey)
# OR
winget install ngrok  # Windows (winget)

# Start ngrok tunnel
ngrok http 8000
```

Copy the **HTTPS URL** (e.g., `https://abc123.ngrok-free.app`).

### Step 4: Configure Twilio Webhook

1. Go to Twilio Console → **Messaging → Try it out → WhatsApp sandbox settings**
   - Direct link: [https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox](https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox)
2. Set **"WHEN A MESSAGE COMES IN"** to:
   ```
   https://YOUR-NGROK-URL.ngrok-free.app/api/whatsapp/webhook
   ```
3. HTTP Method: **POST**
4. Click **Save**

### Step 5: Update Environment Variables

Edit `backend/.env`:

```bash
WHATSAPP_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
PUBLIC_URL=https://YOUR-NGROK-URL.ngrok-free.app
```

### Step 6: Restart Backend & Test

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Test from WhatsApp:**
1. Open WhatsApp on your phone
2. Send "hi" to the sandbox number → Should receive welcome message in Hindi
3. Send a crop photo → Should receive disease analysis + treatment in Hindi

**Test from API:**
```bash
curl -X POST http://localhost:8000/api/whatsapp/test \
  -H "Content-Type: application/json" \
  -d '{"to": "whatsapp:+91XXXXXXXXXX", "message": "Test from FasalDrishti!"}'
```

---

## Option B: Meta Cloud API (Production)

### Step 1: Create Meta Developer Account

1. Go to [https://developers.facebook.com](https://developers.facebook.com)
2. Create a new app → Select "Business" type
3. Add **WhatsApp** product to your app

### Step 2: Get API Credentials

1. In WhatsApp → **Getting Started**, you'll find:
   - **Temporary access token** (valid 24hrs — enough for demo)
   - **Test phone number ID**
   - **Test phone number**
2. Add your phone as a test recipient under **To:** field

### Step 3: Configure Webhook

1. Go to WhatsApp → **Configuration** → **Webhook**
2. Set Callback URL: `https://YOUR-NGROK-URL.ngrok-free.app/api/whatsapp/webhook`
3. Verify Token: `fasaldrishti_verify_2026`
4. Subscribe to: **messages**

### Step 4: Update Environment Variables

```bash
WHATSAPP_PROVIDER=meta
WHATSAPP_API_TOKEN=your_meta_api_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=fasaldrishti_verify_2026
PUBLIC_URL=https://YOUR-NGROK-URL.ngrok-free.app
```

---

## How the Pipeline Works

```
Farmer's Phone                    FasalDrishti Server                 AWS
     │                                  │                              │
     │ 1. Send crop photo               │                              │
     │ ─────────────────────────►       │                              │
     │                                  │ 2. Twilio/Meta sends         │
     │                                  │    webhook to /api/whatsapp  │
     │                                  │    /webhook                  │
     │                                  │                              │
     │                                  │ 3. Download image            │
     │                                  │    from Twilio/Meta          │
     │                                  │                              │
     │                                  │ 4. Send to Bedrock ─────────►│
     │                                  │    Claude 3.5 Sonnet v2      │
     │                                  │                              │
     │                                  │ 5. Receive diagnosis ◄───────│
     │                                  │    + treatment plan          │
     │                                  │                              │
     │                                  │ 6. Format Hindi response     │
     │ 7. Receive diagnosis             │                              │
     │ ◄───────────────────────────────│                              │
     │    in Hindi with treatments      │                              │
```

## Troubleshooting

### "Unable to locate credentials" in logs
- AWS Bedrock credentials not set. The system falls back to demo mode with random disease detection.
- Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `.env` for real AI analysis.

### Twilio not receiving webhooks
- Check ngrok is running: `ngrok http 8000`
- Verify the webhook URL in Twilio console matches your ngrok URL
- Check ngrok dashboard: [http://localhost:4040](http://localhost:4040)

### "Not connected to sandbox"
- Send the join code again from WhatsApp to the sandbox number
- Sandbox connections expire after 72 hours of inactivity

### Image not being analyzed
- Check file size < 10MB
- Ensure ngrok tunnel is active (free tier tunnels expire)
- Check backend logs: `uvicorn` output in terminal

---

## Quick Start (Copy-Paste Commands)

```powershell
# Terminal 1 — Start ngrok
ngrok http 8000

# Terminal 2 — Start backend (after setting .env)
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3 — Start frontend
cd frontend
npm run dev
```

Then:
1. Copy ngrok HTTPS URL → Set in Twilio webhook settings + `PUBLIC_URL` in `.env`
2. Send "hi" from WhatsApp to sandbox number
3. Send a crop photo and receive AI diagnosis!
