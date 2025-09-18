import json
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import unicodedata

@dataclass
class EmailCandidate:
    email: str
    pattern: str
    confidence_score: float
    reasoning: str

class EnhancedEmailPatternGenerator:
    """
    Enhanced email pattern generator with research-based confidence scoring
    """
    
    def __init__(self):
        self.setup_logging()
        
        # Industry to company type mapping
        self.industry_mapping = {
            'technology': 'tech',
            'software': 'tech',
            'fintech': 'fintech',
            'financial services': 'finance',
            'consulting': 'consulting',
            'healthcare': 'healthcare',
            'manufacturing': 'traditional',
            'retail': 'traditional',
            'education': 'education',
            'government': 'government'
        }
        
        # Pattern weights by company type
        self.pattern_weights = {
            'tech': {
                'firstname.lastname': 0.85,
                'firstname': 0.75,
                'firstnamelastname': 0.70,
                'f.lastname': 0.65,
                'firstname_lastname': 0.60,
                'lastname.firstname': 0.45,
                'lastname': 0.40,
                'flastname': 0.35
            },
            'fintech': {
                'firstname.lastname': 0.90,
                'firstname': 0.70,
                'f.lastname': 0.80,
                'firstnamelastname': 0.65,
                'firstname_lastname': 0.55,
                'lastname.firstname': 0.40,
                'lastname': 0.35,
                'flastname': 0.45
            },
            'finance': {
                'firstname.lastname': 0.80,
                'f.lastname': 0.85,
                'firstname': 0.60,
                'firstnamelastname': 0.55,
                'firstname_lastname': 0.50,
                'lastname.firstname': 0.45,
                'lastname': 0.40,
                'flastname': 0.50
            },
            'consulting': {
                'firstname.lastname': 0.85,
                'f.lastname': 0.75,
                'firstname': 0.70,
                'firstnamelastname': 0.60,
                'firstname_lastname': 0.55,
                'lastname.firstname': 0.40,
                'lastname': 0.35,
                'flastname': 0.45
            },
            'traditional': {
                'f.lastname': 0.80,
                'firstname.lastname': 0.75,
                'lastname.firstname': 0.70,
                'firstname': 0.60,
                'firstname_lastname': 0.55,
                'firstnamelastname': 0.50,
                'lastname': 0.45,
                'flastname': 0.55
            },
            'default': {
                'firstname.lastname': 0.75,
                'firstname': 0.65,
                'f.lastname': 0.70,
                'firstnamelastname': 0.60,
                'firstname_lastname': 0.55,
                'lastname.firstname': 0.45,
                'lastname': 0.40,
                'flastname': 0.40
            }
        }
        
        # Company size modifiers
        self.size_modifiers = {
            '1-10': 0.1,      # Startups often use informal patterns
            '11-50': 0.05,
            '51-200': 0.0,    # Baseline
            '201-500': -0.05, # More formal as size increases
            '501-1000': -0.1,
            '1000+': -0.15
        }
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def clean_name(self, name: str) -> str:
        """Clean and normalize names"""
        if not name:
            return ""
        
        # Remove accents and normalize
        name = unicodedata.normalize('NFD', name.lower())
        name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
        
        # Remove special characters and extra spaces
        name = re.sub(r'[^a-zA-Z\s]', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def extract_domain(self, domain_input: str) -> str:
        """Extract clean domain from various inputs"""
        if not domain_input:
            return ""
        
        # Remove protocol
        domain = re.sub(r'^https?://', '', domain_input.lower())
        
        # Remove www
        domain = re.sub(r'^www\.', '', domain)
        
        # Remove trailing slash and paths
        domain = domain.split('/')[0]
        
        # Remove port numbers
        domain = domain.split(':')[0]
        
        return domain.strip()
    
    def get_company_type(self, industry: str) -> str:
        """Map industry to company type"""
        if not industry:
            return 'default'
        
        industry_clean = industry.lower().strip()
        return self.industry_mapping.get(industry_clean, 'default')
    
    def calculate_domain_score(self, domain: str) -> float:
        """Calculate domain quality score"""
        if not domain:
            return 0.0
        
        score = 0.5  # Base score
        
        # Domain length factor
        if 5 <= len(domain) <= 15:
            score += 0.1
        elif len(domain) > 20:
            score -= 0.1
        
        # Common business domains
        business_domains = ['.com', '.org', '.net', '.io', '.co']
        if any(domain.endswith(bd) for bd in business_domains):
            score += 0.15
        
        # Tech-specific domains
        tech_domains = ['.io', '.co', '.tech', '.ai']
        if any(domain.endswith(td) for td in tech_domains):
            score += 0.1
        
        # Avoid suspicious patterns
        suspicious_patterns = ['temp', 'test', 'example', 'demo']
        if any(sp in domain for sp in suspicious_patterns):
            score -= 0.3
        
        return min(1.0, max(0.0, score))
    
    def calculate_name_score(self, first_name: str, last_name: str) -> float:
        """Calculate name quality score"""
        score = 0.5
        
        # Name length factors
        if first_name and 2 <= len(first_name) <= 15:
            score += 0.2
        if last_name and 2 <= len(last_name) <= 20:
            score += 0.2
        
        # Penalize very short or very long names
        if first_name and (len(first_name) < 2 or len(first_name) > 20):
            score -= 0.1
        if last_name and (len(last_name) < 2 or len(last_name) > 25):
            score -= 0.1
        
        return min(1.0, max(0.0, score))
    
    def generate_pattern_email(self, first_name: str, last_name: str, domain: str, pattern: str) -> str:
        """Generate email based on pattern"""
        if not all([first_name, domain]) or not pattern:
            return ""
        
        first_clean = self.clean_name(first_name)
        last_clean = self.clean_name(last_name) if last_name else ""
        
        patterns = {
            'firstname': f"{first_clean}@{domain}",
            'lastname': f"{last_clean}@{domain}" if last_clean else "",
            'firstname.lastname': f"{first_clean}.{last_clean}@{domain}" if last_clean else f"{first_clean}@{domain}",
            'firstname_lastname': f"{first_clean}_{last_clean}@{domain}" if last_clean else f"{first_clean}@{domain}",
            'firstnamelastname': f"{first_clean}{last_clean}@{domain}" if last_clean else f"{first_clean}@{domain}",
            'f.lastname': f"{first_clean[0] if first_clean else ''}.{last_clean}@{domain}" if last_clean else "",
            'lastname.firstname': f"{last_clean}.{first_clean}@{domain}" if last_clean else "",
            'flastname': f"{first_clean[0] if first_clean else ''}{last_clean}@{domain}" if last_clean else ""
        }
        
        return patterns.get(pattern, "")
    
    def calculate_confidence_score(self, 
                                 pattern: str,
                                 company_type: str,
                                 domain: str,
                                 first_name: str,
                                 last_name: str,
                                 company_size: str = None) -> Tuple[float, str]:
        """Calculate comprehensive confidence score"""
        
        # Base pattern score (40% weight)
        pattern_weights = self.pattern_weights.get(company_type, self.pattern_weights['default'])
        base_score = pattern_weights.get(pattern, 0.3) * 0.4
        
        # Domain quality score (25% weight)
        domain_score = self.calculate_domain_score(domain) * 0.25
        
        # Name quality score (15% weight)
        name_score = self.calculate_name_score(first_name, last_name) * 0.15
        
        # Company type bonus (10% weight)
        type_bonus = 0.1 if company_type != 'default' else 0.05
        
        # Company size modifier (10% weight)
        size_modifier = 0.0
        if company_size:
            size_modifier = self.size_modifiers.get(company_size, 0.0) * 0.1
        
        # Calculate final score
        final_score = base_score + domain_score + name_score + type_bonus + size_modifier
        
        # Reasoning
        reasoning_parts = [
            f"Pattern: {pattern} ({pattern_weights.get(pattern, 0.3):.2f})",
            f"Domain: {domain_score/0.25:.2f}",
            f"Names: {name_score/0.15:.2f}",
            f"Industry: {company_type}"
        ]
        
        if company_size:
            reasoning_parts.append(f"Size: {company_size}")
        
        reasoning = " | ".join(reasoning_parts)
        
        return min(0.99, max(0.01, final_score)), reasoning
    
    def generate_emails(self, 
                       first_name: str,
                       last_name: str,
                       company_domain: str,
                       company_industry: str = None,
                       company_size: str = None,
                       max_candidates: int = 8) -> List[EmailCandidate]:
        """
        Generate ranked email candidates
        """
        
        if not first_name or not company_domain:
            self.logger.warning(f"Missing required data: first_name='{first_name}', domain='{company_domain}'")
            return []
        
        # Clean inputs
        domain = self.extract_domain(company_domain)
        if not domain:
            self.logger.warning(f"Invalid domain: {company_domain}")
            return []
        
        company_type = self.get_company_type(company_industry)
        
        # Generate candidates for all patterns
        candidates = []
        patterns = self.pattern_weights.get(company_type, self.pattern_weights['default'])
        
        for pattern in patterns.keys():
            email = self.generate_pattern_email(first_name, last_name, domain, pattern)
            
            if email and self.is_valid_email_format(email):
                confidence, reasoning = self.calculate_confidence_score(
                    pattern, company_type, domain, first_name, last_name, company_size
                )
                
                candidates.append(EmailCandidate(
                    email=email,
                    pattern=pattern,
                    confidence_score=confidence,
                    reasoning=reasoning
                ))
        
        # Sort by confidence score and return top candidates
        candidates.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate.email not in seen:
                seen.add(candidate.email)
                unique_candidates.append(candidate)
        
        return unique_candidates[:max_candidates]
    
    def is_valid_email_format(self, email: str) -> bool:
        """Basic email format validation"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_regex, email))
    
    def process_lead_data(self, lead_data: Dict) -> Dict:
        """Process a single lead record and add email candidates"""
        
        first_name = lead_data.get('firstName', '')
        last_name = lead_data.get('lastName', '')
        company_domain = lead_data.get('companyDomain', '')
        company_industry = lead_data.get('companyIndustry', '')
        company_size = lead_data.get('companySize', '')
        
        # Generate email candidates
        candidates = self.generate_emails(
            first_name=first_name,
            last_name=last_name,
            company_domain=company_domain,
            company_industry=company_industry,
            company_size=company_size
        )
        
        # Add email data to lead record
        enriched_lead = lead_data.copy()
        
        if candidates:
            # Primary email (highest confidence)
            enriched_lead['generatedEmail'] = candidates[0].email
            enriched_lead['emailConfidence'] = round(candidates[0].confidence_score, 3)
            enriched_lead['emailPattern'] = candidates[0].pattern
            enriched_lead['emailReasoning'] = candidates[0].reasoning
            
            # All candidates for reference
            enriched_lead['emailCandidates'] = [
                {
                    'email': c.email,
                    'confidence': round(c.confidence_score, 3),
                    'pattern': c.pattern,
                    'reasoning': c.reasoning
                }
                for c in candidates
            ]
        else:
            enriched_lead['generatedEmail'] = None
            enriched_lead['emailConfidence'] = 0.0
            enriched_lead['emailPattern'] = None
            enriched_lead['emailReasoning'] = 'No valid email could be generated'
            enriched_lead['emailCandidates'] = []
        
        return enriched_lead
    
    def process_leads_batch(self, leads: List[Dict]) -> List[Dict]:
        """Process a batch of leads"""
        enriched_leads = []
        
        for lead in leads:
            try:
                enriched_lead = self.process_lead_data(lead)
                enriched_leads.append(enriched_lead)
            except Exception as e:
                self.logger.error(f"Error processing lead: {e}")
                # Return original lead with error info
                error_lead = lead.copy()
                error_lead.update({
                    'generatedEmail': None,
                    'emailConfidence': 0.0,
                    'emailPattern': None,
                    'emailReasoning': f'Error: {str(e)}',
                    'emailCandidates': []
                })
                enriched_leads.append(error_lead)
        
        return enriched_leads