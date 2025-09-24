"""
EmailListVerify Provider Integration for Email Validation System

This adds EmailListVerify as a validation provider to your existing system.
Simply copy this code into your app/services/email_validator.py file.
"""

import time
import asyncio
import aiohttp
from .email_validator import ValidationProvider, ValidationResult, ValidationStatus

class EmailListVerify_Provider(ValidationProvider):
    """EmailListVerify email validation API provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://apps.emaillistverify.com/api/verifyEmail"
    
    def get_provider_name(self) -> str:
        return "emaillistverify"
    
    async def validate_email(self, email: str, session: aiohttp.ClientSession) -> ValidationResult:
        start_time = time.time()
        
        try:
            params = {
                'secret': self.api_key,
                'email': email
            }
            
            async with session.get(self.base_url, params=params) as response:
                response_time = int((time.time() - start_time) * 1000)
                
                if response.status != 200:
                    return ValidationResult(
                        email=email,
                        status=ValidationStatus.ERROR,
                        confidence=0.0,
                        deliverable=False,
                        catch_all=False,
                        disposable=False,
                        role_account=False,
                        free_provider=False,
                        response_time_ms=response_time,
                        provider=self.get_provider_name(),
                        error_message=f"HTTP {response.status}"
                    )
                
                # EmailListVerify returns plain text, not JSON
                result_text = (await response.text()).strip().lower()
                
                # Parse EmailListVerify response
                # Possible responses: ok, failed, unknown, incorrect, key_not_valid, missing_parameters
                if result_text == "ok":
                    status = ValidationStatus.VALID
                    confidence = 0.9
                    deliverable = True
                elif result_text == "failed":
                    status = ValidationStatus.INVALID
                    confidence = 0.9
                    deliverable = False
                elif result_text == "unknown":
                    status = ValidationStatus.UNKNOWN
                    confidence = 0.1
                    deliverable = False
                elif result_text == "incorrect":
                    status = ValidationStatus.INVALID
                    confidence = 0.9
                    deliverable = False
                elif result_text in ["key_not_valid", "missing_parameters"]:
                    status = ValidationStatus.ERROR
                    confidence = 0.0
                    deliverable = False
                else:
                    # Unexpected response
                    status = ValidationStatus.UNKNOWN
                    confidence = 0.0
                    deliverable = False
                
                return ValidationResult(
                    email=email,
                    status=status,
                    confidence=confidence,
                    deliverable=deliverable,
                    catch_all=False,  # EmailListVerify doesn't provide this detail
                    disposable=False,  # EmailListVerify doesn't provide this detail
                    role_account=False,  # EmailListVerify doesn't provide this detail
                    free_provider=False,  # EmailListVerify doesn't provide this detail
                    response_time_ms=response_time,
                    provider=self.get_provider_name(),
                    raw_response={"result": result_text}
                )
                
        except asyncio.TimeoutError:
            return ValidationResult(
                email=email,
                status=ValidationStatus.TIMEOUT,
                confidence=0.0,
                deliverable=False,
                catch_all=False,
                disposable=False,
                role_account=False,
                free_provider=False,
                response_time_ms=int((time.time() - start_time) * 1000),
                provider=self.get_provider_name(),
                error_message="Request timeout"
            )
        except Exception as e:
            return ValidationResult(
                email=email,
                status=ValidationStatus.ERROR,
                confidence=0.0,
                deliverable=False,
                catch_all=False,
                disposable=False,
                role_account=False,
                free_provider=False,
                response_time_ms=int((time.time() - start_time) * 1000),
                provider=self.get_provider_name(),
                error_message=str(e)
            )

# Quick test function
async def test_emaillistverify(api_key: str, test_email: str = "test@gmail.com"):
    """Test EmailListVerify integration"""
    import aiohttp
    
    provider = EmailListVerify_Provider(api_key)
    
    async with aiohttp.ClientSession() as session:
        result = await provider.validate_email(test_email, session)
        
        print(f"✅ EmailListVerify Test Results:")
        print(f"   📧 Email: {result.email}")
        print(f"   📊 Status: {result.status.value}")
        print(f"   🎯 Deliverable: {result.deliverable}")
        print(f"   ⏱️  Response Time: {result.response_time_ms}ms")
        print(f"   🔧 Raw Response: {result.raw_response}")
        
        if result.error_message:
            print(f"   ❌ Error: {result.error_message}")
        
        return result

if __name__ == "__main__":
    # Quick test
    api_key = input("Enter your EmailListVerify API key: ")
    test_email = input("Enter email to test (default: test@gmail.com): ") or "test@gmail.com"
    
    asyncio.run(test_emaillistverify(api_key, test_email))