# FasalDrishti — Design Document

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                        Client Layer                               │
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐    │
│  │  Web App      │    │  WhatsApp    │    │  Future: SMS /    │    │
│  │  (React 19)   │    │  (Meta API)  │    │  USSD / IVR      │    │
│  └──────┬───────┘    └──────┬───────┘    └──────────────────┘    │
└─────────┼──────────────────┼─────────────────────────────────────┘
          │                  │
          ▼                  ▼
┌───────────────────────────────────────────────────────────────────┐
│                        API Layer                                  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              Amazon API Gateway                           │    │
│  │   /api/analyze   /api/diseases   /api/whatsapp/webhook   │    │
│  └──────────────────────────┬───────────────────────────────┘    │
│                             │                                     │
│  ┌──────────────────────────▼───────────────────────────────┐    │
│  │          AWS Lambda / FastAPI (Python 3.13)               │    │
│  │                                                           │    │
│  │  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │    │
│  │  │ Analyze  │  │ WhatsApp │  │Dashboard │  │  Health   │  │    │
│  │  │ Router   │  │ Router   │  │ Router   │  │  Router   │  │    │
│  │  └────┬────┘  └────┬─────┘  └────┬─────┘  └──────────┘  │    │
│  │       │            │             │                        │    │
│  │  ┌────▼────────────▼─────────────▼───────┐               │    │
│  │  │         AI Service Layer               │               │    │
│  │  │  • Bedrock Claude 3.5 Sonnet v2 Analysis │               │    │
│  │  │  • Fallback Analysis (Demo Mode)       │               │    │
│  │  │  • Disease Database Lookup             │               │    │
│  │  │  • Translation (AWS Translate)         │               │    │
│  │  └──────────────────────────────────────-┘               │    │
│  └──────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌───────────────────────────────────────────────────────────────────┐
│                        Data Layer                                 │
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Bedrock   │  │ S3       │  │ DynamoDB │  │Translate │         │
│  │ Claude 3  │  │ Images   │  │ Scans    │  │ + Polly  │         │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
└───────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow — Image Analysis

```
1. User uploads image → Frontend/WhatsApp
2. Image sent to POST /api/analyze (multipart) or /api/analyze/base64
3. FastAPI handler:
   a. Validate image format and size
   b. Convert to base64 for Bedrock
   c. Call AI Service → analyze_crop_image()
4. AI Service:
   a. Try Bedrock Claude 3.5 Sonnet v2 (vision)
   b. If Bedrock fails → fallback_analysis() (random disease for demo)
   c. Parse AI response → extract disease_key, confidence, severity
   d. Look up disease_key in DISEASE_DATABASE
   e. If language != 'en' → translate via AWS Translate
5. Return structured AnalyzeResponse to client
6. Frontend displays results with treatments, symptoms, prevention
```

---

## 2. Component Design

### 2.1 Frontend Components

```
src/
├── components/
│   └── Navbar.jsx          # Fixed top navigation, mobile responsive
├── pages/
│   ├── Home.jsx            # Landing page with hero, stats, features
│   ├── Analyze.jsx         # Core: image upload + disease results
│   ├── Dashboard.jsx       # Analytics with recharts visualizations
│   └── About.jsx           # Problem/solution, tech stack, SDGs
├── utils/
│   └── api.js              # Axios client for all API calls
├── App.jsx                 # React Router configuration
└── index.css               # Tailwind v4 + custom theme
```

#### Analyze Page (Core Component)
- **Image Upload**: react-dropzone with drag-and-drop, file browser, preview
- **Language Selector**: Dropdown with 11 languages
- **Results Panel**: Disease card, severity badge, confidence score, treatments (collapsible)
- **States**: empty → uploading → analyzing (spinner) → results / error

### 2.2 Backend Modules

```
backend/
├── app/
│   ├── main.py             # FastAPI app, CORS, router registration
│   ├── config.py           # Pydantic Settings (env vars)
│   ├── models/
│   │   └── schemas.py      # Pydantic models (request/response)
│   ├── routes/
│   │   ├── analyze.py      # /api/analyze endpoints
│   │   ├── whatsapp.py     # /api/whatsapp/webhook
│   │   ├── dashboard.py    # /api/dashboard endpoints
│   │   └── health.py       # /api/health
│   ├── services/
│   │   └── ai_service.py   # Bedrock integration + fallback
│   └── data/
│       └── disease_db.py   # Disease database (12 diseases, 7 crops)
└── requirements.txt
```

### 2.3 AI Service Design

```python
# Core function signature
async def analyze_crop_image(
    image_data: bytes,
    language: str = "en"
) -> dict:
    """
    1. Encode image to base64
    2. Send to Bedrock Claude 3 with structured prompt
    3. Parse JSON response: {crop, disease_key, confidence, severity, symptoms}
    4. Look up disease_key in DISEASE_DATABASE
    5. Merge AI observations with curated treatment data
    6. Translate if language != 'en'
    7. Return complete analysis result
    """
```

**Bedrock Prompt Design:**
```
You are an expert agricultural scientist specializing in crop diseases in India.
Analyze this crop leaf image and return:
- crop: identified crop type
- disease_key: one of [tomato_early_blight, rice_blast, ...]
- confidence: 0.0 to 1.0
- severity: low/moderate/high/critical
- symptoms: list of observed symptoms
Return ONLY valid JSON.
```

