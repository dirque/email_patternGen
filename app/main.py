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
    title="Email Pattern Generator API",
    description="Generate professional email addresses using advanced pattern recognition and confidence scoring",
    version="1.0.0",
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
        "version": "1.0.0",
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
        "version": "1.0.0"
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
    Simple API stats
    """
    return {
        "api_name": "Email Pattern Generator",
        "version": "1.0.0",
        "status": "operational",
        "validation": "Pydantic LeadInput model",
        "supported_patterns": [
            "firstname.lastname@domain.com",
            "firstname@domain.com", 
            "f.lastname@domain.com",
            "firstnamelastname@domain.com",
            "firstname_lastname@domain.com"
        ],
        "supported_industries": [
            "Technology", "Fintech", "Finance", 
            "Consulting", "Healthcare", "Manufacturing"
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