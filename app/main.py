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
            "all_patterns": "/patterns/all",
            "pattern_demo": "/patterns/demo", 
            "pattern_count": "/patterns/count",
            "api_stats": "/stats",
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

@app.get("/patterns/all")
async def get_all_patterns():
    """
    🎯 Display ALL 50 patterns with examples - THIS IS WHAT YOU WANTED!
    
    Returns all implemented email patterns organized by category with examples
    """
    # Get all patterns from tech industry (most comprehensive)
    tech_patterns = email_generator.pattern_weights.get('tech', {})
    
    # Pattern categories with examples
    pattern_categories = {
        "A_basic_name_standards": {
            "description": "Basic Name Standards (10 patterns)",
            "patterns": [
                {"name": "firstname", "example": "john@company.com", "weight": tech_patterns.get("firstname", 0)},
                {"name": "lastname", "example": "smith@company.com", "weight": tech_patterns.get("lastname", 0)},
                {"name": "firstname.lastname", "example": "john.smith@company.com", "weight": tech_patterns.get("firstname.lastname", 0)},
                {"name": "firstname_lastname", "example": "john_smith@company.com", "weight": tech_patterns.get("firstname_lastname", 0)},
                {"name": "firstname-lastname", "example": "john-smith@company.com", "weight": tech_patterns.get("firstname-lastname", 0)},
                {"name": "firstinitial.lastname", "example": "j.smith@company.com", "weight": tech_patterns.get("firstinitial.lastname", 0)},
                {"name": "firstname.lastinitial", "example": "john.s@company.com", "weight": tech_patterns.get("firstname.lastinitial", 0)},
                {"name": "firstinitiallastname", "example": "jsmith@company.com", "weight": tech_patterns.get("firstinitiallastname", 0)},
                {"name": "lastnamefirstinitial", "example": "smithj@company.com", "weight": tech_patterns.get("lastnamefirstinitial", 0)},
                {"name": "lastname.firstname", "example": "smith.john@company.com", "weight": tech_patterns.get("lastname.firstname", 0)}
            ]
        },
        "B_extended_middle_initials": {
            "description": "Extended Name + Middle Initials (8 patterns)",
            "patterns": [
                {"name": "firstname.middlename.lastname", "example": "john.m.smith@company.com", "weight": tech_patterns.get("firstname.middlename.lastname", 0)},
                {"name": "firstname.middleinitial.lastname", "example": "john.m.smith@company.com", "weight": tech_patterns.get("firstname.middleinitial.lastname", 0)},
                {"name": "firstinitial.middleinitial.lastname", "example": "j.m.smith@company.com", "weight": tech_patterns.get("firstinitial.middleinitial.lastname", 0)},
                {"name": "firstname+middlename+lastname", "example": "john+m+smith@company.com", "weight": tech_patterns.get("firstname+middlename+lastname", 0)},
                {"name": "firstinitial+middlename+lastname", "example": "j+m+smith@company.com", "weight": tech_patterns.get("firstinitial+middlename+lastname", 0)},
                {"name": "firstname.middleinitial", "example": "john.m@company.com", "weight": tech_patterns.get("firstname.middleinitial", 0)},
                {"name": "firstname.middleinitiallastinitial", "example": "john.ms@company.com", "weight": tech_patterns.get("firstname.middleinitiallastinitial", 0)},
                {"name": "firstname.middlename", "example": "john.m@company.com", "weight": tech_patterns.get("firstname.middlename", 0)}
            ]
        },
        "C_abbreviated_shortened": {
            "description": "Abbreviated/Shortened (10 patterns)",
            "patterns": [
                {"name": "first3letterslastname", "example": "johsmith@company.com", "weight": tech_patterns.get("first3letterslastname", 0)},
                {"name": "first4letterslastname", "example": "johnsmith@company.com", "weight": tech_patterns.get("first4letterslastname", 0)},
                {"name": "firstname+last2letters", "example": "johnsm@company.com", "weight": tech_patterns.get("firstname+last2letters", 0)},
                {"name": "firstname+first2letterslastname", "example": "josmith@company.com", "weight": tech_patterns.get("firstname+first2letterslastname", 0)},
                {"name": "first2letterslastname", "example": "josmith@company.com", "weight": tech_patterns.get("first2letterslastname", 0)},
                {"name": "first3letterslast3letters", "example": "johsmi@company.com", "weight": tech_patterns.get("first3letterslast3letters", 0)},
                {"name": "firstnameinitials", "example": "johns@company.com", "weight": tech_patterns.get("firstnameinitials", 0)},
                {"name": "shortenedname.lastname", "example": "john.smith@company.com", "weight": tech_patterns.get("shortenedname.lastname", 0)},
                {"name": "nickname.lastname", "example": "bob.smith@company.com", "weight": tech_patterns.get("nickname.lastname", 0)},
                {"name": "initials", "example": "js@company.com", "weight": tech_patterns.get("initials", 0)}
            ]
        },
        "D_numeric_variants": {
            "description": "Numeric Variants (7 patterns)",
            "patterns": [
                {"name": "firstname.lastname1", "example": "john.smith1@company.com", "weight": tech_patterns.get("firstname.lastname1", 0)},
                {"name": "firstname1", "example": "john1@company.com", "weight": tech_patterns.get("firstname1", 0)},
                {"name": "lastname1", "example": "smith1@company.com", "weight": tech_patterns.get("lastname1", 0)},
                {"name": "firstinitiallastname1", "example": "jsmith1@company.com", "weight": tech_patterns.get("firstinitiallastname1", 0)},
                {"name": "firstname.lastname01", "example": "john.smith01@company.com", "weight": tech_patterns.get("firstname.lastname01", 0)},
                {"name": "firstname.lastnameYY", "example": "john.smith25@company.com", "weight": tech_patterns.get("firstname.lastnameYY", 0)},
                {"name": "firstnameYY", "example": "john25@company.com", "weight": tech_patterns.get("firstnameYY", 0)}
            ]
        },
        "E_reversed_surname_first": {
            "description": "Reversed/Surname-first (4 patterns)",
            "patterns": [
                {"name": "lastname_firstname", "example": "smith_john@company.com", "weight": tech_patterns.get("lastname_firstname", 0)},
                {"name": "lastname-firstname", "example": "smith-john@company.com", "weight": tech_patterns.get("lastname-firstname", 0)},
                {"name": "lastnamefirstname", "example": "smithjohn@company.com", "weight": tech_patterns.get("lastnamefirstname", 0)},
                {"name": "lastnamefirstinitial", "example": "smithj@company.com", "weight": tech_patterns.get("lastnamefirstinitial", 0)}
            ]
        },
        "F_department_location_hybrids": {
            "description": "Department/Location Hybrids (4 patterns)",
            "patterns": [
                {"name": "firstname.dept", "example": "john.sales@company.com", "weight": tech_patterns.get("firstname.dept", 0)},
                {"name": "firstname.location", "example": "john.nyc@company.com", "weight": tech_patterns.get("firstname.location", 0)},
                {"name": "firstname.lastname.dept", "example": "john.smith.sales@company.com", "weight": tech_patterns.get("firstname.lastname.dept", 0)},
                {"name": "firstname.lastname.location", "example": "john.smith.nyc@company.com", "weight": tech_patterns.get("firstname.lastname.location", 0)}
            ]
        },
        "G_international_multilingual": {
            "description": "International/Multilingual (6 patterns)",
            "patterns": [
                {"name": "f.lastname", "example": "j.smith@company.com", "weight": tech_patterns.get("f.lastname", 0)},
                {"name": "fn.lastname", "example": "jo.smith@company.com", "weight": tech_patterns.get("fn.lastname", 0)},
                {"name": "firstname.l", "example": "john.s@company.com", "weight": tech_patterns.get("firstname.l", 0)},
                {"name": "lastname.fn", "example": "smith.jo@company.com", "weight": tech_patterns.get("lastname.fn", 0)},
                {"name": "firstname.x.lastname", "example": "john.x.smith@company.com", "weight": tech_patterns.get("firstname.x.lastname", 0)},
                {"name": "transliteratedfirstname.lastname", "example": "john.smith@company.com", "weight": tech_patterns.get("transliteratedfirstname.lastname", 0)}
            ]
        }
    }
    
    # Calculate totals
    total_patterns = sum(len(category["patterns"]) for category in pattern_categories.values())
    implemented_patterns = len(tech_patterns)
    
    return {
        "message": "🚀 ALL EMAIL PATTERNS - Complete Reference",
        "summary": {
            "total_patterns_shown": total_patterns,
            "total_patterns_implemented": implemented_patterns,
            "pattern_categories": len(pattern_categories),
            "coverage": f"{implemented_patterns}/{total_patterns}"
        },
        "pattern_categories": pattern_categories,
        "usage_note": "Use GET /patterns/demo to see live examples with real names"
    }

