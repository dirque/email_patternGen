#!/usr/bin/env python3
"""
Quick configuration script for email validation

Run this script to easily configure your email validation provider
"""

import requests
import json
import sys

def configure_validation():
    """Interactive configuration setup"""
    
    print("🔧 EMAIL VALIDATION SETUP")
    print("="*40)
    
    base_url = input("API URL (default: http://localhost:8000): ").strip() or "http://localhost:8000"
    
    print("\nSupported providers:")
    print("1. Hunter.io")
    print("2. ZeroBounce")
    
    provider_choice = input("Choose provider (1 or 2): ").strip()
    
    if provider_choice == "1":
        provider = "hunter_io"
        print("Selected: Hunter.io")
    elif provider_choice == "2": 
        provider = "zerobounce"
        print("Selected: ZeroBounce")
    else:
        print("Invalid choice")
        return
    
    api_key = input(f"Enter your {provider} API key: ").strip()
    
    if not api_key:
        print("API key is required")
        return
    
    print("\nValidation strategies:")
    print("1. Conservative - Top 10 patterns (fastest)")
    print("2. Balanced - Top 20 patterns (recommended)")
    print("3. Comprehensive - All 50 patterns (slowest, most thorough)")
    print("4. Fast - Top 5 patterns (quickest)")
    print("5. Custom - Configure your own settings")
    
    strategy_choice = input("Choose strategy (1-5): ").strip()
    
    strategy_map = {
        "1": "conservative",
        "2": "balanced", 
        "3": "comprehensive",
        "4": "fast"
    }
    
    if strategy_choice in strategy_map:
        strategy = strategy_map[strategy_choice]
        config_data = {
            "provider": provider,
            "api_key": api_key,
            "strategy": strategy
        }
    elif strategy_choice == "5":
        validate_top_n = int(input("Number of top patterns to validate (1-50): ") or "15")
        timeout = int(input("Timeout seconds (default 5): ") or "5")
        concurrent = int(input("Concurrent requests (default 3): ") or "3")
        
        config_data = {
            "provider": provider,
            "api_key": api_key,
            "custom_config": {
                "validate_top_n": min(50, max(1, validate_top_n)),
                "validate_all": False,
                "timeout_seconds": timeout,
                "concurrent_requests": concurrent,
                "cache_results": True
            }
        }
    else:
        print("Invalid strategy choice")
        return
    
    print(f"\n🚀 Configuring {provider} validation...")
    
    try:
        response = requests.post(
            f"{base_url}/validation/configure",
            json=config_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Configuration successful!")
            print(f"Strategy: {result.get('strategy', 'custom')}")
            print(f"Config: {json.dumps(result.get('config', {}), indent=2)}")
            
            # Test with a sample email
            test_validation = input("\nTest with sample email? (y/n): ").strip().lower()
            if test_validation == "y":
                test_email = input("Enter test email: ").strip()
                if test_email:
                    test_data = {"emails": [test_email]}
                    test_response = requests.post(
                        f"{base_url}/validation/test",
                        json=test_data
                    )
                    if test_response.status_code == 200:
                        test_result = test_response.json()
                        print("🧪 Test result:")
                        print(json.dumps(test_result, indent=2))
                    else:
                        print(f"Test failed: {test_response.text}")
        else:
            print(f"❌ Configuration failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("Make sure the API server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def quick_hunter_setup():
    """Quick Hunter.io setup with balanced strategy"""
    api_key = sys.argv[1] if len(sys.argv) > 1 else input("Hunter.io API key: ")
    
    config_data = {
        "provider": "hunter_io",
        "api_key": api_key,
        "strategy": "balanced"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/validation/configure",
            json=config_data
        )
        print("Hunter.io configured:", response.json())
    except Exception as e:
        print("Error:", e)

def quick_zerobounce_setup():
    """Quick ZeroBounce setup with balanced strategy"""
    api_key = sys.argv[1] if len(sys.argv) > 1 else input("ZeroBounce API key: ")
    
    config_data = {
        "provider": "zerobounce",
        "api_key": api_key,
        "strategy": "balanced"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/validation/configure",
            json=config_data
        )
        print("ZeroBounce configured:", response.json())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        if sys.argv[1] == "hunter":
            quick_hunter_setup()
        elif sys.argv[1] == "zerobounce":
            quick_zerobounce_setup()
        else:
            print("Usage: python validation_config.py [hunter|zerobounce] [api_key]")
    else:
        configure_validation()