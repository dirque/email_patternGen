from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import logging
from datetime import datetime

from .services.email_generator import EnhancedEmailPatternGenerator
from .models import LeadInput, EmailResult, BulkEmailResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Email Pattern Generator API",
    description="Generate professional email addresses using 50 advanced patterns with research-based confidence scoring, industry-specific optimizations, and domain correlation analysis",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - allows your Code35 script to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize email generator
email_generator = EnhancedEmailPatternGenerator()

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "status": "healthy",
        "message": "Email Pattern Generator API is running",
        "timestamp": datetime.now(),
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "single_email": "/generate-email",
            "bulk_emails": "/enrich-leads-batch",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "All systems operational",
        "timestamp": datetime.now(),
        "version": "2.0.0"
    }

@app.post("/generate-email", response_model=EmailResult)
async def generate_single_email(lead: LeadInput):
    """
    Generate email for a single lead with Pydantic validation
    """
    try:
        logger.info(f"Generating email for {lead.firstName} {lead.lastName or ''}")
        
        # Convert validated Pydantic model to dict
        lead_data = lead.dict()
        
        # Process the lead
        result = email_generator.process_lead_data(lead_data)
        
        return EmailResult(
            success=True,
            lead_data=result,
            generated_email=result.get('generatedEmail'),
            confidence_score=result.get('emailConfidence', 0.0),
            pattern_used=result.get('emailPattern'),
            reasoning=result.get('emailReasoning'),
            all_candidates=result.get('emailCandidates', [])
        )
        
    except Exception as e:
        logger.error(f"Error generating email: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate email: {str(e)}"
        )

@app.post("/enrich-leads-batch", response_model=BulkEmailResult)
async def enrich_leads_batch(leads: List[LeadInput]):
    """
    Main endpoint with Pydantic validation for each lead
    Enriches a batch of leads with email data
    """
    if len(leads) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Maximum 1000 leads allowed per request. Split into smaller batches."
        )
    
    try:
        logger.info(f"Processing {len(leads)} validated leads in batch")
        
        # Convert validated Pydantic models to dicts
        lead_dicts = [lead.dict() for lead in leads]
        
        # Process all leads
        enriched_leads = email_generator.process_leads_batch(lead_dicts)
        
        # Calculate stats
        successful = len([lead for lead in enriched_leads if lead.get('generatedEmail')])
        failed = len(leads) - successful
        
        return BulkEmailResult(
            success=True,
            total_processed=len(leads),
            successful_generations=successful,
            failed_generations=failed,
            results=enriched_leads
        )
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch processing failed: {str(e)}"
        )

@app.post("/generate-emails-bulk", response_model=BulkEmailResult)
async def generate_bulk_emails(leads: List[LeadInput]):
    """
    Alternative bulk endpoint with validation (same as enrich-leads-batch)
    """
    return await enrich_leads_batch(leads)

@app.get("/stats")
async def get_api_stats():
    """
    Enhanced API stats showing 50-pattern capabilities
    """
    return {
        "api_name": "Enhanced Email Pattern Generator",
        "version": "2.0.0",
        "status": "operational",
        "validation": "Pydantic LeadInput model",
        "total_patterns": 50,
        "pattern_categories": {
            "basic_name_standards": [
                "firstname@domain.com",
                "lastname@domain.com", 
                "firstname.lastname@domain.com",
                "firstname_lastname@domain.com",
                "firstname-lastname@domain.com",
                "f.lastname@domain.com",
                "firstname.l@domain.com",
                "flastname@domain.com",
                "lastnamef@domain.com",
                "lastname.firstname@domain.com"
            ],
            "extended_middle_initials": [
                "firstname.middlename.lastname@domain.com",
                "firstname.m.lastname@domain.com",
                "f.m.lastname@domain.com",
                "firstname+middlename+lastname@domain.com"
            ],
            "abbreviated_shortened": [
                "first3letterslastname@domain.com",
                "first4letterslastname@domain.com",
                "nickname.lastname@domain.com",
                "fn.lastname@domain.com"
            ],
            "numeric_variants": [
                "firstname.lastname1@domain.com",
                "firstname1@domain.com",
                "firstname.lastname01@domain.com",
                "firstname.lastnameYY@domain.com"
            ],
            "international_multilingual": [
                "transliteratedfirstname.lastname@domain.com",
                "firstname.x.lastname@domain.com"
            ]
        },
        "supported_industries": {
            "technology": "High confidence for tech patterns like abbreviated names",
            "education": "Specialized for .edu domains with high firstname.lastname confidence",
            "finance": "Formal patterns with strong f.lastname usage",
            "consulting": "Professional patterns similar to finance",
            "healthcare": "Standard business patterns",
            "government": "Formal government patterns optimized for .gov domains",
            "nonprofit": "Patterns optimized for .org domains",
            "traditional": "Standard business patterns for manufacturing, retail"
        },
        "domain_optimization": {
            ".edu": "Education-specific pattern weighting",
            ".org": "Nonprofit-optimized patterns", 
            ".gov": "Government formal patterns",
            ".com": "Business standard patterns",
            ".io/.tech/.ai": "Tech startup patterns"
        },
        "confidence_factors": [
            "Pattern-industry correlation (45%)",
            "Domain quality score (25%)", 
            "Name quality score (15%)",
            "Pattern-domain correlation bonus (15%)",
            "Company size modifier (5%)"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )