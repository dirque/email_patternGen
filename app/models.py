# app/models.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class LeadInput(BaseModel):
    """Input model for a single lead"""
    firstName: str = Field(..., min_length=1, max_length=50, description="First name of the person")
    lastName: Optional[str] = Field(None, max_length=50, description="Last name of the person")
    companyDomain: str = Field(..., min_length=3, description="Company domain (e.g., example.com)")
    companyName: Optional[str] = Field(None, max_length=100, description="Company name")
    companyIndustry: Optional[str] = Field(None, max_length=50, description="Industry type")
    companySize: Optional[str] = Field(None, description="Company size (e.g., 51-200)")
    jobTitle: Optional[str] = Field(None, max_length=100, description="Job title")
    
    # Additional fields that might come from Code35
    fullName: Optional[str] = None
    linkedinUrl: Optional[str] = None
    companyWebsite: Optional[str] = None
    companyLocation: Optional[str] = None
    
    @validator('firstName')
    def validate_first_name(cls, v):
        if not v or not v.strip():
            raise ValueError('First name cannot be empty')
        return v.strip()
    
    @validator('companyDomain')
    def validate_domain(cls, v):
        if not v or not v.strip():
            raise ValueError('Company domain cannot be empty')
        # Basic domain validation
        domain = v.strip().lower()
        # Remove protocol and www if present
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
        # Remove trailing slash
        domain = domain.rstrip('/')
        # Basic format check
        if '.' not in domain or len(domain) < 3:
            raise ValueError('Invalid domain format')
        return domain
    
    class Config:
        extra = "allow"  # Allow extra fields from Code35
        schema_extra = {
            "example": {
                "firstName": "Bernard",
                "lastName": "Vrijburg",
                "companyDomain": "optimassolutions.com",
                "companyName": "Optimas Solutions",
                "companyIndustry": "Technology",
                "companySize": "51-200",
                "jobTitle": "Solutions Manager"
            }
        }

class EmailCandidate(BaseModel):
    """Single email candidate with confidence score"""
    email: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    pattern: str
    reasoning: Optional[str] = None

class EmailResult(BaseModel):
    """Result for single email generation"""
    success: bool
    lead_data: Dict[str, Any]
    generated_email: Optional[str]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    pattern_used: Optional[str]
    reasoning: Optional[str]
    all_candidates: List[EmailCandidate] = []
    processing_time_ms: Optional[int] = 0
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "lead_data": {
                    "firstName": "Bernard",
                    "lastName": "Vrijburg",
                    "companyDomain": "optimassolutions.com",
                    "generatedEmail": "bernard.vrijburg@optimassolutions.com"
                },
                "generated_email": "bernard.vrijburg@optimassolutions.com",
                "confidence_score": 0.847,
                "pattern_used": "firstname.lastname",
                "reasoning": "Pattern: firstname.lastname (0.85) | Domain: 0.75 | Names: 0.90 | Industry: tech",
                "all_candidates": [
                    {
                        "email": "bernard.vrijburg@optimassolutions.com",
                        "confidence": 0.847,
                        "pattern": "firstname.lastname",
                        "reasoning": "High confidence pattern for tech industry"
                    }
                ]
            }
        }

class BulkEmailResult(BaseModel):
    """Result for bulk email generation"""
    success: bool
    total_processed: int
    successful_generations: int
    failed_generations: int
    results: List[Dict[str, Any]]
    processing_time_ms: Optional[int] = 0
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "total_processed": 100,
                "successful_generations": 95,
                "failed_generations": 5,
                "results": ["...array of enriched lead objects..."],
                "processing_time_ms": 1500
            }
        }

class ProcessingStatus(BaseModel):
    """Status of background file processing task"""
    task_id: str
    status: str = Field(..., description="queued, processing, completed, or failed")
    total_leads: int
    processed_leads: int = 0
    successful_generations: int = 0
    failed_generations: int = 0
    created_at: datetime
    updated_at: datetime
    input_file: Optional[str] = None
    output_file: Optional[str] = None
    error_message: Optional[str] = None
    
    @property
    def progress_percentage(self) -> float:
        if self.total_leads == 0:
            return 0.0
        return (self.processed_leads / self.total_leads) * 100
    
    @property
    def success_rate(self) -> float:
        if self.processed_leads == 0:
            return 0.0
        return (self.successful_generations / self.processed_leads) * 100
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "processing",
                "total_leads": 1000,
                "processed_leads": 750,
                "successful_generations": 720,
                "failed_generations": 30,
                "created_at": "2025-01-15T10:00:00Z",
                "updated_at": "2025-01-15T10:05:00Z"
            }
        }

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    message: str
    timestamp: datetime
    version: str
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "message": "Email Pattern Generator API is running",
                "timestamp": "2025-01-15T10:00:00Z",
                "version": "1.0.0"
            }
        }

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: bool = True
    message: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "error": True,
                "message": "Validation failed",
                "detail": "First name cannot be empty",
                "timestamp": "2025-01-15T10:00:00Z"
            }
        }