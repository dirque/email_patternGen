import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ValidationStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    RISKY = "risky"
    UNKNOWN = "unknown"
    TIMEOUT = "timeout"
    ERROR = "error"

@dataclass
class ValidationResult:
    email: str
    status: ValidationStatus
    confidence: float
    deliverable: bool
    catch_all: bool
    disposable: bool
    role_account: bool
    free_provider: bool
    response_time_ms: int
    provider: str
    raw_response: Dict = None
    error_message: str = None

@dataclass
class ValidationConfig:
    validate_top_n: int = 15  # Default: validate top 15 patterns
    validate_all: bool = False  # Set to True to validate all 50
    timeout_seconds: int = 5
    concurrent_requests: int = 3
    retry_attempts: int = 2
    cache_results: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour cache

class ValidationProvider(ABC):
    """Abstract base class for email validation providers"""
    
    @abstractmethod
    async def validate_email(self, email: str, session: aiohttp.ClientSession) -> ValidationResult:
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        pass

class Hunter_io_Provider(ValidationProvider):
    """Hunter.io email verification API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hunter.io/v2/email-verifier"
    
    def get_provider_name(self) -> str:
        return "hunter_io"
    
    async def validate_email(self, email: str, session: aiohttp.ClientSession) -> ValidationResult:
        start_time = time.time()
        
        try:
            params = {
                'email': email,
                'api_key': self.api_key
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
                
                data = await response.json()
                result_data = data.get('data', {})
                
                # Parse Hunter.io response
                status_map = {
                    'valid': ValidationStatus.VALID,
                    'invalid': ValidationStatus.INVALID,
                    'risky': ValidationStatus.RISKY,
                    'unknown': ValidationStatus.UNKNOWN
                }
                
                status = status_map.get(result_data.get('result'), ValidationStatus.UNKNOWN)
                
                return ValidationResult(
                    email=email,
                    status=status,
                    confidence=result_data.get('confidence', 0) / 100.0,  # Convert to 0-1 scale
                    deliverable=result_data.get('result') == 'valid',
                    catch_all=result_data.get('accept_all', False),
                    disposable=result_data.get('disposable', False),
                    role_account=result_data.get('role', False),
                    free_provider=result_data.get('webmail', False),
                    response_time_ms=response_time,
                    provider=self.get_provider_name(),
                    raw_response=result_data
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

class ZeroBounce_Provider(ValidationProvider):
    """ZeroBounce email validation API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.zerobounce.net/v2/validate"
    
    def get_provider_name(self) -> str:
        return "zerobounce"
    
    async def validate_email(self, email: str, session: aiohttp.ClientSession) -> ValidationResult:
        start_time = time.time()
        
        try:
            params = {
                'api_key': self.api_key,
                'email': email,
                'ip_address': ''  # Optional
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
                
                data = await response.json()
                
                # Parse ZeroBounce response
                status_map = {
                    'valid': ValidationStatus.VALID,
                    'invalid': ValidationStatus.INVALID,
                    'catch-all': ValidationStatus.RISKY,
                    'unknown': ValidationStatus.UNKNOWN,
                    'spamtrap': ValidationStatus.INVALID,
                    'abuse': ValidationStatus.INVALID,
                    'do_not_mail': ValidationStatus.INVALID
                }
                
                zb_status = data.get('status', 'unknown')
                status = status_map.get(zb_status, ValidationStatus.UNKNOWN)
                
                return ValidationResult(
                    email=email,
                    status=status,
                    confidence=0.9 if status == ValidationStatus.VALID else 0.1,
                    deliverable=zb_status == 'valid',
                    catch_all=zb_status == 'catch-all',
                    disposable=data.get('sub_status') == 'disposable',
                    role_account=data.get('sub_status') == 'role_based',
                    free_provider=data.get('free_email', False),
                    response_time_ms=response_time,
                    provider=self.get_provider_name(),
                    raw_response=data
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

class EmailValidationService:
    """
    Email validation service that can validate generated email patterns
    Supports multiple providers and configurable validation strategies
    """
    
    def __init__(self, config: ValidationConfig = None):
        self.config = config or ValidationConfig()
        self.providers: List[ValidationProvider] = []
        self.cache: Dict[str, ValidationResult] = {}
        self.cache_timestamps: Dict[str, float] = {}
        
    def add_provider(self, provider: ValidationProvider):
        """Add a validation provider"""
        self.providers.append(provider)
        logger.info(f"Added validation provider: {provider.get_provider_name()}")
    
    def _is_cache_valid(self, email: str) -> bool:
        """Check if cached result is still valid"""
        if not self.config.cache_results or email not in self.cache:
            return False
        
        cache_age = time.time() - self.cache_timestamps.get(email, 0)
        return cache_age < self.config.cache_ttl_seconds
    
    def _cache_result(self, result: ValidationResult):
        """Cache validation result"""
        if self.config.cache_results:
            self.cache[result.email] = result
            self.cache_timestamps[result.email] = time.time()
    
    async def validate_emails(self, email_candidates: List, use_top_n: bool = None) -> Dict[str, ValidationResult]:
        """
        Validate email candidates with configurable strategy
        
        Args:
            email_candidates: List of EmailCandidate objects from the generator
            use_top_n: Override config to use top N validation (None uses config)
        
        Returns:
            Dictionary mapping email addresses to ValidationResult objects
        """
        if not self.providers:
            logger.warning("No validation providers configured")
            return {}
        
        # Determine validation strategy
        validate_all = self.config.validate_all if use_top_n is None else not use_top_n
        top_n = self.config.validate_top_n
        
        # Select emails to validate
        if validate_all:
            emails_to_validate = [candidate.email for candidate in email_candidates]
            logger.info(f"Validating ALL {len(emails_to_validate)} email patterns")
        else:
            # Sort by confidence score and take top N
            sorted_candidates = sorted(email_candidates, key=lambda x: x.confidence_score, reverse=True)
            emails_to_validate = [candidate.email for candidate in sorted_candidates[:top_n]]
            logger.info(f"Validating TOP {len(emails_to_validate)} email patterns (out of {len(email_candidates)})")
        
        # Check cache first
        results = {}
        emails_needing_validation = []
        
        for email in emails_to_validate:
            if self._is_cache_valid(email):
                results[email] = self.cache[email]
                logger.debug(f"Using cached result for {email}")
            else:
                emails_needing_validation.append(email)
        
        if not emails_needing_validation:
            logger.info("All emails found in cache")
            return results
        
        # Validate remaining emails
        logger.info(f"Validating {len(emails_needing_validation)} emails via API")
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        ) as session:
            # Use first available provider (could be extended to use multiple providers)
            provider = self.providers[0]
            
            # Create semaphore for concurrent requests
            semaphore = asyncio.Semaphore(self.config.concurrent_requests)
            
            async def validate_single_email(email: str) -> ValidationResult:
                async with semaphore:
                    for attempt in range(self.config.retry_attempts + 1):
                        try:
                            result = await provider.validate_email(email, session)
                            self._cache_result(result)
                            return result
                        except Exception as e:
                            if attempt == self.config.retry_attempts:
                                logger.error(f"Failed to validate {email} after {attempt + 1} attempts: {e}")
                                return ValidationResult(
                                    email=email,
                                    status=ValidationStatus.ERROR,
                                    confidence=0.0,
                                    deliverable=False,
                                    catch_all=False,
                                    disposable=False,
                                    role_account=False,
                                    free_provider=False,
                                    response_time_ms=0,
                                    provider=provider.get_provider_name(),
                                    error_message=str(e)
                                )
                            await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
            
            # Execute validation tasks
            tasks = [validate_single_email(email) for email in emails_needing_validation]
            validation_results = await asyncio.gather(*tasks)
            
            # Add to results
            for result in validation_results:
                results[result.email] = result
        
        return results
    
    def get_validation_summary(self, validation_results: Dict[str, ValidationResult]) -> Dict[str, Any]:
        """Generate a summary of validation results"""
        if not validation_results:
            return {"total": 0, "summary": "No validations performed"}
        
        total = len(validation_results)
        valid_count = sum(1 for r in validation_results.values() if r.status == ValidationStatus.VALID)
        invalid_count = sum(1 for r in validation_results.values() if r.status == ValidationStatus.INVALID)
        risky_count = sum(1 for r in validation_results.values() if r.status == ValidationStatus.RISKY)
        error_count = sum(1 for r in validation_results.values() if r.status in [ValidationStatus.ERROR, ValidationStatus.TIMEOUT])
        
        avg_confidence = sum(r.confidence for r in validation_results.values()) / total if total > 0 else 0
        avg_response_time = sum(r.response_time_ms for r in validation_results.values()) / total if total > 0 else 0
        
        deliverable_count = sum(1 for r in validation_results.values() if r.deliverable)
        
        return {
            "total_validated": total,
            "valid": valid_count,
            "invalid": invalid_count,
            "risky": risky_count,
            "errors": error_count,
            "deliverable": deliverable_count,
            "avg_confidence": round(avg_confidence, 3),
            "avg_response_time_ms": round(avg_response_time, 1),
            "validation_success_rate": round((total - error_count) / total * 100, 1) if total > 0 else 0
        }

# Example configuration for different validation strategies
VALIDATION_STRATEGIES = {
    "conservative": ValidationConfig(
        validate_top_n=10,
        validate_all=False,
        timeout_seconds=3,
        concurrent_requests=2
    ),
    "balanced": ValidationConfig(
        validate_top_n=20,
        validate_all=False,
        timeout_seconds=5,
        concurrent_requests=3
    ),
    "comprehensive": ValidationConfig(
        validate_all=True,
        timeout_seconds=10,
        concurrent_requests=5
    ),
    "fast": ValidationConfig(
        validate_top_n=5,
        validate_all=False,
        timeout_seconds=2,
        concurrent_requests=1
    )
}