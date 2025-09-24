import json
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import unicodedata
from datetime import datetime

@dataclass
class EmailCandidate:
    email: str
    pattern: str
    confidence_score: float
    reasoning: str

class EnhancedEmailPatternGenerator:
    """
    Enhanced email pattern generator with 50 research-based patterns
    
    EXPANDED FROM 8 TO 50 PATTERNS:
    - A. Basic Name Standards (10 patterns)
    - B. Extended Name + Middle Initials (8 patterns) 
    - C. Abbreviated/Shortened (10 patterns)
    - D. Numeric Variants (7 patterns)
    - E. Reversed/Surname-first (5 patterns)
    - F. Department/Location Hybrids (4 patterns)
    - G. International/Multilingual (6 patterns)
    """

    def __init__(self):
        self.setup_logging()

        # Industry to company type mapping (enhanced)
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
            'higher education': 'education',
            'university': 'education',
            'college': 'education',
            'government': 'government',
            'nonprofit': 'nonprofit'
        }

        # EXPANDED: Pattern weights for all 50 patterns across industries
        self.pattern_weights = {
            'tech': {
                # A. Basic Name Standards
                'firstname': 0.70,
                'lastname': 0.35,
                'firstname.lastname': 0.90,
                'firstname_lastname': 0.60,
                'firstname-lastname': 0.55,
                'firstinitial.lastname': 0.75,
                'firstname.lastinitial': 0.65,
                'firstinitiallastname': 0.70,
                'lastnamefirstinitial': 0.40,
                'lastname.firstname': 0.45,
                
                # B. Extended Name + Middle Initials
                'firstname.middlename.lastname': 0.40,
                'firstname.middleinitial.lastname': 0.50,
                'firstinitial.middleinitial.lastname': 0.45,
                'firstname+middlename+lastname': 0.30,
                'firstinitial+middlename+lastname': 0.25,
                'firstname.middleinitial': 0.35,
                'firstname.middleinitiallastinitial': 0.20,
                'firstname.middlename': 0.25,
                
                # C. Abbreviated/Shortened (HIGH for tech)
                'first3letterslastname': 0.65,
                'first4letterslastname': 0.60,
                'firstname+last2letters': 0.55,
                'firstname+first2letterslastname': 0.50,
                'first2letterslastname': 0.60,
                'first3letterslast3letters': 0.70,
                'firstnameinitials': 0.65,
                'shortenedname.lastname': 0.55,
                'nickname.lastname': 0.60,
                'initials': 0.50,
                
                # D. Numeric Variants (MEDIUM for tech)
                'firstname.lastname1': 0.45,
                'firstname1': 0.40,
                'lastname1': 0.25,
                'firstinitiallastname1': 0.35,
                'firstname.lastname01': 0.30,
                'firstname.lastnameYY': 0.25,
                'firstnameYY': 0.20,
                
                # E. Reversed/Surname-first
                'lastname_firstname': 0.35,
                'lastname-firstname': 0.30,
                'lastnamefirstname': 0.45,
                
                # F. Department/Location Hybrids
                'firstname.dept': 0.25,
                'firstname.location': 0.20,
                'firstname.lastname.dept': 0.15,
                'firstname.lastname.location': 0.10,
                
                # G. International/Multilingual
                'f.lastname': 0.75,
                'fn.lastname': 0.40,
                'firstname.l': 0.55,
                'lastname.fn': 0.30,
                'firstname.x.lastname': 0.15,
                'transliteratedfirstname.lastname': 0.20
            },
            
            'education': {
                # A. Basic Name Standards (HIGH firstname.lastname usage)
                'firstname': 0.45,
                'lastname': 0.25,
                'firstname.lastname': 0.98,
                'firstname_lastname': 0.55,
                'firstname-lastname': 0.50,
                'firstinitial.lastname': 0.65,
                'firstname.lastinitial': 0.60,
                'firstinitiallastname': 0.65,
                'lastnamefirstinitial': 0.45,
                'lastname.firstname': 0.40,
                
                # B. Extended Name + Middle Initials (HIGH for academia)
                'firstname.middlename.lastname': 0.70,
                'firstname.middleinitial.lastname': 0.80,
                'firstinitial.middleinitial.lastname': 0.75,
                'firstname+middlename+lastname': 0.40,
                'firstinitial+middlename+lastname': 0.35,
                'firstname.middleinitial': 0.60,
                'firstname.middleinitiallastinitial': 0.50,
                'firstname.middlename': 0.55,
                
                # C. Abbreviated/Shortened (LOW for education)
                'first3letterslastname': 0.25,
                'first4letterslastname': 0.20,
                'firstname+last2letters': 0.15,
                'firstname+first2letterslastname': 0.15,
                'first2letterslastname': 0.20,
                'first3letterslast3letters': 0.25,
                'firstnameinitials': 0.30,
                'shortenedname.lastname': 0.20,
                'nickname.lastname': 0.35,
                'initials': 0.25,
                
                # D. Numeric Variants (LOW for education)
                'firstname.lastname1': 0.30,
                'firstname1': 0.20,
                'lastname1': 0.15,
                'firstinitiallastname1': 0.25,
                'firstname.lastname01': 0.20,
                'firstname.lastnameYY': 0.15,
                'firstnameYY': 0.10,
                
                # E. Reversed/Surname-first
                'lastnamefirstinitial': 0.45,
                'lastname_firstname': 0.40,
                'lastname-firstname': 0.35,
                'lastnamefirstname': 0.40,
                
                # F. Department/Location Hybrids (MEDIUM for education)
                'firstname.dept': 0.40,
                'firstname.location': 0.35,
                'firstname.lastname.dept': 0.30,
                'firstname.lastname.location': 0.25,
                
                # G. International/Multilingual (HIGH f.lastname)
                'f.lastname': 0.88,
                'fn.lastname': 0.60,
                'firstname.l': 0.65,
                'lastname.fn': 0.40,
                'firstname.x.lastname': 0.25,
                'transliteratedfirstname.lastname': 0.30
            },
            
            'finance': {
                # A. Basic Name Standards (FORMAL)
                'firstname': 0.55,
                'lastname': 0.35,
                'firstname.lastname': 0.85,
                'firstname_lastname': 0.50,
                'firstname-lastname': 0.45,
                'firstinitial.lastname': 0.80,
                'firstname.lastinitial': 0.70,
                'firstinitiallastname': 0.55,
                'lastnamefirstinitial': 0.55,
                'lastname.firstname': 0.45,
                
                # B. Extended Name + Middle Initials (HIGH for formal finance)
                'firstname.middlename.lastname': 0.65,
                'firstname.middleinitial.lastname': 0.75,
                'firstinitial.middleinitial.lastname': 0.80,
                'firstname+middlename+lastname': 0.35,
                'firstinitial+middlename+lastname': 0.40,
                'firstname.middleinitial': 0.60,
                'firstname.middleinitiallastinitial': 0.65,
                'firstname.middlename': 0.45,
                
                # C. Abbreviated/Shortened (LOW for finance)
                'first3letterslastname': 0.30,
                'first4letterslastname': 0.25,
                'firstname+last2letters': 0.20,
                'firstname+first2letterslastname': 0.20,
                'first2letterslastname': 0.25,
                'first3letterslast3letters': 0.30,
                'firstnameinitials': 0.35,
                'shortenedname.lastname': 0.25,
                'nickname.lastname': 0.20,
                'initials': 0.40,
                
                # D. Numeric Variants (MEDIUM for finance)
                'firstname.lastname1': 0.40,
                'firstname1': 0.25,
                'lastname1': 0.20,
                'firstinitiallastname1': 0.35,
                'firstname.lastname01': 0.30,
                'firstname.lastnameYY': 0.25,
                'firstnameYY': 0.15,
                
                # E. Reversed/Surname-first (FORMAL)
                'lastnamefirstinitial': 0.55,
                'lastname_firstname': 0.50,
                'lastname-firstname': 0.45,
                'lastnamefirstname': 0.45,
                
                # F. Department/Location Hybrids
                'firstname.dept': 0.30,
                'firstname.location': 0.25,
                'firstname.lastname.dept': 0.20,
                'firstname.lastname.location': 0.15,
                
                # G. International/Multilingual (HIGH f.lastname)
                'f.lastname': 0.90,
                'fn.lastname': 0.70,
                'firstname.l': 0.60,
                'lastname.fn': 0.50,
                'firstname.x.lastname': 0.20,
                'transliteratedfirstname.lastname': 0.25
            },
            
            # Add default weights for all other industries
            'default': {
                # A. Basic Name Standards
                'firstname': 0.60,
                'lastname': 0.35,
                'firstname.lastname': 0.80,
                'firstname_lastname': 0.55,
                'firstname-lastname': 0.50,
                'firstinitial.lastname': 0.70,
                'firstname.lastinitial': 0.60,
                'firstinitiallastname': 0.60,
                'lastnamefirstinitial': 0.40,
                'lastname.firstname': 0.45,
                
                # B. Extended Name + Middle Initials
                'firstname.middlename.lastname': 0.45,
                'firstname.middleinitial.lastname': 0.55,
                'firstinitial.middleinitial.lastname': 0.50,
                'firstname+middlename+lastname': 0.30,
                'firstinitial+middlename+lastname': 0.25,
                'firstname.middleinitial': 0.40,
                'firstname.middleinitiallastinitial': 0.35,
                'firstname.middlename': 0.35,
                
                # C. Abbreviated/Shortened
                'first3letterslastname': 0.40,
                'first4letterslastname': 0.35,
                'firstname+last2letters': 0.30,
                'firstname+first2letterslastname': 0.30,
                'first2letterslastname': 0.35,
                'first3letterslast3letters': 0.40,
                'firstnameinitials': 0.45,
                'shortenedname.lastname': 0.35,
                'nickname.lastname': 0.40,
                'initials': 0.35,
                
                # D. Numeric Variants
                'firstname.lastname1': 0.35,
                'firstname1': 0.25,
                'lastname1': 0.20,
                'firstinitiallastname1': 0.30,
                'firstname.lastname01': 0.25,
                'firstname.lastnameYY': 0.20,
                'firstnameYY': 0.15,
                
                # E. Reversed/Surname-first
                'lastnamefirstinitial': 0.40,
                'lastname_firstname': 0.35,
                'lastname-firstname': 0.30,
                'lastnamefirstname': 0.40,
                
                # F. Department/Location Hybrids
                'firstname.dept': 0.25,
                'firstname.location': 0.20,
                'firstname.lastname.dept': 0.15,
                'firstname.lastname.location': 0.10,
                
                # G. International/Multilingual
                'f.lastname': 0.75,
                'fn.lastname': 0.50,
                'firstname.l': 0.55,
                'lastname.fn': 0.35,
                'firstname.x.lastname': 0.15,
                'transliteratedfirstname.lastname': 0.20
            }
        }

        # Copy weights to other industry types
        self.pattern_weights['traditional'] = self.pattern_weights['default'].copy()
        self.pattern_weights['consulting'] = self.pattern_weights['finance'].copy()
        self.pattern_weights['fintech'] = self.pattern_weights['tech'].copy()
        self.pattern_weights['healthcare'] = self.pattern_weights['default'].copy()
        self.pattern_weights['government'] = self.pattern_weights['finance'].copy()  # Formal like finance
        self.pattern_weights['nonprofit'] = self.pattern_weights['default'].copy()

        # Company size modifiers (unchanged)
        self.size_modifiers = {
            '1-10': 0.1,
            '11-50': 0.05,
            '51-200': 0.0,
            '201-500': -0.05,
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
        domain = re.sub(r'^www\.', '', domain)
        domain = domain.split('/')[0]
        domain = domain.split(':')[0]

        return domain.strip()

    def get_company_type(self, industry: str, domain: str = None) -> str:
        """Enhanced company type detection with domain-first approach"""
        
        # Domain-first detection
        if domain:
            domain_clean = domain.lower().strip()
            
            if domain_clean.endswith('.edu'):
                return 'education'
            elif domain_clean.endswith('.org'):
                return 'nonprofit'
            elif domain_clean.endswith(('.gov', '.mil')):
                return 'government'
            elif domain_clean.endswith(('.io', '.tech', '.ai')):
                return 'tech'

        # Fallback to industry mapping
        if not industry:
            return 'default'

        industry_clean = industry.lower().strip()
        education_keywords = ['education', 'university', 'college', 'school', 'academic']
        if any(keyword in industry_clean for keyword in education_keywords):
            return 'education'

        return self.industry_mapping.get(industry_clean, 'default')

    def calculate_domain_score(self, domain: str) -> float:
        """Calculate domain quality score"""
        if not domain:
            return 0.0

        score = 0.5

        # Domain-specific bonuses
        if domain.endswith('.edu'):
            score += 0.25
        elif domain.endswith('.org'):
            score += 0.15
        elif domain.endswith('.gov'):
            score += 0.20

        # Domain length factor
        if 5 <= len(domain) <= 15:
            score += 0.1
        elif len(domain) > 20:
            score -= 0.1

        # Business domains
        business_domains = ['.com', '.net', '.io', '.co']
        if any(domain.endswith(bd) for bd in business_domains):
            score += 0.10

        # Tech domains
        tech_domains = ['.io', '.co', '.tech', '.ai']
        if any(domain.endswith(td) for td in tech_domains):
            score += 0.10

        # Avoid suspicious patterns
        suspicious_patterns = ['temp', 'test', 'example', 'demo']
        if any(sp in domain for sp in suspicious_patterns):
            score -= 0.3

        return min(1.0, max(0.0, score))

    def calculate_name_score(self, first_name: str, last_name: str) -> float:
        """Calculate name quality score"""
        score = 0.5

        if first_name and 2 <= len(first_name) <= 15:
            score += 0.2
        if last_name and 2 <= len(last_name) <= 20:
            score += 0.2

        if first_name and (len(first_name) < 2 or len(first_name) > 20):
            score -= 0.1
        if last_name and (len(last_name) < 2 or len(last_name) > 25):
            score -= 0.1

        return min(1.0, max(0.0, score))

    def get_pattern_domain_bonus(self, pattern: str, domain: str) -> float:
        """Pattern-domain correlation bonus"""
        if not domain:
            return 0.5

        domain_clean = domain.lower()

        # .edu domain bonuses
        if domain_clean.endswith('.edu'):
            edu_bonuses = {
                'firstname.lastname': 0.95,
                'f.lastname': 0.85,
                'firstname': 0.45,
                'firstinitiallastname': 0.60,
                'firstname_lastname': 0.55,
                'lastname.firstname': 0.40,
                'lastname': 0.30,
                'firstinitial.lastname': 0.75
            }
            return edu_bonuses.get(pattern, 0.5)

        # .org domain bonuses
        elif domain_clean.endswith('.org'):
            org_bonuses = {
                'f.lastname': 0.85,
                'firstname.lastname': 0.80,
                'firstname': 0.65,
                'lastname.firstname': 0.70,
                'firstinitiallastname': 0.55,
                'firstname_lastname': 0.60,
                'lastname': 0.50,
                'firstinitial.lastname': 0.70
            }
            return org_bonuses.get(pattern, 0.5)

        # .gov domain bonuses
        elif domain_clean.endswith('.gov'):
            gov_bonuses = {
                'f.lastname': 0.90,
                'lastname.firstname': 0.85,
                'firstname.lastname': 0.80,
                'firstinitial.lastname': 0.75,
                'firstname': 0.50,
                'firstinitiallastname': 0.45,
                'firstname_lastname': 0.60,
                'lastname': 0.65
            }
            return gov_bonuses.get(pattern, 0.5)

        # .com and other business domains
        elif domain_clean.endswith('.com'):
            com_bonuses = {
                'firstname.lastname': 0.80,
                'firstname': 0.75,
                'f.lastname': 0.70,
                'firstinitiallastname': 0.65,
                'firstname_lastname': 0.60,
                'lastname.firstname': 0.50,
                'lastname': 0.45,
                'firstinitial.lastname': 0.65
            }
            return com_bonuses.get(pattern, 0.5)

        return 0.5

    def generate_pattern_email(self, first_name: str, last_name: str, domain: str, pattern: str) -> str:
        """Generate email based on pattern - EXPANDED TO 50 PATTERNS"""
        if not all([first_name, domain]) or not pattern:
            return ""

        first_clean = self.clean_name(first_name)
        last_clean = self.clean_name(last_name) if last_name else ""

        # Get current year for year-based patterns
        current_year = str(datetime.now().year)[-2:]  # Last 2 digits

        # Helper functions for abbreviated names
        def get_abbreviated(name, length):
            return name[:length] if len(name) >= length else name

        def get_nickname(name):
            # Simple nickname mapping (can be expanded)
            nickname_map = {
                'robert': 'bob', 'william': 'bill', 'richard': 'rick',
                'michael': 'mike', 'christopher': 'chris', 'matthew': 'matt',
                'joshua': 'josh', 'andrew': 'andy', 'daniel': 'dan',
                'anthony': 'tony', 'elizabeth': 'liz', 'jennifer': 'jen',
                'stephanie': 'steph', 'katherine': 'kate', 'patricia': 'pat'
            }
            return nickname_map.get(name.lower(), name)

        # All 50 pattern implementations
        patterns = {
            # A. Basic Name Standards (10 patterns)
            'firstname': f"{first_clean}@{domain}",
            'lastname': f"{last_clean}@{domain}" if last_clean else "",
            'firstname.lastname': f"{first_clean}.{last_clean}@{domain}" if last_clean else f"{first_clean}@{domain}",
            'firstname_lastname': f"{first_clean}_{last_clean}@{domain}" if last_clean else f"{first_clean}@{domain}",
            'firstname-lastname': f"{first_clean}-{last_clean}@{domain}" if last_clean else f"{first_clean}@{domain}",
            'firstinitial.lastname': f"{first_clean[0] if first_clean else ''}.{last_clean}@{domain}" if last_clean else "",
            'firstname.lastinitial': f"{first_clean}.{last_clean[0] if last_clean else ''}@{domain}" if first_clean else "",
            'firstinitiallastname': f"{first_clean[0] if first_clean else ''}{last_clean}@{domain}" if last_clean else "",
            'lastnamefirstinitial': f"{last_clean}{first_clean[0] if first_clean else ''}@{domain}" if last_clean else "",
            'lastname.firstname': f"{last_clean}.{first_clean}@{domain}" if last_clean else "",

            # B. Extended Name + Middle Initials (8 patterns) - Using middle initial 'm' as placeholder
            'firstname.middlename.lastname': f"{first_clean}.m.{last_clean}@{domain}" if last_clean else "",
            'firstname.middleinitial.lastname': f"{first_clean}.m.{last_clean}@{domain}" if last_clean else "",
            'firstinitial.middleinitial.lastname': f"{first_clean[0] if first_clean else ''}.m.{last_clean}@{domain}" if last_clean else "",
            'firstname+middlename+lastname': f"{first_clean}+m+{last_clean}@{domain}" if last_clean else "",
            'firstinitial+middlename+lastname': f"{first_clean[0] if first_clean else ''}+m+{last_clean}@{domain}" if last_clean else "",
            'firstname.middleinitial': f"{first_clean}.m@{domain}",
            'firstname.middleinitiallastinitial': f"{first_clean}.m{last_clean[0] if last_clean else ''}@{domain}" if first_clean else "",
            'firstname.middlename': f"{first_clean}.m@{domain}",

            # C. Abbreviated/Shortened (10 patterns)
            'first3letterslastname': f"{get_abbreviated(first_clean, 3)}{last_clean}@{domain}" if last_clean else "",
            'first4letterslastname': f"{get_abbreviated(first_clean, 4)}{last_clean}@{domain}" if last_clean else "",
            'firstname+last2letters': f"{first_clean}{get_abbreviated(last_clean, 2)}@{domain}" if last_clean else "",
            'firstname+first2letterslastname': f"{get_abbreviated(first_clean, 2)}{last_clean}@{domain}" if last_clean else "",
            'first2letterslastname': f"{get_abbreviated(first_clean, 2)}{last_clean}@{domain}" if last_clean else "",
            'first3letterslast3letters': f"{get_abbreviated(first_clean, 3)}{get_abbreviated(last_clean, 3)}@{domain}" if last_clean else "",
            'firstnameinitials': f"{first_clean}{last_clean[0] if last_clean else ''}@{domain}" if first_clean else "",
            'shortenedname.lastname': f"{get_abbreviated(first_clean, 4)}.{last_clean}@{domain}" if last_clean else "",
            'nickname.lastname': f"{get_nickname(first_clean)}.{last_clean}@{domain}" if last_clean else "",
            'initials': f"{first_clean[0] if first_clean else ''}{last_clean[0] if last_clean else ''}@{domain}",

            # D. Numeric Variants (7 patterns)
            'firstname.lastname1': f"{first_clean}.{last_clean}1@{domain}" if last_clean else "",
            'firstname1': f"{first_clean}1@{domain}",
            'lastname1': f"{last_clean}1@{domain}" if last_clean else "",
            'firstinitiallastname1': f"{first_clean[0] if first_clean else ''}{last_clean}1@{domain}" if last_clean else "",
            'firstname.lastname01': f"{first_clean}.{last_clean}01@{domain}" if last_clean else "",
            'firstname.lastnameYY': f"{first_clean}.{last_clean}{current_year}@{domain}" if last_clean else "",
            'firstnameYY': f"{first_clean}{current_year}@{domain}",

            # E. Reversed/Surname-first (5 patterns) - Note: lastnamefirstinitial is in basic patterns
            'lastname_firstname': f"{last_clean}_{first_clean}@{domain}" if last_clean else "",
            'lastname-firstname': f"{last_clean}-{first_clean}@{domain}" if last_clean else "",
            'lastnamefirstname': f"{last_clean}{first_clean}@{domain}" if last_clean else "",

            # F. Department/Location Hybrids (4 patterns) - Using 'sales' and 'nyc' as examples
            'firstname.dept': f"{first_clean}.sales@{domain}",
            'firstname.location': f"{first_clean}.nyc@{domain}",
            'firstname.lastname.dept': f"{first_clean}.{last_clean}.sales@{domain}" if last_clean else "",
            'firstname.lastname.location': f"{first_clean}.{last_clean}.nyc@{domain}" if last_clean else "",

            # G. International/Multilingual (6 patterns)
            'f.lastname': f"{first_clean[0] if first_clean else ''}.{last_clean}@{domain}" if last_clean else "",
            'fn.lastname': f"{get_abbreviated(first_clean, 2)}.{last_clean}@{domain}" if last_clean else "",
            'firstname.l': f"{first_clean}.{last_clean[0] if last_clean else ''}@{domain}" if first_clean else "",
            'lastname.fn': f"{last_clean}.{get_abbreviated(first_clean, 2)}@{domain}" if last_clean else "",
            'firstname.x.lastname': f"{first_clean}.x.{last_clean}@{domain}" if last_clean else "",
            'transliteratedfirstname.lastname': f"{first_clean}.{last_clean}@{domain}" if last_clean else f"{first_clean}@{domain}"
        }

        return patterns.get(pattern, "")

    def calculate_confidence_score(self, 
                                 pattern: str,
                                 company_type: str,
                                 domain: str,
                                 first_name: str,
                                 last_name: str,
                                 company_size: str = None) -> Tuple[float, str]:
        """Enhanced confidence scoring with 50 patterns"""

        # Base pattern score (45% weight)
        pattern_weights = self.pattern_weights.get(company_type, self.pattern_weights['default'])
        base_score = pattern_weights.get(pattern, 0.3) * 0.45

        # Domain quality score (25% weight)
        domain_score = self.calculate_domain_score(domain) * 0.25

        # Name quality score (15% weight)
        name_score = self.calculate_name_score(first_name, last_name) * 0.15

        # Pattern-domain correlation bonus (15% weight)
        correlation_bonus = self.get_pattern_domain_bonus(pattern, domain) * 0.15

        # Company size modifier
        size_modifier = 0.0
        if company_size:
            size_modifier = self.size_modifiers.get(company_size, 0.0) * 0.05

        # Calculate final score
        final_score = base_score + domain_score + name_score + correlation_bonus + size_modifier

        # Enhanced reasoning
        reasoning_parts = [
            f"Pattern: {pattern} ({pattern_weights.get(pattern, 0.3):.2f})",
            f"Domain: {domain_score/0.25:.2f}",
            f"Names: {name_score/0.15:.2f}",
            f"Correlation: {correlation_bonus/0.15:.2f}",
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
                       max_candidates: int = 50) -> List[EmailCandidate]:
        """Generate ranked email candidates using 50 patterns"""

        if not first_name or not company_domain:
            self.logger.warning(f"Missing required data: first_name='{first_name}', domain='{company_domain}'")
            return []

        # Clean inputs
        domain = self.extract_domain(company_domain)
        if not domain:
            self.logger.warning(f"Invalid domain: {company_domain}")
            return []

        # Enhanced company type detection
        company_type = self.get_company_type(company_industry, domain)

        # Generate candidates for all 50 patterns
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

# Usage example
if __name__ == "__main__":
    generator = EnhancedEmailPatternGenerator()

    # Test with various examples
    test_cases = [
        {
            'firstName': 'John',
            'lastName': 'Smith',
            'companyDomain': 'harvard.edu',
            'companyIndustry': 'Higher Education',
            'companySize': '1000+'
        },
        {
            'firstName': 'Sarah',
            'lastName': 'Johnson',
            'companyDomain': 'techstartup.io',
            'companyIndustry': 'Technology',
            'companySize': '11-50'
        }
    ]

    print("50-PATTERN EMAIL GENERATION RESULTS:")
    print("=" * 60)

    for i, test in enumerate(test_cases, 1):
        result = generator.process_lead_data(test)
        print(f"\nTest {i}: {test['firstName']} {test['lastName']} @ {test['companyDomain']}")
        print(f"   Total Candidates: {len(result.get('emailCandidates', []))}")
        print(f"   Top Email: {result['generatedEmail']}")
        print(f"   Confidence: {result['emailConfidence']:.1%}")
        print(f"   Pattern: {result['emailPattern']}")
        for i, candidate in enumerate(result['emailCandidates'][:10]):
            print(f"{i+1}. {candidate['email']} ({candidate['pattern']}) - {candidate['confidence']:.3f}")