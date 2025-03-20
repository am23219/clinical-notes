from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

class ProcessNoteRequest(BaseModel):
    clinical_note: str = Field(..., min_length=10, description="Clinical note text to process")
    patient_id: str = Field(..., description="Patient identifier")
    visit_id: Optional[str] = Field(None, description="Visit identifier (optional)")
    
    @validator('clinical_note')
    def validate_clinical_note(cls, v):
        if not v.strip():
            raise ValueError("Clinical note can't be empty")
        return v

class MedicationEntity(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None

class DiagnosisEntity(BaseModel):
    condition: str
    status: Optional[str] = None
    certainty: Optional[str] = None

class ProcedureEntity(BaseModel):
    name: str
    date: Optional[str] = None
    status: Optional[str] = None

class ExtractedEntities(BaseModel):
    medications: List[MedicationEntity] = []
    diagnoses: List[DiagnosisEntity] = []
    procedures: List[ProcedureEntity] = []
    allergies: List[str] = []
    vitals: Dict[str, Any] = {}

class ProcessNoteResponse(BaseModel):
    request_id: str
    patient_id: str
    visit_id: Optional[str] = None
    summary: str
    entities: ExtractedEntities
    processed_at: datetime = Field(default_factory=datetime.now)
    
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now) 