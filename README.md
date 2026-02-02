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
| **Amazon Bedrock** | AI/ML inference for disease detection (Claude 3 Vision) |
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
3. **AI analyzes the image** using Amazon Bedrock (Claude 3 Vision)
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
