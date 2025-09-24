#!/usr/bin/env python3
"""
Email Validation System Examples and Usage Guide

This demonstrates the flexible email validation system that can:
1. Validate all 50 patterns OR just top N patterns (configurable)
2. Support multiple validation API providers
3. Integrate validation results back into confidence scoring

VALIDATION STRATEGIES:
- Conservative: Top 10 patterns, fast timeouts (good for quick checks)
- Balanced: Top 20 patterns, balanced performance (recommended default)
- Comprehensive: All 50 patterns, thorough but slower (best accuracy)
- Fast: Top 5 patterns, minimal latency (basic validation)
"""

import asyncio
import json
from typing import Dict, List
import requests

class EmailValidationDemo:
    """Demo class showing different validation scenarios"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def setup_hunter_io_validation(self, api_key: str, strategy: str = "balanced"):
        """
        Configure Hunter.io as validation provider
        
        Strategies:
        - conservative: Validate top 10 patterns
        - balanced: Validate top 20 patterns  
        - comprehensive: Validate all 50 patterns
        - fast: Validate top 5 patterns
        """
        config_data = {
            "provider": "hunter_io",
            "api_key": api_key,
            "strategy": strategy
        }
        
        response = requests.post(
            f"{self.base_url}/validation/configure",
            json=config_data
        )
        
        print(f"🔧 Hunter.io Configuration ({strategy}):")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    
    def setup_zerobounce_validation(self, api_key: str, strategy: str = "balanced"):
        """Configure ZeroBounce as validation provider"""
        config_data = {
            "provider": "zerobounce", 
            "api_key": api_key,
            "strategy": strategy
        }
        
        response = requests.post(
            f"{self.base_url}/validation/configure",
            json=config_data
        )
        
        print(f"🔧 ZeroBounce Configuration ({strategy}):")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    
    def setup_custom_validation(self, api_key: str, provider: str, validate_top_n: int = 15):
        """Configure custom validation settings"""
        config_data = {
            "provider": provider,
            "api_key": api_key,
            "custom_config": {
                "validate_top_n": validate_top_n,
                "validate_all": False,
                "timeout_seconds": 7,
                "concurrent_requests": 4,
                "cache_results": True
            }
        }
        
        response = requests.post(
            f"{self.base_url}/validation/configure",
            json=config_data
        )
        
        print(f"🔧 Custom Configuration (Top {validate_top_n}):")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    
    def test_validation_api(self, test_emails: List[str]):
        """Test the validation API with sample emails"""
        test_data = {
            "emails": test_emails,
            "use_top_n_only": False  # Test all provided emails
        }
        
        response = requests.post(
            f"{self.base_url}/validation/test",
            json=test_data
        )
        
        print("🧪 Validation Test Results:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    
    def generate_with_validation_top_n(self, lead_data: Dict):
        """Generate emails and validate top N patterns (faster)"""
        response = requests.post(
            f"{self.base_url}/generate-email-validated",
            json=lead_data
        )
        
        result = response.json()
        
        print(f"🚀 Email Generation + Top-N Validation for {lead_data['firstName']} {lead_data['lastName']}:")
        print(f"   📧 Best Email: {result['generated_email']}")
        print(f"   📊 Confidence: {result['confidence_score']:.3f}")
        print(f"   🔍 Pattern: {result['pattern_used']}")
        print(f"   ✅ Validation: {result['validation_info']['patterns_validated']} patterns validated")
        print(f"   📈 Strategy: {result['validation_info']['validation_strategy']}")
        
        return result
    
    def generate_with_validation_all(self, lead_data: Dict):
        """Generate emails and validate ALL 50 patterns (comprehensive)"""
        # Add validation params to request all patterns
        validation_params = {"validate_all": True}
        
        # For this endpoint, we can modify the lead data to include validation preferences
        enhanced_lead_data = {**lead_data, "validation_params": validation_params}
        
        response = requests.post(
            f"{self.base_url}/generate-email-validated",
            json=enhanced_lead_data
        )
        
        result = response.json()
        
        print(f"🔬 Email Generation + Full Validation (All 50) for {lead_data['firstName']} {lead_data['lastName']}:")
        print(f"   📧 Best Email: {result['generated_email']}")
        print(f"   📊 Confidence: {result['confidence_score']:.3f}")
        print(f"   🔍 Pattern: {result['pattern_used']}")
        print(f"   ✅ Validation: {result['validation_info']['patterns_validated']} patterns validated")
        print(f"   📈 Strategy: {result['validation_info']['validation_strategy']}")
        
        return result
    
    def compare_strategies(self, lead_data: Dict):
        """Compare different validation strategies for the same lead"""
        strategies = ["conservative", "balanced", "comprehensive", "fast"]
        results = {}
        
        for strategy in strategies:
            print(f"\n{'='*20} {strategy.upper()} STRATEGY {'='*20}")
            
            # Would need to reconfigure for each strategy in real usage
            # This is just for demonstration
            try:
                result = self.generate_with_validation_top_n(lead_data)
                results[strategy] = {
                    "email": result["generated_email"],
                    "confidence": result["confidence_score"],
                    "patterns_validated": result["validation_info"]["patterns_validated"],
                    "validation_time": result["validation_summary"].get("avg_response_time_ms", 0)
                }
            except Exception as e:
                print(f"   ❌ Error with {strategy}: {e}")
                results[strategy] = {"error": str(e)}
        
        return results

def main():
    """
    Comprehensive demo of the email validation system
    
    This shows the "super loop" functionality:
    1. Generate all 50 email patterns
    2. Validate either top N or all patterns via external API
    3. Re-rank results based on validation feedback
    4. Return enhanced candidates with validation data
    """
    
    print("🚀 EMAIL VALIDATION SYSTEM DEMO")
    print("="*50)
    
    # Initialize demo
    demo = EmailValidationDemo()
    
    # Sample leads for testing
    test_leads = [
        {
            "firstName": "Sarah",
            "lastName": "Johnson", 
            "companyDomain": "harvard.edu",
            "companyIndustry": "Education"
        },
        {
            "firstName": "Alex", 
            "lastName": "Chen",
            "companyDomain": "startup.io",
            "companyIndustry": "Technology"
        },
        {
            "firstName": "Maria",
            "lastName": "Rodriguez",
            "companyDomain": "jpmorgan.com", 
            "companyIndustry": "Finance"
        }
    ]
    
    print("\n1. 📋 CHECK VALIDATION CONFIG")
    try:
        config_response = requests.get("http://localhost:8000/validation/config")
        config = config_response.json()
        print(f"   Validation Enabled: {config['validation_enabled']}")
        print(f"   Providers: {config['providers_configured']}")
        print("   Available Strategies:")
        for name, details in config["available_strategies"].items():
            print(f"     - {name}: Validate {'all' if details['validate_all'] else f'top {details['validate_top_n']}'} patterns")
    except Exception as e:
        print(f"   ⚠️  API not running or validation not configured: {e}")
    
    print("\n2. 🔧 SETUP VALIDATION (EXAMPLE)")
    print("   # To setup Hunter.io validation:")
    print("   demo.setup_hunter_io_validation('your_hunter_api_key', 'balanced')")
    print("   ")
    print("   # To setup ZeroBounce validation:")
    print("   demo.setup_zerobounce_validation('your_zerobounce_api_key', 'comprehensive')")
    print("   ")
    print("   # To setup custom validation (validate top 15 patterns):")
    print("   demo.setup_custom_validation('your_api_key', 'hunter_io', validate_top_n=15)")
    
    print("\n3. 🧪 VALIDATION STRATEGIES")
    print("   CONSERVATIVE: Top 10 patterns, 3sec timeout (fastest)")
    print("   BALANCED:     Top 20 patterns, 5sec timeout (recommended)")  
    print("   COMPREHENSIVE: All 50 patterns, 10sec timeout (most thorough)")
    print("   FAST:         Top 5 patterns, 2sec timeout (quickest)")
    print("   CUSTOM:       Configure your own validate_top_n and timeouts")
    
    print("\n4. 🚀 USAGE EXAMPLES")
    print("   # Generate + validate top N patterns (faster, recommended):")
    print("   demo.generate_with_validation_top_n(lead_data)")
    print("   ")
    print("   # Generate + validate ALL 50 patterns (slower, comprehensive):")
    print("   demo.generate_with_validation_all(lead_data)")
    
    print("\n5. 📊 WHAT YOU GET")
    print("   ✅ All 50 email patterns generated")
    print("   ✅ Top N or all patterns validated via external API")
    print("   ✅ Confidence scores boosted for deliverable emails")
    print("   ✅ Validation metadata (deliverable, catch-all, disposable, etc.)")
    print("   ✅ Performance metrics (response times, success rates)")
    print("   ✅ Re-ranked results based on validation feedback")
    
    print("\n6. 🔄 THE SUPER LOOP WORKFLOW")
    print("   1. 📧 Generate all 50 email patterns with confidence scores")
    print("   2. 🎯 Select top N patterns OR all patterns (configurable)")
    print("   3. 🌐 Validate selected patterns via external API (Hunter.io/ZeroBounce)")
    print("   4. 📈 Boost confidence for validated deliverable emails")
    print("   5. 🏆 Re-rank and return enhanced results")
    
    print("\n" + "="*50)
    print("Ready to use! Configure your validation provider and start validating!")

if __name__ == "__main__":
    main()