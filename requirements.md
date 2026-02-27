# FasalDrishti - Requirements Specification

## Project Overview

**Project Name:** FasalDrishti (फसल दृष्टि)  
**Tagline:** "Send a photo, save your crop"  
**Track:** AI for Rural Innovation & Sustainable Systems  
**Hackathon:** AI for Bharat - Powered by AWS

---

## 1. Problem Statement

### 1.1 Current Challenges

| Challenge | Impact |
|-----------|--------|
| Crop diseases cause 20-40% annual yield loss in India | ₹50,000+ crore economic loss per year |
| 1 agricultural extension officer serves 1,000+ farmers | Delayed expert advice (3-7 days) |
| Farmers cannot identify diseases in early stages | Irreversible crop damage |
| Existing apps require downloads and are English-only | Low adoption in rural areas |
| Poor internet connectivity in villages | Heavy apps fail to work |
| 40% rural population has limited literacy | Text-based apps are inaccessible |

### 1.2 Target Users

**Primary Users:**
- Smallholder farmers (< 2 hectares) in rural India
- Farmer Producer Organizations (FPOs)
- Agricultural extension workers

**Secondary Users:**
- State Agriculture Departments
- Agri-input retailers
- Agricultural research institutions

### 1.3 User Personas

#### Persona 1: Ramesh (Smallholder Farmer)
- **Age:** 45 years
- **Location:** Village in Maharashtra
- **Education:** 8th standard
- **Technology:** Basic smartphone with WhatsApp
- **Pain Points:** Cannot identify crop diseases, relies on neighbors' advice, often buys wrong pesticides
- **Needs:** Quick, reliable disease diagnosis in Marathi with voice support

#### Persona 2: Lakshmi (Progressive Farmer)
- **Age:** 35 years
- **Location:** Tamil Nadu
- **Education:** 12th standard
- **Technology:** Smartphone, moderate internet
- **Pain Points:** Wants to reduce pesticide costs, needs timely intervention
- **Needs:** Accurate diagnosis with specific treatment recommendations

#### Persona 3: Kumar (FPO Manager)
- **Age:** 40 years
- **Location:** Andhra Pradesh
- **Technology:** Good smartphone, decent internet
- **Pain Points:** Needs to help 500+ member farmers with disease queries
- **Needs:** Dashboard to track disease patterns, bulk advisory system

---

## 2. Solution Overview

### 2.1 Product Vision

FasalDrishti is an AI-powered crop disease detection and advisory system accessible via WhatsApp. Farmers send crop photos and receive instant disease diagnosis with treatment recommendations in their local language, including voice responses for accessibility.

### 2.2 Value Proposition

| For | Current State | With FasalDrishti |
|-----|---------------|-------------------|
| Disease identification | 3-7 days (expert visit) | < 30 seconds |
| Accuracy | ~30% (farmer self-diagnosis) | > 90% (AI-assisted) |
| Language support | English only | 12+ Indian languages |
| Accessibility | Requires app download | WhatsApp (already installed) |
| Literacy requirement | Must read text | Voice responses available |
| Cost to farmer | ₹100-500 (expert consultation) | FREE |

### 2.3 Key Differentiators

1. **Zero-friction adoption** - Works on WhatsApp, no download needed
2. **True vernacular support** - 12+ Indian languages with voice
3. **End-to-end solution** - Diagnosis + Treatment + Shop locator
4. **Designed for Bharat** - Works on 2G, SMS fallback, voice-first

---

## 3. Functional Requirements

### 3.1 Core Features

#### FR-001: Image-Based Disease Detection
| Attribute | Description |
|-----------|-------------|
| **ID** | FR-001 |
| **Priority** | P0 (Critical) |
| **Description** | System shall analyze crop images and identify diseases |
| **Input** | Crop leaf/plant image via WhatsApp |
| **Output** | Disease name, severity, confidence score |
| **Acceptance Criteria** | - Accuracy > 85% on test dataset<br>- Response time < 30 seconds<br>- Support images up to 5MB |

#### FR-002: Multi-Language Response
| Attribute | Description |
|-----------|-------------|
| **ID** | FR-002 |
| **Priority** | P0 (Critical) |
| **Description** | System shall respond in user's preferred language |
| **Languages** | Hindi, Tamil, Telugu, Kannada, Marathi, Bengali, Gujarati, Punjabi, Odia, Malayalam, Assamese, English |
| **Acceptance Criteria** | - Auto-detect language from user message<br>- Allow manual language selection<br>- Accurate translations verified by native speakers |

#### FR-003: Treatment Recommendations
| Attribute | Description |
|-----------|-------------|
| **ID** | FR-003 |
| **Priority** | P0 (Critical) |
| **Description** | System shall provide actionable treatment advice |
| **Output** | Pesticide/fungicide name, dosage, application method, timing |
| **Acceptance Criteria** | - Include local brand names<br>- Dosage calculator based on farm area<br>- Include organic alternatives where available |

