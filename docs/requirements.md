# FasalDrishti — Requirements Document

## 1. Overview

### 1.1 Product Name
**FasalDrishti** (फसल दृष्टि — "Crop Vision")

### 1.2 Purpose
An AI-powered crop disease detection platform that helps smallholder Indian farmers identify crop diseases instantly using a photograph, accessible via WhatsApp and web interface in 11 Indian languages.

### 1.3 Target Users
- Smallholder farmers in rural India (primary)
- Agricultural extension officers
- Krishi Vigyan Kendras (Farm Science Centres)
- Agricultural input dealers

---

## 2. User Stories

### US-001: Image-Based Disease Detection
**As a** farmer,  
**I want to** upload a photo of my crop leaf,  
**So that** I can identify the disease affecting my crop.

**Acceptance Criteria:**
- User can upload JPG/PNG/WebP images up to 10MB
- AI analysis completes within 5 seconds
- Results include disease name, confidence score, and severity level
- Fallback analysis works when Bedrock is unavailable

### US-002: Multi-Language Support
**As a** farmer who speaks Hindi/Tamil/Telugu/etc.,  
**I want to** receive results in my local language,  
**So that** I can understand the diagnosis and treatment.

**Acceptance Criteria:**
- Language selector offers 11 Indian languages
- Disease names shown in selected language
- Treatment recommendations translated accurately
- UI labels remain in English (for now)

### US-003: Treatment Recommendations
**As a** farmer with an identified crop disease,  
**I want to** see treatment options with dosage and cost,  
**So that** I can take action to save my crop.

**Acceptance Criteria:**
- Chemical treatments with product name, dosage, application method, and cost
- Organic/bio alternatives listed separately
- Prevention tips for future seasons
- Favorable conditions warning

### US-004: WhatsApp Integration
**As a** farmer without a smartphone app,  
**I want to** send a crop photo via WhatsApp,  
**So that** I can get disease diagnosis on my existing phone.

**Acceptance Criteria:**
- WhatsApp webhook receives and processes images
- Response includes disease name, treatment, and follow-up steps
- Response formatted for readability on mobile devices
- Hindi response by default via WhatsApp

### US-005: Analytics Dashboard
**As an** agricultural officer,  
**I want to** view disease detection statistics,  
**So that** I can understand regional disease patterns.

**Acceptance Criteria:**
- Display total scans, diseases detected, crops covered
- Bar chart showing disease distribution
- Pie chart showing crop distribution
- Area chart showing scan trends over time
- Regional coverage breakdown

### US-006: Disease Information Library
**As a** farmer or extension officer,  
**I want to** browse the complete disease database,  
**So that** I can learn about diseases proactively.

**Acceptance Criteria:**
- List all 12 supported diseases
- Each disease shows symptoms, treatments, prevention
- Filterable by crop type

---

## 3. Functional Requirements

### FR-001: Image Upload & Analysis
- Accept image upload via multipart form data
- Accept base64-encoded images
- Support JPG, PNG, WebP formats
- Maximum file size: 10MB
- Return structured JSON response with disease analysis

### FR-002: AI Disease Detection Engine
- Use Amazon Bedrock Claude 3 Sonnet for vision analysis
- Provide fallback random analysis for demo mode
- Return: crop type, disease key, confidence (0-1), severity level
- Map disease key to treatment database

### FR-003: Disease & Treatment Database
- 12 diseases across 7 crops
- Each disease includes: name (EN + Hindi), scientific name, symptoms, treatments (chemical + organic), prevention, favorable conditions
- Treatment includes: product name, dosage, application method, cost estimate

### FR-004: Multi-Language Translation
- Amazon Translate for real-time translation
- 11 languages: Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, Punjabi, Malayalam, Odia, Assamese
- Translate treatment descriptions and symptoms

### FR-005: WhatsApp Webhook
- Verify webhook with challenge token
- Process incoming image messages
- Format and send diagnosis response
- Handle text messages (welcome/help)

### FR-006: Dashboard API
- Total scan count statistics
- Disease detection frequency
- Supported crops and languages
- Recent scan history

---

## 4. Non-Functional Requirements

### NFR-001: Performance
- Image analysis: < 5 seconds end-to-end
- API response time: < 200ms for non-AI endpoints
- Frontend initial load: < 3 seconds on 3G

### NFR-002: Scalability
- Serverless architecture via AWS Lambda
- DynamoDB auto-scaling for scan history
- S3 for unlimited image storage

### NFR-003: Availability
- 99.9% uptime target
- Graceful fallback when Bedrock is unavailable
- CDN for frontend static assets

### NFR-004: Security
- CORS properly configured
- Input validation on all API endpoints
- No PII stored without consent
- Environment variables for secrets

### NFR-005: Accessibility
- Works on low-bandwidth (< 100kbps) networks
- WhatsApp integration for feature phones
- 11 Indian language support
- High-contrast dark UI for outdoor visibility

---

## 5. Constraints

- **Budget**: $100 AWS credits for hackathon prototype
- **Timeline**: 7-day development window
- **Infrastructure**: Must use AWS services (hackathon requirement)
- **AI Model**: Amazon Bedrock Claude 3 Sonnet (vision capabilities)
