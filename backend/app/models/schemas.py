from pydantic import BaseModel
from typing import List, Optional, Any


class IntermediaryBase(BaseModel):
    name: Optional[str] = None
    registration_no: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    entity_type: Optional[str] = None


class Intermediary(IntermediaryBase):
    # Add any other fields that are scraped from SEBI
    validity: Optional[str] = None


class VerificationResponse(BaseModel):
    status: str
    count: int
    results: List[Intermediary]


class ScanResult(BaseModel):
    status: str
    provider: str
    score: float
    details: Optional[Any] = None