#### FR-004: Voice Response Generation
| Attribute | Description |
|-----------|-------------|
| **ID** | FR-004 |
| **Priority** | P1 (High) |
| **Description** | System shall generate audio responses |
| **Output** | Voice note in user's language |
| **Acceptance Criteria** | - Natural-sounding voice<br>- Duration < 60 seconds<br>- Clear pronunciation of technical terms |

#### FR-005: Nearby Shop Locator
| Attribute | Description |
|-----------|-------------|
| **ID** | FR-005 |
| **Priority** | P1 (High) |
| **Description** | System shall suggest nearby agri-input shops |
| **Input** | User's location (GPS or manual) |
| **Output** | Shop name, distance, directions |
| **Acceptance Criteria** | - Show top 3 nearest shops<br>- Include contact information if available |

#### FR-006: Disease History Tracking
| Attribute | Description |
|-----------|-------------|
| **ID** | FR-006 |
| **Priority** | P2 (Medium) |
| **Description** | System shall maintain user's disease query history |
| **Output** | List of past diagnoses with dates |
| **Acceptance Criteria** | - Store last 20 queries per user<br>- Allow user to view history on request |

#### FR-007: Preventive Alerts
| Attribute | Description |
|-----------|-------------|
| **ID** | FR-007 |
| **Priority** | P2 (Medium) |
| **Description** | System shall send proactive disease alerts |
| **Trigger** | Disease outbreak detected in user's region |
| **Output** | Alert message with preventive measures |
| **Acceptance Criteria** | - Alert within 24 hours of outbreak detection<br>- Opt-in/opt-out functionality |

#### FR-008: Cost Estimation
| Attribute | Description |
|-----------|-------------|
| **ID** | FR-008 |
| **Priority** | P2 (Medium) |
| **Description** | System shall estimate treatment cost |
| **Input** | Disease, farm area |
| **Output** | Approximate cost in INR |
| **Acceptance Criteria** | - Based on current market prices<br>- Update prices monthly |

### 3.2 Supported Crops (MVP)

| Crop | Common Diseases Covered |
|------|------------------------|
| Rice | Blast, Brown Spot, Bacterial Leaf Blight |
| Wheat | Rust (Leaf, Stem, Stripe), Powdery Mildew |
| Tomato | Early Blight, Late Blight, Leaf Curl |
| Potato | Late Blight, Early Blight, Black Scurf |
| Cotton | Fusarium Wilt, Bacterial Blight, Bollworm damage |
| Maize | Northern Leaf Blight, Gray Leaf Spot |
| Onion | Purple Blotch, Downy Mildew |
| Chilli | Anthracnose, Leaf Curl, Powdery Mildew |

### 3.3 User Interactions

#### Interaction Flow 1: Disease Detection
```
User: [Sends crop photo]
System: "नमस्ते! आपकी फोटो का विश्लेषण हो रहा है... ⏳"
System: "🔍 बीमारी: Early Blight (अगेती झुलसा)
         ⚠️ गंभीरता: मध्यम
         💊 उपचार: [Treatment details]
         📍 नजदीकी दुकान: [Shop info]
         🎧 [Voice note attached]"
```

#### Interaction Flow 2: Language Selection
```
User: "Change language to Tamil"
System: "மொழி தமிழுக்கு மாற்றப்பட்டது! ✅"
```

#### Interaction Flow 3: Help Menu
```
User: "Help" / "मदद"
System: "FasalDrishti में आपका स्वागत है! 🌱
         
         आप क्या कर सकते हैं:
         📸 फसल की फोटो भेजें - बीमारी पहचान
         🗣️ 'भाषा बदलें' - अपनी भाषा चुनें
         📜 'इतिहास' - पिछली जांच देखें
         ❓ 'मदद' - यह मेनू"
```

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements

| Requirement | Target | Priority |
|-------------|--------|----------|
| Response Time | < 30 seconds for disease detection | P0 |
| Availability | 99.5% uptime | P0 |
| Concurrent Users | Support 10,000 simultaneous users | P1 |
| Image Processing | Handle images up to 5MB | P0 |
| Voice Generation | < 5 seconds for audio creation | P1 |

### 4.2 Scalability Requirements

| Requirement | Target |
|-------------|--------|
| Daily Active Users | Scale to 1 million |
| Daily Queries | Handle 5 million queries/day |
| Storage | Auto-scale for image storage |
| Geographic Distribution | Multi-region deployment |

### 4.3 Security Requirements

