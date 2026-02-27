<<<<<<< HEAD
# 🌱 FasalDrishti — AI-Powered Crop Disease Detection for Indian Farmers

> **AI for Bharat Hackathon 2026** | Track 03: AI for Rural Innovation & Sustainable Systems

## 🎯 Overview

**FasalDrishti** (फसल दृष्टि — "Crop Vision") is an AI-powered crop disease detection platform that helps smallholder farmers across rural India identify crop diseases instantly through a simple photograph. Accessible via **WhatsApp** in **11 Indian languages**, it provides actionable treatment recommendations with dosage, cost, and organic alternatives.

## 🔥 Key Features

| Feature | Description |
|---------|-------------|
| 📸 **Snap & Detect** | Upload a crop leaf photo for instant AI diagnosis |
| 🧠 **AI-Powered** | Amazon Bedrock Claude 3.5 Sonnet v2 for expert-grade analysis |
| 💬 **WhatsApp Integration** | No app download — works on any phone farmers already own |
| 🌐 **11 Indian Languages** | Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, Punjabi, Malayalam, Odia, Assamese |
| 💊 **Treatment Plans** | Chemical + organic treatments with exact dosage and cost |
| 📊 **Analytics Dashboard** | Real-time insights on disease trends and regional coverage |
| ⚡ **Fast & Lightweight** | Under 3-second response, optimized for low-bandwidth networks |

## 🏗️ Architecture

```
┌─────────────┐     ┌───────────────┐     ┌────────────────┐
│  WhatsApp /  │────▶│  API Gateway  │────▶│  FastAPI /      │
│  Web UI      │     │               │     │  Lambda         │
└─────────────┘     └───────────────┘     └───────┬────────┘
                                                   │
                    ┌──────────────────────────────┤
                    │                              │
              ┌─────▼──────┐  ┌──────────┐  ┌─────▼──────┐
              │  Bedrock    │  │ Translate │  │  DynamoDB   │
              │  Claude 3   │  │ + Polly   │  │  + S3       │
              └────────────┘  └──────────┘  └────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **React 19** + **Vite 6** — Modern UI framework
- **Tailwind CSS v4** — Utility-first styling
- **Recharts** — Analytics dashboard visualizations
- **React Router v6** — Client-side routing

### Backend
- **Python 3.13** + **FastAPI** — High-performance async API
- **Pydantic v2** — Data validation
- **Boto3** — AWS SDK for Python

### AWS Services
- **Amazon Bedrock** (Claude 3.5 Sonnet v2) — AI vision-based disease detection
- **Amazon S3** — Image storage
- **Amazon DynamoDB** — Scan history and user data
- **AWS Lambda** — Serverless compute
- **Amazon API Gateway** — RESTful API management
- **Amazon Translate** — Multi-language support
- **Amazon Polly** — Voice responses
- **Amazon CloudWatch** — Monitoring and logging

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- AWS Account with Bedrock access

### Backend Setup
```bash
cd FasalDrishti/backend
pip install -r requirements.txt
cp .env.example .env  # Configure your AWS credentials
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd FasalDrishti/frontend
npm install
npm run dev
```

### Environment Variables
Create a `.env` file in the `backend/` directory:
```env
APP_ENV=development
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
S3_BUCKET_NAME=fasaldrishti-images
WHATSAPP_API_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

## 📱 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/analyze` | Upload image for disease detection |
| `POST` | `/api/analyze/base64` | Analyze base64-encoded image |
| `GET` | `/api/diseases` | List all supported diseases |
| `GET` | `/api/diseases/{key}` | Get disease details |
| `GET` | `/api/crops` | List supported crops |
| `GET` | `/api/scans` | Get scan history |
| `GET` | `/api/dashboard/stats` | Dashboard statistics |
| `GET` | `/api/dashboard/supported` | Supported crops & languages |
| `GET` | `/api/whatsapp/webhook` | WhatsApp webhook verification |
| `POST` | `/api/whatsapp/webhook` | WhatsApp message handler |

## 🌾 Supported Crops & Diseases

| Crop | Diseases |
|------|----------|
| 🍅 Tomato | Early Blight, Late Blight, Leaf Curl Virus |
| 🌾 Rice | Blast, Brown Spot |
| 🌾 Wheat | Leaf Rust, Yellow Rust |
| 🧶 Cotton | Bacterial Blight |
| 🥔 Potato | Late Blight |
| 🌶️ Chili | Anthracnose / Fruit Rot |
| 🧅 Onion | Purple Blotch |

