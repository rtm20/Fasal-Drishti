# FasalDrishti — AWS Setup Guide

> **Time required**: ~20 minutes  
> **Budget**: Fits within $100 AWS hackathon credits  
> **Region**: `ap-south-1` (Mumbai) — closest to Indian farmers  

---

## Overview: What We Need from AWS

| # | AWS Service | Purpose | Required? | Est. Cost |
|---|-------------|---------|-----------|-----------|
| 1 | **IAM** | Access credentials | ✅ Yes | Free |
| 2 | **Amazon Bedrock** | Claude 3.5 Sonnet v2 — AI crop disease vision | ✅ Yes | ~$0.003/image |
| 3 | **Amazon Translate** | Multilingual output (9 Indian languages) | ✅ Yes | ~$15/million chars |
| 4 | **Amazon Rekognition** | Fallback label detection | ⬜ Optional | ~$0.001/image |
| 5 | **Amazon S3** | Image archival + scan history | ⬜ Optional | ~$0.023/GB |

**Estimated total for hackathon demo**: < $5 (well within $100 credits)

---

## Step 1: Sign In to AWS Console

1. Go to: **https://console.aws.amazon.com/**
2. Sign in with the account where your hackathon credits are applied
3. In the top-right, set region to **Asia Pacific (Mumbai) `ap-south-1`**

---

## Step 2: Enable Amazon Bedrock Model Access

> This is the most critical step — Bedrock models must be explicitly enabled.

1. Go to: **[Amazon Bedrock Console](https://ap-south-1.console.aws.amazon.com/bedrock/home?region=ap-south-1)**
2. In the left sidebar, click **"Model access"**
3. Click **"Manage model access"** (orange button, top-right)
4. Find and CHECK these models:
   - ✅ **Anthropic → Claude 3.5 Sonnet v2** (`anthropic.claude-3-5-sonnet-20241022-v2:0`)
   - ✅ **Anthropic → Claude 3 Haiku** (optional, cheaper fallback)
5. Click **"Request model access"**
6. Wait 1-2 minutes for approval (usually instant for these models)

### 📝 Verify model access:
- Go back to "Model access" page
- Status should show **"Access granted"** ✅ next to Claude 3.5 Sonnet v2

> **If Claude 3.5 Sonnet v2 is not available in ap-south-1:**  
> Try region `us-east-1` (Virginia) instead.  
> Update `AWS_REGION=us-east-1` in `backend/.env`

---

## Step 3: Create IAM User & Get Credentials

1. Go to: **[IAM Console → Users](https://console.aws.amazon.com/iam/home#/users)**
2. Click **"Create user"**
3. User name: `fasaldrishti-hackathon`
4. Click **Next**
5. Select **"Attach policies directly"**
6. Search and CHECK these policies:
   - ✅ `AmazonBedrockFullAccess`
   - ✅ `TranslateFullAccess`
   - ✅ `AmazonRekognitionReadOnlyAccess`
   - ✅ `AmazonS3FullAccess`
7. Click **Next → Create user**

### Get Access Keys:
1. Click on the user `fasaldrishti-hackathon`
2. Go to **"Security credentials"** tab
3. Scroll to **"Access keys"** → Click **"Create access key"**
4. Select **"Application running outside AWS"** → Next → Create
5. **COPY BOTH VALUES NOW** (you won't see the secret again):

```
AWS_ACCESS_KEY_ID=AKIA................
AWS_SECRET_ACCESS_KEY=xxxx................
```

### 📝 Share these with me:
```
AWS_ACCESS_KEY_ID=<paste here>
AWS_SECRET_ACCESS_KEY=<paste here>
```

---

## Step 4: Create S3 Bucket (Optional — for image archival)

1. Go to: **[S3 Console](https://s3.console.aws.amazon.com/s3/)**
2. Click **"Create bucket"**
3. Bucket name: `fasaldrishti-images` (must be globally unique — add your team name if taken, e.g., `fasaldrishti-images-team42`)
4. Region: **ap-south-1**
5. Keep all defaults (Block all public access = ON)
6. Click **"Create bucket"**

### 📝 If you changed the bucket name, tell me:
```
S3_BUCKET_NAME=fasaldrishti-images-<your-suffix>
```

---

## Step 5: Verify Amazon Translate (No setup needed!)

Amazon Translate is enabled by default — no extra setup required.  
The IAM policy `TranslateFullAccess` from Step 3 covers it.

**Supported languages in our app:**
| # | Language | Code |
|---|----------|------|
| 1 | English | en |
| 2 | Hindi | hi |
| 3 | Tamil | ta |
| 4 | Telugu | te |
| 5 | Kannada | kn |
| 6 | Bengali | bn |
| 7 | Marathi | mr |
| 8 | Punjabi | pa |
| 9 | Gujarati | gu |

---

## Step 6: Share Credentials with Me

After completing steps 1-4, share these values:

```bash
# ── REQUIRED ──
AWS_ACCESS_KEY_ID=AKIA________________
AWS_SECRET_ACCESS_KEY=________________
AWS_REGION=ap-south-1

# ── ONLY IF YOU CHANGED DEFAULTS ──
S3_BUCKET_NAME=fasaldrishti-images
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

I'll plug them into the `.env` file and the real AI pipeline will go live instantly.

---

## How the Pipeline Works (Architecture)

```
📱 Farmer's WhatsApp
       │
       ▼
┌──────────────────┐
│  Twilio Webhook   │ ← incoming image
│  (ngrok tunnel)   │
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│           FasalDrishti AI Pipeline            │
│                                              │
│  Stage 1: Image Preprocessing                │
│  ├─ Validate format (JPEG/PNG/WebP)          │
│  ├─ Resize to 1024px max (optimize speed)    │
│  └─ Convert RGBA→RGB, compress               │
│                                              │
│  Stage 2: AI Analysis (fallback chain)       │
│  ├─ 🥇 Amazon Bedrock Claude 3.5 Sonnet v2   │
│  │   └─ Crop ID → Disease diagnosis →        │
│  │     Severity → Symptoms → Confidence      │
│  ├─ 🥈 Amazon Rekognition (if Bedrock fails) │
│  │   └─ Label detection → crop mapping        │
│  └─ 🥉 Local Disease DB (demo fallback)      │
│                                              │
│  Stage 3: Disease DB Enrichment              │
│  ├─ Match AI result to 12+ known diseases    │
│  ├─ Add treatment plans (chemical + organic) │
│  ├─ Add dosage, cost/acre, frequency         │
│  └─ Add prevention tips                      │
│                                              │
│  Stage 4: Amazon Translate                   │
│  └─ Translate to user's chosen language      │
│                                              │
│  Stage 5: S3 Archival                        │
│  └─ Store image + result for analytics       │
└──────────────────────────────────────────────┘
       │
       ▼
📱 WhatsApp Reply in farmer's language
   ├─ 🔍 Disease name + Hindi name
   ├─ 📊 Confidence % + Severity
   ├─ 📝 Description
   ├─ 💊 Chemical treatments + dosage + cost
   ├─ 🌿 Organic alternatives
   └─ 🛡️ Prevention tips
```

---

## Quick Verification Checklist

After sharing credentials, I'll verify each service:

- [ ] **Bedrock**: Send test image → get real AI diagnosis
- [ ] **Translate**: Hindi → Tamil/Telugu/Bengali translation works
- [ ] **Rekognition**: Label detection returns plant/leaf labels
- [ ] **S3**: Image uploaded + result JSON saved
- [ ] **End-to-end**: WhatsApp photo → real AI response in chosen language

---

## Cost Estimates for Hackathon

| Activity | Unit Cost | Est. Usage | Total |
|----------|-----------|------------|-------|
| Bedrock Claude 3.5 Sonnet v2 (vision) | ~$0.003/image | 500 demo images | $1.50 |
| Amazon Translate | $15/million chars | ~50,000 chars | $0.75 |
| Rekognition DetectLabels | $0.001/image | 100 images | $0.10 |
| S3 Storage | $0.023/GB | ~0.5 GB | $0.01 |
| **Total** | | | **~$2.36** |

Well within your $100 credits! 💰

---

## Troubleshooting

### "AccessDeniedException" on Bedrock
→ Model access not enabled. Redo Step 2.

### "UnrecognizedClientException"
→ Wrong access key. Verify `AWS_ACCESS_KEY_ID` is correct.

### "Could not connect to endpoint URL"
→ Wrong region. Ensure `AWS_REGION=ap-south-1` matches where you enabled Bedrock.

### Bedrock model not available in ap-south-1
→ Some models have limited regional availability.  
→ Switch to `us-east-1`: Update `AWS_REGION=us-east-1` in `.env`

### S3 "BucketAlreadyExists"
→ Bucket names are globally unique. Add a suffix like `-team42`