### 2.4 Disease Database Schema

```python
DISEASE_DATABASE = {
    "tomato_early_blight": {
        "disease_name": "Early Blight",
        "hindi_name": "अगेती गुलसा",
        "scientific_name": "Alternaria solani",
        "crop": "Tomato",
        "category": "Fungal",
        "symptoms": [...],
        "treatments": [
            {
                "name": "Mancozeb 75% WP",
                "dosage": "2.5 g/L water",
                "application": "Foliar spray every 7-10 days",
                "cost": "₹150-200/100g"
            }
        ],
        "organic_treatments": [...],
        "prevention": [...],
        "favorable_conditions": "Temperature 24-29°C, high humidity..."
    }
}
```

---

## 3. API Design

### 3.1 POST /api/analyze
```
Request: multipart/form-data
  - file: image file (required)
  - language: string (default: "en")

Response: 200 OK
{
  "disease": "early_blight",
  "disease_name": "Early Blight",
  "hindi_name": "अगेती गुलसा",
  "scientific_name": "Alternaria solani",
  "crop": "Tomato",
  "confidence": 0.87,
  "severity": "moderate",
  "symptoms": ["Dark brown concentric rings on lower leaves"],
  "treatments": [...],
  "organic_treatments": [...],
  "prevention": [...],
  "favorable_conditions": "...",
  "description": "AI-generated analysis description"
}
```

### 3.2 POST /api/whatsapp/webhook
```
Request: WhatsApp Cloud API webhook payload
  - Messages containing images are downloaded and analyzed
  - Text messages receive welcome/help responses

Response: 200 OK (acknowledgement)
  - Asynchronous WhatsApp message sent back to user
```

---

## 4. UI/UX Design

### 4.1 Design Principles
- **Dark theme** with green accents — reduces eye strain for outdoor use
- **Large hit targets** — minimum 44px for touch-friendly interaction
- **Minimal data usage** — optimized for 2G/3G networks
- **Progressive disclosure** — collapsible treatment sections
- **Visual hierarchy** — severity badges use color coding (yellow/orange/red)

### 4.2 Color Palette
| Use | Color | Hex |
|-----|-------|-----|
| Background | Dark Navy | `#0a0a14` |
| Card Background | Dark | `#0f0f1a` |
| Primary | Green | `#22c55e` |
| Accent | Emerald | `#10b981` |
| Warning Low | Yellow | `#facc15` |
| Warning Moderate | Orange | `#f97316` |
| Warning High | Red | `#ef4444` |
| Warning Critical | Deep Red | `#dc2626` |

### 4.3 Page Layouts

**Home Page:**
- Hero section with gradient text, CTA buttons
- Stats counter (12+ diseases, 7 crops, 11 languages, <3s)
- How It Works (3 steps: Capture → Analyze → Treat)
- Feature grid (6 features)
- Supported crops & languages tags
- AWS tech stack badges
- Final CTA

**Analyze Page:**
- Left panel: Language selector, Dropzone (drag-and-drop)
- Right panel: Results card, Severity badge, Treatments (collapsible)
- Loading state: Spinner with AI analyzing message

**Dashboard Page:**
- 4 KPI cards (Total Scans, Diseases, Crops, Response Time)
- Bar chart: Disease distribution
- Pie chart: Crop distribution
- Area chart: Weekly scan trends
- Regional coverage grid
- Recent detections table

---

## 5. Deployment Architecture

### 5.1 Development
```
Frontend: Vite dev server (localhost:5173) → proxy /api → Backend
Backend: Uvicorn (localhost:8000)
```

### 5.2 Production (AWS)
```
Frontend → S3 + CloudFront (static hosting)
Backend → Lambda + API Gateway (serverless)
Images → S3
Data → DynamoDB
AI → Bedrock (Claude 3.5 Sonnet v2, ap-south-1)
Translation → Amazon Translate
Monitoring → CloudWatch
```

### 5.3 Cost Estimation ($100 Budget)
| Service | Estimated Cost |
|---------|---------------|
| Bedrock (1000 analyses) | ~$15 |
| Lambda (10K invocations) | ~$2 |
| DynamoDB (on-demand) | ~$3 |
| S3 + CloudFront | ~$5 |
| Translate (100K chars) | ~$2 |
| API Gateway | ~$3 |
| **Total** | **~$30** |

---

## 6. Security Considerations

- Environment variables for all secrets (AWS keys, WhatsApp tokens)
- CORS restricted to frontend origin in production
- Input validation via Pydantic on all endpoints
- Rate limiting on analysis endpoint
- No PII stored without explicit consent
- Image data not persisted beyond analysis (configurable)

---

## 7. Future Enhancements

1. **Offline mode** — TensorFlow Lite model for on-device inference
2. **Community reporting** — Crowdsourced disease outbreak maps
3. **Weather integration** — Predictive disease alerts based on conditions
4. **Marketplace** — Direct purchase of recommended treatments
5. **SMS/USSD** — For farmers without WhatsApp
6. **Voice interface** — Amazon Polly for spoken diagnosis
7. **Satellite imagery** — Large-scale crop health monitoring
