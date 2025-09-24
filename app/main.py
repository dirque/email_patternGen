from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import logging
from datetime import datetime

from .services.email_generator import EnhancedEmailPatternGenerator
from .services.email_validator import (
    EmailValidationService, ValidationConfig, ValidationResult,
    Hunter_io_Provider, ZeroBounce_Provider, EmailListVerify_Provider, VALIDATION_STRATEGIES
)
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

# Initialize email validation service (configured but no providers yet)
validation_service = EmailValidationService()
validation_enabled = False  # Will be enabled when providers are added

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
            "validation_config": "/validation/config",
            "validation_test": "/validation/test",
            "generate_with_validation": "/generate-email-validated",
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
        "validation_enabled": validation_enabled,
        "validation_providers": len(validation_service.providers) if validation_service else 0,
        "message": f"✅ {len(tech_patterns)} email patterns are active and generating candidates"
    }

# =============== EMAIL VALIDATION ENDPOINTS ===============

@app.post("/validation/configure")
async def configure_validation(config: Dict[str, Any]):
    """
    🔧 Configure email validation providers and settings
    
    Example request body:
    {
        "provider": "hunter_io",
        "api_key": "your_api_key_here",
        "strategy": "balanced",
        "custom_config": {
            "validate_top_n": 15,
            "timeout_seconds": 5
        }
    }
    """
    global validation_enabled, validation_service
    
    try:
        provider_type = config.get("provider", "").lower()
        api_key = config.get("api_key")
        strategy = config.get("strategy", "balanced")
        custom_config = config.get("custom_config", {})
        
        if not provider_type or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Both 'provider' and 'api_key' are required"
            )
        
        # Initialize validation service with strategy
        if strategy in VALIDATION_STRATEGIES:
            validation_config = VALIDATION_STRATEGIES[strategy]
        else:
            validation_config = ValidationConfig(**custom_config)
        
        validation_service = EmailValidationService(validation_config)
        
        # Add provider
        if provider_type == "emaillistverify":
            provider = EmailListVerify_Provider(api_key)
            validation_service.add_provider(provider)
        elif provider_type == "hunter_io":
            provider = Hunter_io_Provider(api_key)
            validation_service.add_provider(provider)
        elif provider_type == "zerobounce":
            provider = ZeroBounce_Provider(api_key)
            validation_service.add_provider(provider)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported provider: {provider_type}. Supported: emaillistverify, hunter_io, zerobounce"
            )
        
        validation_enabled = True
        
        return {
            "success": True,
            "message": f"Validation configured with {provider_type} provider",
            "strategy": strategy,
            "config": {
                "validate_top_n": validation_config.validate_top_n,
                "validate_all": validation_config.validate_all,
                "timeout_seconds": validation_config.timeout_seconds,
                "concurrent_requests": validation_config.concurrent_requests
            }
        }
        
    except Exception as e:
        logger.error(f"Validation configuration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to configure validation: {str(e)}"
        )

@app.get("/validation/config")
async def get_validation_config():
    """
    📋 Get current validation configuration and available strategies
    """
    return {
        "validation_enabled": validation_enabled,
        "providers_configured": len(validation_service.providers) if validation_service else 0,
        "current_config": {
            "validate_top_n": validation_service.config.validate_top_n if validation_service else None,
            "validate_all": validation_service.config.validate_all if validation_service else None,
            "timeout_seconds": validation_service.config.timeout_seconds if validation_service else None,
            "concurrent_requests": validation_service.config.concurrent_requests if validation_service else None
        } if validation_service else None,
        "available_strategies": {
            name: {
                "validate_top_n": strategy.validate_top_n,
                "validate_all": strategy.validate_all,
                "timeout_seconds": strategy.timeout_seconds,
                "concurrent_requests": strategy.concurrent_requests,
                "description": {
                    "conservative": "Validates top 10 patterns with conservative timeouts",
                    "balanced": "Validates top 20 patterns with balanced performance",
                    "comprehensive": "Validates ALL 50 patterns (slower but complete)",
                    "fast": "Validates only top 5 patterns for quick results"
                }.get(name, "Custom strategy")
            }
            for name, strategy in VALIDATION_STRATEGIES.items()
        },
        "supported_providers": [
            {
                "name": "hunter_io",
                "description": "Hunter.io Email Verifier API",
                "features": ["deliverability", "catch_all", "disposable", "role_account"]
            },
            {
                "name": "emaillistverify",
                "description": "EmailListVerify API (Available Now!)",
                "features": ["deliverability", "basic_validation"],
                "status": "ready"
            },
            {
                "name": "zerobounce", 
                "description": "ZeroBounce Email Validation API",
                "features": ["deliverability", "catch_all", "spam_trap", "abuse"],
                "status": "available"
            }
        ]
    }

