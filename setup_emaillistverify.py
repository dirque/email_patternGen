#!/usr/bin/env python3
"""
Quick setup script for EmailListVerify integration
Run this after starting your local server to configure EmailListVerify validation
"""

import requests
import json
import sys

def setup_emaillistverify():
    """Setup EmailListVerify with your API key"""
    
    print("🔧 EMAILLISTVERIFY SETUP FOR LOCAL DEVELOPMENT")
    print("="*55)
    
    # Get API details
    api_key = input("📧 Enter your EmailListVerify API key: ").strip()
    
    if not api_key:
        print("❌ API key is required!")
        return
    
    base_url = input("🌐 API URL (default: http://localhost:8000): ").strip() or "http://localhost:8000"
    
    print("\n🎯 Choose validation strategy:")
    print("1. 🏃 Fast        - Top 5 patterns (quickest)")
    print("2. ⚖️  Balanced   - Top 20 patterns (recommended)")
    print("3. 🔍 Conservative - Top 10 patterns") 
    print("4. 📊 Comprehensive - All 50 patterns (slowest, most thorough)")
    print("5. ⚙️  Custom      - Choose your own settings")
    
    choice = input("\nSelect strategy (1-5, default: 2): ").strip() or "2"
    
    strategy_map = {
        "1": "fast",
        "2": "balanced",
        "3": "conservative", 
        "4": "comprehensive"
    }
    
    if choice in strategy_map:
        config_data = {
            "provider": "emaillistverify",
            "api_key": api_key,
            "strategy": strategy_map[choice]
        }
        strategy_name = strategy_map[choice]
    elif choice == "5":
        validate_top_n = int(input("🔢 Number of patterns to validate (1-50, default: 15): ") or "15")
        timeout = int(input("⏱️  Timeout seconds (default: 5): ") or "5")
        
        config_data = {
            "provider": "emaillistverify",
            "api_key": api_key,
            "custom_config": {
                "validate_top_n": min(50, max(1, validate_top_n)),
                "validate_all": False,
                "timeout_seconds": timeout,
                "concurrent_requests": 2,  # Conservative for EmailListVerify
                "cache_results": True
            }
        }
        strategy_name = f"custom (top {validate_top_n})"
    else:
        print("❌ Invalid choice, using balanced strategy")
        config_data = {
            "provider": "emaillistverify",
            "api_key": api_key,
            "strategy": "balanced"
        }
        strategy_name = "balanced"
    
    print(f"\n🚀 Configuring EmailListVerify with {strategy_name} strategy...")
    
    try:
        # Configure validation
        response = requests.post(
            f"{base_url}/validation/configure",
            json=config_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ EmailListVerify configured successfully!")
            print(f"📊 Strategy: {result.get('strategy', 'custom')}")
            print(f"⚙️  Settings: {json.dumps(result.get('config', {}), indent=2)}")
            
            # Test with a sample email
            print(f"\n🧪 Testing validation...")
            test_email = input("Enter test email (default: test@gmail.com): ").strip() or "test@gmail.com"
            
            test_data = {"emails": [test_email], "use_top_n_only": False}
            test_response = requests.post(
                f"{base_url}/validation/test",
                json=test_data,
                timeout=15
            )
            
            if test_response.status_code == 200:
                test_result = test_response.json()
                print("✅ Test successful!")
                
                if test_result.get("results"):
                    result = test_result["results"][0]
                    print(f"📧 Email: {result['email']}")
                    print(f"📊 Status: {result['status']}")
                    print(f"✅ Deliverable: {result['deliverable']}")
                    print(f"⏱️  Response Time: {result['response_time_ms']}ms")
                
                print(f"\n🎯 Validation Summary:")
                summary = test_result.get("validation_summary", {})
                for key, value in summary.items():
                    print(f"   {key}: {value}")
                    
            else:
                print(f"❌ Test failed: {test_response.text}")
                
        else:
            print(f"❌ Configuration failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {base_url}")
        print("   Make sure your FastAPI server is running:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print(f"\n🎉 EMAILLISTVERIFY SETUP COMPLETE!")
    print(f"   Now you can use the super loop endpoint:")
    print(f"   POST {base_url}/generate-email-validated")
    print(f"   ")
    print(f"   Example request body:")
    print(f"   {{")
    print(f"     \"firstName\": \"John\",")
    print(f"     \"lastName\": \"Doe\",")
    print(f"     \"companyDomain\": \"company.com\",")
    print(f"     \"companyIndustry\": \"Technology\"")
    print(f"   }}")
    
    return True

def quick_test():
    """Quick test of the validation system"""
    base_url = "http://localhost:8000"
    
    print("\n🧪 QUICK VALIDATION TEST")
    print("="*30)
    
    # Check if validation is configured
    try:
        config_response = requests.get(f"{base_url}/validation/config", timeout=5)
        if config_response.status_code == 200:
            config = config_response.json()
            if config.get("validation_enabled"):
                print("✅ Validation is configured and enabled!")
                print(f"   Providers: {config['providers_configured']}")
                
                # Test email generation with validation
                test_lead = {
                    "firstName": "Sarah", 
                    "lastName": "Johnson",
                    "companyDomain": "harvard.edu",
                    "companyIndustry": "Education"
                }
                
                print(f"\n🚀 Testing super loop with: {test_lead['firstName']} {test_lead['lastName']}")
                
                response = requests.post(
                    f"{base_url}/generate-email-validated",
                    json=test_lead,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Super loop test successful!")
                    print(f"📧 Best Email: {result['generated_email']}")
                    print(f"📊 Confidence: {result['confidence_score']:.3f}")
                    print(f"🔍 Pattern: {result['pattern_used']}")
                    
                    val_info = result.get('validation_info', {})
                    print(f"✅ Validated: {val_info.get('patterns_validated', 0)} patterns")
                    print(f"📈 Strategy: {val_info.get('validation_strategy', 'unknown')}")
                    
                else:
                    print(f"❌ Super loop test failed: {response.text}")
            else:
                print("⚠️  Validation not enabled. Run setup first.")
        else:
            print("❌ Cannot check validation config")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            quick_test()
        elif sys.argv[1] == "setup":
            setup_emaillistverify()
        else:
            print("Usage: python setup_emaillistverify.py [setup|test]")
    else:
        # Interactive mode
        print("1. Setup EmailListVerify")
        print("2. Quick test validation")
        choice = input("Choose (1 or 2): ").strip()
        
        if choice == "1":
            setup_emaillistverify()
        elif choice == "2":
            quick_test()
        else:
            setup_emaillistverify()  # Default to setup