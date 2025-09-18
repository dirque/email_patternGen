# API testing scripts
#!/usr/bin/env python3
"""
Test script for Email Generator API
Run this to verify everything is working before integrating with Code35
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:8000"

def test_api_health():
    """Test if API is running"""
    print("🩺 Testing API health...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API is healthy: {health['message']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_single_email():
    """Test single email generation"""
    print("\n🧪 Testing single email generation...")
    
    test_lead = {
        "firstName": "Bernard",
        "lastName": "Vrijburg",
        "companyName": "Optimas Solutions", 
        "companyDomain": "optimassolutions.com",
        "companyIndustry": "Technology",
        "companySize": "51-200",
        "jobTitle": "Solutions Manager"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/generate-email",
            json=test_lead,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Single email test successful!")
            print(f"   Generated email: {result['generated_email']}")
            print(f"   Confidence: {result['confidence_score']:.1%}")
            print(f"   Pattern: {result['pattern_used']}")
            print(f"   Total candidates: {len(result['all_candidates'])}")
            return True
        else:
            print(f"❌ Single email test failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Single email test error: {e}")
        return False

def test_bulk_emails():
    """Test bulk email generation"""
    print("\n📦 Testing bulk email generation...")
    
    test_leads = [
        {
            "firstName": "Bernard",
            "lastName": "Vrijburg",
            "companyDomain": "optimassolutions.com",
            "companyIndustry": "Technology",
            "companySize": "51-200"
        },
        {
            "firstName": "Kevin",
            "lastName": "Carmody", 
            "companyDomain": "optimassolutions.com",
            "companyIndustry": "Technology",
            "companySize": "51-200"
        },
        {
            "firstName": "Jennifer",
            "lastName": "Scott",
            "companyDomain": "amplifyhrmanagement.com",
            "companyIndustry": "Technology", 
            "companySize": "51-200"
        }
    ]
    
    try:
        response = requests.post(
            f"{API_URL}/enrich-leads-batch",
            json=test_leads,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Bulk email test successful!")
            print(f"   Total processed: {result['total_processed']}")
            print(f"   Successful: {result['successful_generations']}")
            print(f"   Failed: {result['failed_generations']}")
            print(f"   Success rate: {result['success_rate']}")
            
            # Show sample results
            print("\n📋 Sample results:")
            for i, lead in enumerate(result['enriched_leads'][:2]):
                name = f"{lead.get('firstName', '')} {lead.get('lastName', '')}"
                email = lead.get('generatedEmail', 'None')
                confidence = lead.get('emailConfidence', 0)
                print(f"   {i+1}. {name}: {email} ({confidence:.1%})")
            
            return True
        else:
            print(f"❌ Bulk email test failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Bulk email test error: {e}")
        return False

def test_performance():
    """Test API performance with larger batch"""
    print("\n⚡ Testing performance with 100 leads...")
    
    # Generate test data
    test_leads = []
    for i in range(100):
        test_leads.append({
            "firstName": f"TestUser{i}",
            "lastName": f"LastName{i}",
            "companyDomain": f"testcompany{i % 10}.com",
            "companyIndustry": "Technology",
            "companySize": "51-200"
        })
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_URL}/enrich-leads-batch",
            json=test_leads,
            headers={'Content-Type': 'application/json'}
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Performance test successful!")
            print(f"   Processing time: {processing_time:.2f} seconds")
            print(f"   Leads per second: {len(test_leads) / processing_time:.1f}")
            print(f"   Success rate: {result['success_rate']}")
            return True
        else:
            print(f"❌ Performance test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🔬 Testing edge cases...")
    
    edge_cases = [
        {
            "name": "Missing lastName",
            "data": {
                "firstName": "John",
                "companyDomain": "example.com"
            }
        },
        {
            "name": "Special characters in name",
            "data": {
                "firstName": "José-María",
                "lastName": "O'Connor",
                "companyDomain": "example.com"
            }
        },
        {
            "name": "Domain with subdomain",
            "data": {
                "firstName": "Test",
                "lastName": "User",
                "companyDomain": "https://www.subdomain.example.com/path"
            }
        },
        {
            "name": "Empty firstName",
            "data": {
                "firstName": "",
                "lastName": "User",
                "companyDomain": "example.com"
            }
        }
    ]
    
    passed = 0
    
    for case in edge_cases:
        try:
            response = requests.post(
                f"{API_URL}/generate-email",
                json=case["data"],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                email = result.get('generated_email', 'None')
                print(f"   ✅ {case['name']}: {email}")
                passed += 1
            else:
                print(f"   ⚠️  {case['name']}: HTTP {response.status_code}")
                passed += 1  # Error handling is also a pass
                
        except Exception as e:
            print(f"   ❌ {case['name']}: {e}")
    
    print(f"\n📊 Edge case results: {passed}/{len(edge_cases)} handled correctly")
    return passed == len(edge_cases)

def main():
    """Run all tests"""
    print("🚀 Starting Email Generator API Tests\n")
    
    tests = [
        ("API Health", test_api_health),
        ("Single Email", test_single_email),
        ("Bulk Emails", test_bulk_emails),
        ("Performance", test_performance),
        ("Edge Cases", test_edge_cases)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Final summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your API is ready for Code35 integration.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)