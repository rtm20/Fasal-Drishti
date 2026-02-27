"""
FasalDrishti - Pydantic Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    none = "none"
    mild = "mild"
    moderate = "moderate"
    severe = "severe"


class Language(str, Enum):
    en = "en"
    hi = "hi"
    ta = "ta"
    te = "te"
    kn = "kn"
    mr = "mr"
    bn = "bn"
    gu = "gu"
    pa = "pa"
    or_ = "or"
    ml = "ml"
    as_ = "as"


class TreatmentItem(BaseModel):
    name: str
    dosage: str
    method: str
    frequency: str
    cost_per_acre: int


class AnalysisResult(BaseModel):
    crop: str
    crop_hindi: Optional[str] = None
    disease_key: str
    disease_name: str
    hindi_name: Optional[str] = None
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    confidence: int = Field(ge=0, le=100)
    severity: Severity
    description: str
    description_hindi: Optional[str] = None
    symptoms_observed: List[str] = []
    all_symptoms: List[str] = []


class TreatmentResponse(BaseModel):
    chemical: List[TreatmentItem] = []
    organic: List[str] = []
    prevention: List[str] = []


class AnalyzeResponse(BaseModel):
    success: bool
    analysis: AnalysisResult
    treatment: TreatmentResponse
    metadata: dict = {}


class AnalyzeRequest(BaseModel):
    image_base64: str = Field(description="Base64 encoded image")
    language: Language = Language.en
    crop_hint: Optional[str] = None


class ScanRecord(BaseModel):
    scan_id: str
    user_id: Optional[str] = None
    crop: str
    disease_key: str
    disease_name: str
    severity: Severity
    confidence: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    location: Optional[dict] = None


class DashboardStats(BaseModel):
    total_scans: int
    diseases_detected: int
    crops_analyzed: int
    top_diseases: List[dict]
    severity_distribution: dict
    recent_scans: List[dict]