@app.get("/patterns/demo")
async def get_pattern_demo():
    """
    🧪 Live demo of patterns with real name examples across different industries
    """
    demo_cases = [
        {"firstName": "Sarah", "lastName": "Johnson", "companyDomain": "harvard.edu", "companyIndustry": "Education", "label": "🎓 University"},
        {"firstName": "Alexander", "lastName": "Chen", "companyDomain": "techstartup.io", "companyIndustry": "Technology", "label": "💻 Tech Startup"},
        {"firstName": "Elizabeth", "lastName": "Williams", "companyDomain": "goldmansachs.com", "companyIndustry": "Finance", "label": "💰 Finance"},
        {"firstName": "Michael", "lastName": "Rodriguez", "companyDomain": "government.gov", "companyIndustry": "Government", "label": "🏛️ Government"}
    ]
    
    results = []
    
    for case in demo_cases:
        result = email_generator.process_lead_data(case)
        candidates = result.get('emailCandidates', [])
        
        results.append({
            "scenario": f"{case['label']}: {case['firstName']} {case['lastName']} @ {case['companyDomain']}",
            "industry": case['companyIndustry'],
            "total_candidates": len(candidates),
            "top_recommendation": {
                "email": result['generatedEmail'],
                "confidence": result['emailConfidence'],
                "pattern": result['emailPattern'],
                "reasoning": result['emailReasoning']
            },
            "top_10_candidates": [
                {
                    "rank": i+1,
                    "email": c['email'],
                    "pattern": c['pattern'],
                    "confidence": c['confidence']
                }
                for i, c in enumerate(candidates[:10])
            ]
        })
    
    return {
        "message": "🧪 Live Pattern Demo - Real Examples Across Industries",
        "demo_results": results,
        "note": "These are real examples showing how patterns perform differently across industries and domains"
    }

@app.get("/patterns/count")
async def get_pattern_count():
    """
    📊 Quick pattern count summary
    """
    tech_patterns = email_generator.pattern_weights.get('tech', {})
    
    return {
        "total_patterns_implemented": len(tech_patterns),
        "pattern_names": sorted(list(tech_patterns.keys())),
        "message": f"✅ {len(tech_patterns)} email patterns are active and generating candidates"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )