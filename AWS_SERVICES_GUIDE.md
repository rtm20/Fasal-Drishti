# AWS Services Guide — FasalDrishti

> A learning guide for every AWS service used in FasalDrishti.  
> Each section explains **what** the service is, **why** we use it, **how** it works in our code, and **how to verify** it's working.

---

## Table of Contents
1. [Amazon Bedrock (Claude 3.5 Sonnet v2)](#1-amazon-bedrock)
2. [Amazon Rekognition](#2-amazon-rekognition)
3. [Amazon S3](#3-amazon-s3)
4. [Amazon DynamoDB](#4-amazon-dynamodb)
5. [Amazon Translate](#5-amazon-translate)
6. [Amazon Polly](#6-amazon-polly)
7. [AWS Lambda + API Gateway](#7-aws-lambda--api-gateway)
8. [Amazon CloudWatch](#8-amazon-cloudwatch)
9. [AWS SAM (Infrastructure as Code)](#9-aws-sam)
10. [Setup & Verification](#10-setup--verification)

---

## 1. Amazon Bedrock

### What is it?
Amazon Bedrock is a fully managed service that provides access to foundation models (FMs) from leading AI companies — including Anthropic's Claude, Meta's Llama, and Amazon's Titan — all through a single unified API.

### Why do we use it?
We use **Claude 3.5 Sonnet v2** (via Bedrock) as our primary AI engine for crop disease analysis. It's a vision-capable model that can look at a photo of a plant leaf and:
- Identify the crop species
- Detect diseases from visual symptoms
- Estimate severity and confidence
- Recommend treatments

### How it works in our code
```
File: backend/app/services/ai_service.py
Function: analyze_image_with_bedrock()
```

1. We send the crop image (base64-encoded) to Claude via `bedrock-runtime.invoke_model()`
2. The prompt asks Claude to analyze the image as a plant pathologist
3. Claude returns structured JSON with disease identification, severity, confidence
4. We parse the response and enrich it with our disease database

```python
# Key API call
client = boto3.client("bedrock-runtime", region_name="ap-south-1")
response = client.invoke_model(
    modelId="apac.anthropic.claude-3-5-sonnet-20241022-v2:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_base64}},
            {"type": "text", "text": prompt}
        ]}]
    })
)
```

### How to verify
```bash
# Check Bedrock status
curl http://localhost:8001/api/whatsapp/pipeline
# Look for: "bedrock": {"available": true, "model": "apac.anthropic.claude-3-5-sonnet-20241022-v2:0"}
```

### AWS Console
- Go to: **Amazon Bedrock → Model access → Anthropic → Claude 3.5 Sonnet v2**
- Region: `ap-south-1` (Mumbai)

---

## 2. Amazon Rekognition

### What is it?
Amazon Rekognition is a computer vision service that uses deep learning to analyze images. It can detect objects, scenes, faces, text, and more — all without training your own models.

### Why do we use it?
Rekognition serves as our **fallback AI engine** when Bedrock is unavailable. It uses `detect_labels()` to identify plant-related labels (e.g., "Leaf", "Plant", "Disease", "Tomato"), and we map these to our disease database.

### How it works in our code
```
File: backend/app/services/ai_service.py
Function: analyze_image_with_rekognition()
```

1. Send image bytes to `rekognition.detect_labels()`
2. Get back labels like "Plant", "Leaf", "Tomato", "Blight"
3. Match labels to known crops and diseases in `DISEASE_DATABASE`
4. Return structured result with crop + disease + confidence

```python
client = boto3.client("rekognition", region_name="ap-south-1")
response = client.detect_labels(
    Image={"Bytes": image_bytes},
    MaxLabels=15,
    MinConfidence=60.0,
    Features=["GENERAL_LABELS"]
)
```

### How to verify
```bash
curl http://localhost:8001/api/whatsapp/pipeline
# Look for: "rekognition": {"available": true}
```

---

## 3. Amazon S3

### What is it?
Amazon S3 (Simple Storage Service) is object storage with 99.999999999% durability. Think of it as infinite, cheap, reliable file storage in the cloud.

### Why do we use it?
Two purposes:
1. **Scan Archival**: Every crop analysis is archived to S3 with the image + result JSON for analytics and auditing
2. **Voice Advisory Storage**: Polly-generated MP3 voice advisories are stored in S3 with presigned URLs so farmers can download them via WhatsApp

### How it works in our code
```
File: backend/app/services/ai_service.py → archive_scan_to_s3()
File: backend/app/services/polly_service.py → upload_voice_to_s3()
```

**Scan archival:**
```python
s3_client.put_object(
    Bucket="fasaldrishti-images",
    Key=f"scans/{phone}/{scan_id}/image.jpg",
    Body=image_bytes,
    ContentType="image/jpeg"
)
```

**Voice advisory upload:**
```python
s3_client.put_object(
    Bucket="fasaldrishti-images",
    Key=f"voice/{scan_id}.mp3",
    Body=audio_bytes,
    ContentType="audio/mpeg"
)
# Generate time-limited download URL
url = s3_client.generate_presigned_url(
    "get_object",
    Params={"Bucket": bucket, "Key": key},
    ExpiresIn=86400  # 24 hours
)
```

### Bucket structure
```
fasaldrishti-images/
├── scans/
│   └── whatsapp:+91XXXX/
│       └── abc12345/
│           ├── image.jpg
│           └── result.json
├── voice/
│   └── abc12345_hi.mp3
└── test/
    └── health-check.json
```

### Lifecycle rules
- `scans/*` → auto-deleted after **90 days**
- `voice/*` → auto-deleted after **30 days**

### How to verify
```bash
# Setup creates bucket + lifecycle
cd backend && python -m scripts.setup_aws
# Check S3 in detailed health
curl http://localhost:8001/api/health/detailed
```

---

## 4. Amazon DynamoDB

### What is it?
Amazon DynamoDB is a fully managed NoSQL database with single-digit millisecond performance at any scale. It's serverless — no servers to manage, no patching, no capacity planning.

### Why do we use it?
We use DynamoDB as our primary database for:
1. **Scan History**: Every crop analysis is stored persistently (survives server restarts)
2. **User Profiles**: Phone number, language preference, scan count
3. **Dashboard Analytics**: Stats, top diseases, severity distribution

Previously, scan history was an in-memory Python list `scan_history = []` that was lost on every restart!

### How it works in our code
```
File: backend/app/services/dynamodb_service.py
Functions: save_scan(), get_scan(), get_recent_scans(), get_scan_stats(), save_user()
```

**Two tables:**

| Table | Partition Key | Sort Key | GSI | Purpose |
|-------|-------------|---------|-----|---------|
| `fasaldrishti-scans` | `scan_id` (S) | — | `phone-index` (phone_number + timestamp) | Scan results |
| `fasaldrishti-users` | `phone_number` (S) | — | — | User profiles |

```python
# Save a scan
table = dynamodb.Table("fasaldrishti-scans")
table.put_item(Item={
    "scan_id": "abc12345",
    "phone_number": "whatsapp:+919876543210",
    "crop": "tomato",
    "disease_key": "early_blight",
    "disease_name": "Early Blight",
    "severity": "moderate",
    "confidence": 87,
    "timestamp": "2026-06-15T10:30:00Z",
    "ttl": 1760000000  # Auto-expire after 90 days
})
```

### Key features
- **TTL (Time-to-Live)**: Scans auto-delete after 90 days — cost optimization
- **GSI (Global Secondary Index)**: `phone-index` allows querying all scans for a phone number
- **Auto-creation**: Tables are created on app startup if they don't exist

### How to verify
```bash
# Tables are created on startup
python -m scripts.setup_aws  # creates tables
# Or check via health endpoint
curl http://localhost:8001/api/health/detailed
# Look for: "dynamodb": {"operational": true}

# Check via AWS CLI
aws dynamodb list-tables --region ap-south-1
aws dynamodb scan --table-name fasaldrishti-scans --max-items 5 --region ap-south-1
```

---

## 5. Amazon Translate

### What is it?
Amazon Translate is a neural machine translation service that delivers fast, high-quality language translation. It supports 75+ languages.

### Why do we use it?
Indian farmers speak many languages. We use Translate to convert disease descriptions, treatment advice, and prevention tips into the farmer's chosen language:
- Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, Punjabi

### How it works in our code
```
File: backend/app/services/ai_service.py
Function: translate_text()
```

```python
client = boto3.client("translate", region_name="ap-south-1")
response = client.translate_text(
    Text="Your tomato has early blight. Apply Mancozeb fungicide.",
    SourceLanguageCode="en",
    TargetLanguageCode="hi"  # Hindi
)
# Returns: "आपके टमाटर में अर्ली ब्लाइट है। मैनकोज़ेब फफूंदनाशक लगाएं।"
```

### Supported language codes
| Code | Language | Native |
|------|----------|--------|
| hi | Hindi | हिंदी |
| ta | Tamil | தமிழ் |
| te | Telugu | తెలుగు |
| kn | Kannada | ಕನ್ನಡ |
| bn | Bengali | বাংলা |
| mr | Marathi | मराठी |
| gu | Gujarati | ગુજરાતી |
| pa | Punjabi | ਪੰਜਾਬੀ |
| en | English | English |

### How to verify
```bash
python -m scripts.setup_aws
# Section "5. Amazon Translate" will show translated Hindi text
```

---

## 6. Amazon Polly

### What is it?
Amazon Polly turns text into lifelike speech using deep learning. It supports neural voices in multiple languages and produces natural-sounding audio.

### Why do we use it?
Many rural farmers may have limited reading ability. Polly generates **voice advisories** in their language — they can listen to the disease diagnosis and treatment plan instead of reading text.

### How it works in our code
```
File: backend/app/services/polly_service.py
Functions: generate_voice_advisory(), upload_voice_to_s3()
```

```python
client = boto3.client("polly", region_name="ap-south-1")
response = client.synthesize_speech(
    Text="नमस्ते किसान भाई। आपके टमाटर में अर्ली ब्लाइट बीमारी पाई गई है।",
    OutputFormat="mp3",
    VoiceId="Kajal",
    LanguageCode="hi-IN",
    Engine="neural"
)
audio_stream = response["AudioStream"].read()
# → MP3 bytes ready to send via WhatsApp
```

### Voice mapping
| Language | Voice ID | Language Code | Engine |
|----------|---------|---------------|--------|
| Hindi | Kajal | hi-IN | Neural |
| English (India) | Kajal | en-IN | Neural |
| Tamil | — | — | Standard |
| Telugu | — | — | Standard |

### Flow
1. After AI analysis, Polly generates an MP3 voice advisory
2. The MP3 is uploaded to S3 with a presigned URL (24-hour expiry)
3. The URL is sent to the farmer via WhatsApp as an audio message
4. Farmer can listen to the diagnosis in their language

### How to verify
```bash
python -m scripts.setup_aws
# Section "6. Amazon Polly" will generate a test Hindi audio file
# Check: scripts/test_polly_output.mp3
```

---

## 7. AWS Lambda + API Gateway

### What is it?
- **AWS Lambda**: Run code without provisioning servers. Pay only for compute time.
- **API Gateway**: Create, publish, and manage HTTP APIs at any scale.

Together, they form a **serverless deployment option** — no EC2 instances, no Docker, no server management.

### Why do we use it?
Lambda + API Gateway allows FasalDrishti to scale from 0 to millions of requests automatically without any infrastructure management. This is ideal for real-world deployment where traffic is unpredictable.

### How it works in our code
```
File: backend/lambda_handler.py — Mangum wraps FastAPI for Lambda
File: infrastructure/template.yaml — SAM template defines all resources
```

**Lambda handler:**
```python
from mangum import Mangum
from app.main import app

handler = Mangum(app, lifespan="off")
# AWS Lambda invokes handler(event, context)
# Mangum translates API Gateway event ↔ FastAPI ASGI
```

**SAM template defines:**
- Lambda function (Python 3.13, 512MB RAM, 60s timeout)
- HTTP API Gateway (routes all requests to Lambda)
- DynamoDB tables
- S3 bucket
- IAM permissions for all services
- CloudWatch log group

### How to deploy
```bash
# Install SAM CLI: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
cd infrastructure

# Build
sam build

# Deploy (guided mode for first time)
sam deploy --guided

# After deploy, you get an API Gateway URL like:
# https://abc123.execute-api.ap-south-1.amazonaws.com/
```

### How to verify
```bash
# After deploy:
curl https://your-api-url.execute-api.ap-south-1.amazonaws.com/api/health
# → {"status": "healthy", "service": "FasalDrishti API"}
```

---

## 8. Amazon CloudWatch

### What is it?
Amazon CloudWatch monitors AWS resources and applications. It collects metrics, logs, and events — giving you a unified view of your infrastructure and app health.

### Why do we use it?
Three purposes:
1. **Structured Logging**: JSON logs of every scan, error, and WhatsApp message — searchable in CloudWatch Logs
2. **Custom Metrics**: ScanCount, ScanLatency, DiseaseDetections, ScanErrors — visible in CloudWatch dashboards
3. **Monitoring**: Track app health, set alarms, visualize trends

### How it works in our code
```
File: backend/app/services/cloudwatch_service.py
Classes: CloudWatchLogger (logs), publish_scan_metric() (metrics)
```

**Structured logging:**
```python
cloudwatch_logger.log_scan(
    scan_id="abc123",
    crop="tomato",
    disease="early_blight",
    severity="moderate",
    confidence=87.5,
    analysis_method="rekognition",
    latency_ms=1200,
    language="hi"
)
# → Sends JSON to CloudWatch Logs: /fasaldrishti/application
```

**Custom metrics:**
```python
publish_scan_metric(
    crop="tomato",
    disease="early_blight",
    severity="moderate",
    latency_ms=1200,
    analysis_method="rekognition"
)
# → CloudWatch Metrics: FasalDrishti/ScanCount, ScanLatency, DiseaseDetections
```

### CloudWatch Metrics published
| Metric | Unit | Dimensions |
|--------|------|------------|
| ScanCount | Count | Environment, AnalysisMethod |
| ScanLatency | Milliseconds | Environment, AnalysisMethod |
| DiseaseDetections | Count | Crop, Disease, Severity |
| ScanErrors | Count | Environment, AnalysisMethod |
| WhatsAppMessages | Count | Direction, MessageType, Environment |

### How to verify
```bash
curl http://localhost:8001/api/health/detailed
# Look for: "cloudwatch": {"operational": true}

# In AWS Console:
# CloudWatch → Log groups → /fasaldrishti/application
# CloudWatch → Metrics → FasalDrishti namespace
```

---

## 9. AWS SAM

### What is it?
AWS SAM (Serverless Application Model) is an Infrastructure as Code (IaC) framework for building serverless apps. It extends CloudFormation with simplified syntax for Lambda, API Gateway, and DynamoDB.

### Our template
```
File: infrastructure/template.yaml
```

Defines ALL infrastructure:
- 1 Lambda function (FastAPI wrapped with Mangum)
- 1 HTTP API Gateway
- 2 DynamoDB tables (scans + users)
- 1 S3 bucket (with lifecycle)
- 1 CloudWatch log group
- IAM policies for Bedrock, Rekognition, Translate, Polly, S3, DynamoDB, CloudWatch

### Commands
```bash
cd infrastructure
sam validate          # Check template syntax
sam build             # Build Lambda package
sam deploy --guided   # Deploy to AWS
sam delete            # Tear down all resources
```

---

## 10. Setup & Verification

### Prerequisites
1. AWS account with credentials configured
2. Python 3.13+ installed
3. `.env` file with AWS credentials

### Quick setup
```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Create .env (if not exists)
# AWS_ACCESS_KEY_ID=AKIA...
# AWS_SECRET_ACCESS_KEY=...
# AWS_REGION=ap-south-1

# 3. Run AWS setup script (creates S3 bucket + DynamoDB tables + tests all services)
python -m scripts.setup_aws

# 4. Start the backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# 5. Verify all services
curl http://localhost:8001/api/health/detailed
curl http://localhost:8001/api/whatsapp/pipeline
```

### Service count summary
| # | AWS Service | Purpose | Code File |
|---|------------|---------|-----------|
| 1 | Amazon Bedrock | AI crop disease analysis (primary) | ai_service.py |
| 2 | Amazon Rekognition | Image label detection (fallback) | ai_service.py |
| 3 | Amazon S3 | Image + voice storage | ai_service.py, polly_service.py |
| 4 | Amazon DynamoDB | Persistent scan history + users | dynamodb_service.py |
| 5 | Amazon Translate | Multilingual translation (9 languages) | ai_service.py |
| 6 | Amazon Polly | Voice advisory generation | polly_service.py |
| 7 | AWS Lambda | Serverless compute | lambda_handler.py |
| 8 | API Gateway | HTTP API routing | template.yaml |
| 9 | Amazon CloudWatch | Logging + metrics + monitoring | cloudwatch_service.py |

**Total: 9 AWS services — all with real, working code.**

---

*Built for AI for Bharat Hackathon 2026 — Track 03: Rural Innovation*