## 📊 Impact

- **10M+ farmers** reachable via WhatsApp
- **30-40% reduction** in crop losses through early detection
- **₹15K-20K savings** per farmer per season
- **11 Indian languages** for accessibility

## 🌍 UN SDG Alignment

- **SDG 1** — No Poverty (higher yields = better income)
- **SDG 2** — Zero Hunger (reduced crop losses)
- **SDG 12** — Responsible Consumption (optimized pesticide use)
- **SDG 15** — Life on Land (sustainable farming practices)

## 📄 License

MIT License — Built with ❤️ for Indian Farmers

## 👥 Team

**Team FasalDrishti** — AI for Bharat Hackathon 2026
=======
# 🌾 FasalDrishti (फसल दृष्टि)

> **"Send a photo, save your crop"**

[![AI for Bharat](https://img.shields.io/badge/Hackathon-AI%20for%20Bharat-orange)](https://github.com)
[![Powered by AWS](https://img.shields.io/badge/Powered%20by-AWS-FF9900?logo=amazon-aws)](https://aws.amazon.com)
[![Track](https://img.shields.io/badge/Track-Rural%20Innovation-green)](https://github.com)

**FasalDrishti** is an AI-powered crop disease detection and advisory system that enables farmers to identify crop diseases instantly by simply sending a photo via WhatsApp. The system delivers actionable treatment recommendations in 12+ Indian languages, including voice responses for accessibility.

---

## 🎯 Problem Statement

| Challenge | Impact |
|-----------|--------|
| Crop diseases cause 20-40% annual yield loss | ₹50,000+ crore economic loss per year |
| 1 extension officer serves 1,000+ farmers | Delayed expert advice (3-7 days) |
| Language barrier with existing apps | Most apps are English-only |
| Poor internet in rural areas | Heavy apps don't work reliably |
| 40% rural population has limited literacy | Text-based apps are inaccessible |

---

## 💡 Our Solution

FasalDrishti brings **expert-level crop disease diagnosis to every farmer's pocket** through the app they already use daily - **WhatsApp**. No downloads, no learning curve, no language barriers.

```
📱 Open WhatsApp → 📸 Send crop photo → 🤖 AI analyzes → 💊 Get treatment advice (in local language + voice)
```

### Key Features

- 🔍 **Instant Disease Detection** - AI-powered diagnosis in < 30 seconds
- 🗣️ **12+ Indian Languages** - Hindi, Tamil, Telugu, Kannada, Marathi, Bengali & more
- 🎧 **Voice Responses** - Audio advisories for farmers with limited literacy
- 💊 **Treatment Recommendations** - Specific pesticides/fungicides with local brand names
- 📍 **Shop Locator** - Find nearest agri-input stores
- 📱 **Zero Download** - Works entirely on WhatsApp
- 📶 **Low Bandwidth** - Optimized for 2G networks with SMS fallback

---

## 🏗️ Architecture Overview

FasalDrishti is built on a serverless AWS architecture for scalability and cost-efficiency:

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   WhatsApp    │────▶│  API Gateway  │────▶│    Lambda     │
│   Business    │     │               │     │   Functions   │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                    │
        ┌───────────────────────────────────────────┼───────────────────────────┐
        │                                           │                           │
        ▼                                           ▼                           ▼
┌───────────────┐                         ┌───────────────┐           ┌───────────────┐
│ Amazon Bedrock│                         │   DynamoDB    │           │ Amazon Polly  │
│ (Claude Vision)│                        │ (Disease DB)  │           │ (Voice Gen)   │
└───────────────┘                         └───────────────┘           └───────────────┘
        │                                           │                           │
        ▼                                           ▼                           ▼
┌───────────────┐                         ┌───────────────┐           ┌───────────────┐
│ Amazon S3     │                         │   Amazon      │           │   Amazon      │
│ (Image Store) │                         │   Translate   │           │   Location    │
└───────────────┘                         └───────────────┘           └───────────────┘
```

### AWS Services Used

| Service | Purpose |
|---------|---------|
| **Amazon Bedrock** | AI/ML inference for disease detection (Claude 3.5 Sonnet v2) |
| **Amazon Translate** | Multi-language translation (12+ languages) |
| **Amazon Polly** | Text-to-speech for voice responses |
| **Amazon DynamoDB** | Disease database & user data storage |
| **Amazon S3** | Image storage and static assets |
| **AWS Lambda** | Serverless compute for all processing |
| **Amazon API Gateway** | REST API endpoint for WhatsApp webhook |
| **Amazon Comprehend** | Language detection from user messages |
| **Amazon Location Service** | Nearby shop finder |
| **Amazon CloudWatch** | Monitoring and logging |

---

## 🚀 How It Works

1. **Farmer sends crop photo** via WhatsApp to FasalDrishti number
2. **Image is processed** - validated, compressed, stored in S3
3. **AI analyzes the image** using Amazon Bedrock (Claude 3.5 Sonnet v2)
4. **Disease identified** with confidence score and severity level
5. **Treatment looked up** from curated database
6. **Response translated** to farmer's preferred language
7. **Voice note generated** using Amazon Polly
8. **Complete advisory sent** back via WhatsApp (text + voice + shop info)

**Total response time: < 30 seconds**

---

## 📊 Impact Metrics

| Metric | Current State | With FasalDrishti |
|--------|---------------|-------------------|
| Disease identification time | 3-7 days | **< 30 seconds** |
| Diagnosis accuracy | ~30% (self-diagnosis) | **> 90%** |
| Language support | English only | **12+ Indian languages** |
| Cost to farmer | ₹100-500 per consultation | **FREE** |
| Crop loss reduction | - | **15-20%** |

---

## 🌱 Supported Crops (MVP)

| Crop | Common Diseases Covered |
|------|------------------------|
| 🍚 Rice | Blast, Brown Spot, Bacterial Leaf Blight |
| 🌾 Wheat | Rust (Leaf, Stem, Stripe), Powdery Mildew |
| 🍅 Tomato | Early Blight, Late Blight, Leaf Curl |
| 🥔 Potato | Late Blight, Early Blight, Black Scurf |
| 🌿 Cotton | Fusarium Wilt, Bacterial Blight |
| 🌽 Maize | Northern Leaf Blight, Gray Leaf Spot |
| 🧅 Onion | Purple Blotch, Downy Mildew |
| 🌶️ Chilli | Anthracnose, Leaf Curl, Powdery Mildew |

---

## 📁 Repository Structure

```
├── README.md                      # This file
├── requirements.md                # Detailed requirements specification
├── design.md                      # System design document
├── FasalDrishti_Idea_Submission.md # Hackathon idea submission
└── demo/
    └── index.html                 # Demo interface
```

---

## 🔗 Documentation

| Document | Description |
|----------|-------------|
| [Requirements Specification](requirements.md) | Detailed functional & non-functional requirements |
| [System Design](design.md) | Architecture, data flow, database design |
| [Idea Submission](FasalDrishti_Idea_Submission.md) | Hackathon submission document |

---

## 🎯 Target Users

- **Primary:** Smallholder farmers (< 2 hectares) in rural India
- **Secondary:** Farmer Producer Organizations (FPOs), Agricultural extension workers
- **Tertiary:** State Agriculture Departments, Agri-input retailers

---

## 🌟 Key Differentiators

| Feature | Existing Apps | FasalDrishti |
|---------|---------------|--------------|
| Platform | App Download Required | **WhatsApp (No Download)** |
| Languages | 3-5 | **12+ Indian Languages** |
| Voice Support | ❌ | **✅ Audio in local language** |
| Internet Requirement | High | **Low (2G compatible)** |
| Offline Fallback | ❌ | **✅ SMS fallback** |
| Treatment Cost Estimate | ❌ | **✅ Local shop prices** |
| Nearby Shop Locator | ❌ | **✅ GPS-based** |

---

## 👥 Team

**Team Name:** [Your Team Name]  
**Track:** AI for Rural Innovation & Sustainable Systems  
**Hackathon:** AI for Bharat - Powered by AWS

---

## 📜 License

This project was created for the **AI for Bharat Hackathon** powered by AWS.

---

## 🙏 Acknowledgments

- AWS for providing cloud infrastructure and AI/ML services
- PlantVillage dataset for training data
- Indian Council of Agricultural Research (ICAR) for disease information

---

<p align="center">
  <strong>🌾 Empowering Indian Farmers with AI 🌾</strong><br>
  <em>"Send a photo, save your crop"</em>
</p>
>>>>>>> a5e567410cc75c567bcd0d8ff14d6105e8f7d169
