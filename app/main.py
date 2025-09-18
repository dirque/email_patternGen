from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import logging
from datetime import datetime

from .services.email_generator import EnhancedEmailPatternGenerator

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

@app.post("/generate-email")
async def generate_single_email(lead_data: dict):
    """
    Generate email for a single lead
    No validation - assumes pre-validated data from Code35
    """
    try:
        logger.info(f"Generating email for {lead_data.get('firstName', 'Unknown')}")
        
        # Process the lead
        result = email_generator.process_lead_data(lead_data)
        
        return {
            "success": True,
            "lead_data": result,
            "generated_email": result.get('generatedEmail'),
            "confidence_score": result.get('emailConfidence', 0.0),
            "pattern_used": result.get('emailPattern'),
            "reasoning": result.get('emailReasoning'),
            "all_candidates": result.get('emailCandidates', [])
        }
        
    except Exception as e:
        logger.error(f"Error generating email: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate email: {str(e)}"
        )

@app.post("/enrich-leads-batch")
async def enrich_leads_batch(leads: List[dict]):
    """
    Main endpoint for Code35 integration
    Enriches a batch of leads with email data
    """
    if len(leads) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Maximum 1000 leads allowed per request. Split into smaller batches."
        )
    
    try:
        logger.info(f"Processing {len(leads)} leads in batch")
        
        # Process all leads
        enriched_leads = email_generator.process_leads_batch(leads)
        
        # Calculate stats
        successful = len([lead for lead in enriched_leads if lead.get('generatedEmail')])
        failed = len(leads) - successful
        
        return {
            "success": True,
            "total_processed": len(leads),
            "successful_generations": successful,
            "failed_generations": failed,
            "success_rate": f"{(successful/len(leads)*100):.1f}%" if leads else "0%",
            "enriched_leads": enriched_leads
        }
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch processing failed: {str(e)}"
        )

@app.post("/generate-emails-bulk") 
async def generate_bulk_emails(leads: List[dict]):
    """
    Alternative bulk endpoint (same as enrich-leads-batch)
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