| Requirement | Description |
|-------------|-------------|
| Data Encryption | All data encrypted at rest and in transit |
| User Privacy | No personal data stored beyond phone number |
| Image Retention | Delete images after 7 days |
| Compliance | GDPR-compliant data handling |
| Authentication | WhatsApp verified phone numbers |

### 4.4 Accessibility Requirements

| Requirement | Description |
|-------------|-------------|
| Voice Support | All text responses available as voice |
| Simple Language | Use 8th-grade reading level |
| Low Bandwidth | Work on 2G connections |
| Offline Fallback | SMS-based fallback for no-data scenarios |

### 4.5 Reliability Requirements

| Requirement | Description |
|-------------|-------------|
| Error Handling | Graceful degradation on AI failure |
| Fallback | Human expert escalation for low-confidence results |
| Data Backup | Daily backups of all databases |
| Disaster Recovery | RTO < 4 hours, RPO < 1 hour |

---

## 5. Data Requirements

### 5.1 Training Data

| Dataset | Source | Size |
|---------|--------|------|
| PlantVillage | Public Dataset | 54,000+ images |
| ICAR Disease Images | Government (with permission) | 10,000+ images |
| Synthetic Data | Generated for rare diseases | 5,000+ images |

### 5.2 Knowledge Base

| Data Type | Source | Update Frequency |
|-----------|--------|------------------|
| Disease Information | ICAR, State Agri Universities | Quarterly |
| Treatment Protocols | Plant Protection Guidelines | Quarterly |
| Pesticide Database | CIB&RC Registered Products | Monthly |
| Market Prices | Agmarknet | Weekly |
| Shop Directory | Crowdsourced + Partners | Ongoing |

### 5.3 Data Privacy

- All solutions must use **synthetic or publicly available data only**
- No collection of personal farmer data beyond phone number
- Clear disclosure of data usage to users
- Opt-out mechanism for data collection

---

## 6. Integration Requirements

### 6.1 External Integrations

| System | Purpose | Type |
|--------|---------|------|
| WhatsApp Business API | User interface | Primary |
| IMD Weather API | Weather-aware advice | Optional |
| Google Maps API | Shop locations | Required |
| SMS Gateway | Fallback communication | Backup |

### 6.2 Internal Integrations

| Component | Integration Point |
|-----------|-------------------|
| AI Model | Amazon Bedrock API |
| Image Storage | Amazon S3 |
| Database | Amazon DynamoDB |
| Voice Generation | Amazon Polly |
| Translation | Amazon Translate |

---

## 7. Success Metrics

### 7.1 Key Performance Indicators (KPIs)

| Metric | Target (6 months) | Target (12 months) |
|--------|-------------------|---------------------|
| Registered Users | 100,000 | 1,000,000 |
| Daily Active Users | 10,000 | 100,000 |
| Queries Processed | 500,000 | 5,000,000 |
| Disease Detection Accuracy | > 85% | > 90% |
| User Satisfaction Score | > 4.0/5 | > 4.5/5 |
| Response Time (P95) | < 30s | < 20s |

### 7.2 Impact Metrics

| Metric | Target |
|--------|--------|
| Crop Loss Reduction | 15-20% reduction in user farms |
| Farmer Income Impact | ₹5,000 average savings per season |
| Treatment Cost Reduction | 20% through accurate diagnosis |
| Extension Officer Efficiency | 3x more farmers served |

---

## 8. Constraints & Assumptions

### 8.1 Constraints

1. **Data:** Must use only public/synthetic data (hackathon requirement)
2. **Platform:** Primary interface must be WhatsApp
3. **Budget:** Operate within AWS free tier + hackathon credits
4. **Time:** MVP in 4 weeks (hackathon timeline)
5. **Languages:** Minimum 5 languages for MVP

### 8.2 Assumptions

1. Farmers have access to basic smartphones with WhatsApp
2. Farmers can take reasonably clear photos of crop symptoms
3. WhatsApp Business API will be available for integration
4. AWS services (Bedrock, Polly, Translate) support required languages
5. Internet connectivity available (2G minimum)

### 8.3 Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low AI accuracy | User trust loss | Ensemble models, human fallback |
| WhatsApp API limitations | Feature constraints | Design within API limits |
| Language translation quality | Miscommunication | Native speaker validation |
| Scalability issues | Service degradation | Auto-scaling, load testing |

---

## 9. Glossary

| Term | Definition |
|------|------------|
| FPO | Farmer Producer Organization |
| ICAR | Indian Council of Agricultural Research |
| IMD | India Meteorological Department |
| CIB&RC | Central Insecticides Board & Registration Committee |
| Agmarknet | Agricultural Marketing Information Network |
| MVP | Minimum Viable Product |

---

## 10. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Jan 22, 2026 | Team | Initial requirements document |

---

*Document prepared for AI for Bharat Hackathon - Track 3: AI for Rural Innovation & Sustainable Systems*