@app.post("/validation/test")
async def test_validation(request: Dict[str, Any]):
    """
    🧪 Test email validation with sample emails
    
    Example request:
    {
        "emails": ["john.doe@company.com", "jane.smith@startup.io"],
        "use_top_n_only": false
    }
    """
    if not validation_enabled:
        raise HTTPException(
            status_code=400,
            detail="Email validation not configured. Use POST /validation/configure first."
        )
    
    emails = request.get("emails", [])
    use_top_n = request.get("use_top_n_only", True)
    
    if not emails:
        raise HTTPException(
            status_code=400,
            detail="Please provide 'emails' array with email addresses to test"
        )
    
    try:
        # Create mock email candidates for validation
        from .services.email_generator import EmailCandidate
        mock_candidates = [
            EmailCandidate(email=email, pattern="test_pattern", confidence_score=0.8, reasoning="Test email")
            for email in emails
        ]
        
        # Validate emails
        validation_results = await validation_service.validate_emails(mock_candidates, use_top_n=use_top_n)
        summary = validation_service.get_validation_summary(validation_results)
        
        # Format results
        formatted_results = []
        for email, result in validation_results.items():
            formatted_results.append({
                "email": result.email,
                "status": result.status.value,
                "confidence": result.confidence,
                "deliverable": result.deliverable,
                "catch_all": result.catch_all,
                "disposable": result.disposable,
                "role_account": result.role_account,
                "free_provider": result.free_provider,
                "response_time_ms": result.response_time_ms,
                "provider": result.provider,
                "error_message": result.error_message
            })
        
        return {
            "success": True,
            "validation_summary": summary,
            "results": formatted_results,
            "test_info": {
                "emails_tested": len(emails),
                "validation_strategy": "top_n" if use_top_n else "all",
                "provider_used": validation_service.providers[0].get_provider_name() if validation_service.providers else "none"
            }
        }
        
    except Exception as e:
        logger.error(f"Validation test error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation test failed: {str(e)}"
        )

@app.post("/generate-email-validated", response_model=Dict[str, Any])
async def generate_email_with_validation(lead: LeadInput, validation_params: Dict[str, Any] = None):
    """
    🚀 Generate email patterns AND validate them using external API
    
    This is the SUPER LOOP you wanted - generates all patterns then validates top N or all
    
    Example request body:
    {
        "firstName": "John",
        "lastName": "Doe", 
        "companyDomain": "company.com",
        "companyIndustry": "Technology"
    }
    
    Query params or validation_params:
    - validate_top_n: true (default) - validate only top ranked patterns
    - validate_all: false (default) - set true to validate all 50 patterns
    """
    if not validation_enabled:
        raise HTTPException(
            status_code=400,
            detail="Email validation not configured. Use POST /validation/configure first to set up API provider."
        )
    
    try:
        # Step 1: Generate all email patterns (original 50-pattern generation)
        logger.info(f"Generating and validating email for {lead.firstName} {lead.lastName or ''}")
        
        lead_data = lead.dict()
        generation_result = email_generator.process_lead_data(lead_data)
        email_candidates = generation_result.get('emailCandidates', [])
        
        if not email_candidates:
            raise HTTPException(
                status_code=500,
                detail="No email patterns could be generated for this lead"
            )
        
        # Step 2: Validate emails using the configured strategy
        validation_params = validation_params or {}
        use_top_n = not validation_params.get("validate_all", False)
        
        logger.info(f"Starting validation for {len(email_candidates)} generated patterns")
        
        # Convert to validation format
        from .services.email_generator import EmailCandidate as GenEmailCandidate
        validation_candidates = [
            GenEmailCandidate(
                email=candidate['email'],
                pattern=candidate['pattern'], 
                confidence_score=candidate['confidence'],
                reasoning=candidate.get('reasoning', '')
            )
            for candidate in email_candidates
        ]
        
        # Perform validation
        validation_results = await validation_service.validate_emails(validation_candidates, use_top_n=use_top_n)
        validation_summary = validation_service.get_validation_summary(validation_results)
        
        # Step 3: Merge generation + validation results
        enhanced_candidates = []
        for candidate in email_candidates:
            email = candidate['email']
            validation_result = validation_results.get(email)
            
            enhanced_candidate = {
                **candidate,
                "validation": {
                    "validated": validation_result is not None,
                    "status": validation_result.status.value if validation_result else "not_validated",
                    "deliverable": validation_result.deliverable if validation_result else None,
                    "confidence_boost": 0.0,
                    "validation_confidence": validation_result.confidence if validation_result else 0.0,
                    "catch_all": validation_result.catch_all if validation_result else None,
                    "disposable": validation_result.disposable if validation_result else None,
                    "role_account": validation_result.role_account if validation_result else None,
                    "response_time_ms": validation_result.response_time_ms if validation_result else 0
                } if validation_result else {
                    "validated": False,
                    "status": "not_validated", 
                    "deliverable": None,
                    "confidence_boost": 0.0
                }
            }
            
            # Boost confidence for validated deliverable emails
            if validation_result and validation_result.deliverable:
                boost = 0.2 if validation_result.status.value == "valid" else 0.1
                enhanced_candidate["confidence"] = min(1.0, candidate["confidence"] + boost)
                enhanced_candidate["validation"]["confidence_boost"] = boost
            
            enhanced_candidates.append(enhanced_candidate)
        
        # Re-sort by enhanced confidence (after validation boost)
        enhanced_candidates.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Update top recommendation based on validation
        top_candidate = enhanced_candidates[0]
        
        return {
            "success": True,
            "lead_data": generation_result,
            "generated_email": top_candidate["email"],
            "confidence_score": top_candidate["confidence"],
            "pattern_used": top_candidate["pattern"],
            "reasoning": top_candidate.get("reasoning", ""),
            "validation_enhanced": True,
            "validation_summary": validation_summary,
            "all_candidates": enhanced_candidates,
            "validation_info": {
                "total_patterns_generated": len(email_candidates),
                "patterns_validated": len(validation_results),
                "validation_strategy": "all_patterns" if validation_params.get("validate_all") else f"top_{validation_service.config.validate_top_n}",
                "deliverable_found": any(r.deliverable for r in validation_results.values()),
                "provider_used": validation_service.providers[0].get_provider_name() if validation_service.providers else "unknown"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in validated email generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate and validate email: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )