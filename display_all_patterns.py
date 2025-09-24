#!/usr/bin/env python3
"""
Dedicated script to display ALL 50 EMAIL PATTERNS with examples
This is the function you were looking for to see all patterns!
"""

from app.services.email_generator import EnhancedEmailPatternGenerator


def display_all_patterns():
    """
    🎯 THIS IS THE FUNCTION THAT PRINTS ALL 50 PATTERNS!
    
    Displays all implemented email patterns with examples for each category.
    """
    
    generator = EnhancedEmailPatternGenerator()
    
    # Get all patterns from the tech industry (most comprehensive set)
    all_patterns = generator.pattern_weights.get('tech', {})
    
    print("🚀 ALL 50 EMAIL PATTERNS - COMPLETE REFERENCE")
    print("=" * 80)
    print(f"📊 TOTAL PATTERNS IMPLEMENTED: {len(all_patterns)}")
    print()
    
    # Define pattern categories with descriptions
    pattern_categories = {
        "A. Basic Name Standards (10 patterns)": [
            'firstname',
            'lastname', 
            'firstname.lastname',
            'firstname_lastname',
            'firstname-lastname',
            'firstinitial.lastname',
            'firstname.lastinitial',
            'firstinitiallastname',
            'lastnamefirstinitial',
            'lastname.firstname'
        ],
        
        "B. Extended Name + Middle Initials (8 patterns)": [
            'firstname.middlename.lastname',
            'firstname.middleinitial.lastname',
            'firstinitial.middleinitial.lastname',
            'firstname+middlename+lastname',
            'firstinitial+middlename+lastname',
            'firstname.middleinitial',
            'firstname.middleinitiallastinitial',
            'firstname.middlename'
        ],
        
        "C. Abbreviated/Shortened (10 patterns)": [
            'first3letterslastname',
            'first4letterslastname',
            'firstname+last2letters',
            'firstname+first2letterslastname',
            'first2letterslastname',
            'first3letterslast3letters',
            'firstnameinitials',
            'shortenedname.lastname',
            'nickname.lastname',
            'initials'
        ],
        
        "D. Numeric Variants (7 patterns)": [
            'firstname.lastname1',
            'firstname1',
            'lastname1',
            'firstinitiallastname1',
            'firstname.lastname01',
            'firstname.lastnameYY',
            'firstnameYY'
        ],
        
        "E. Reversed/Surname-first (4 patterns)": [
            'lastname_firstname',
            'lastname-firstname', 
            'lastnamefirstname',
            'lastnamefirstinitial'  # Note: This is actually in basic patterns but logically belongs here
        ],
        
        "F. Department/Location Hybrids (4 patterns)": [
            'firstname.dept',
            'firstname.location',
            'firstname.lastname.dept',
            'firstname.lastname.location'
        ],
        
        "G. International/Multilingual (6 patterns)": [
            'f.lastname',
            'fn.lastname',
            'firstname.l',
            'lastname.fn',
            'firstname.x.lastname',
            'transliteratedfirstname.lastname'
        ]
    }
    
    # Sample names for demonstration
    sample_first = "John"
    sample_last = "Smith"
    sample_domain = "company.com"
    
    total_shown = 0
    
    for category, pattern_list in pattern_categories.items():
        print(f"\n📂 {category}")
        print("-" * len(category))
        
        for i, pattern in enumerate(pattern_list, 1):
            # Generate example email for this pattern
            example_email = generator.generate_pattern_email(sample_first, sample_last, sample_domain, pattern)
            
            # Get confidence weight for this pattern
            confidence = all_patterns.get(pattern, 0.0)
            
            # Mark if pattern exists in our implementation
            status = "✅" if pattern in all_patterns else "❌"
            
            print(f"  {i:2d}. {status} {pattern:35s} → {example_email:40s} (weight: {confidence:.2f})")
            
            if pattern in all_patterns:
                total_shown += 1
    
    print(f"\n📊 SUMMARY:")
    print(f"  📝 Total patterns categorized: {sum(len(patterns) for patterns in pattern_categories.values())}")
    print(f"  ✅ Patterns implemented: {total_shown}")
    print(f"  🔧 Patterns in system: {len(all_patterns)}")
    
    print(f"\n🧪 LIVE TEST WITH DIFFERENT NAMES:")
    test_names = [
        ("Sarah", "Johnson", "harvard.edu"),
        ("Alexander", "Chen", "techstartup.io"),
        ("Elizabeth", "Williams", "goldmansachs.com")
    ]
    
    for first, last, domain in test_names:
        test_data = {
            'firstName': first,
            'lastName': last, 
            'companyDomain': domain,
            'companyIndustry': 'Technology'
        }
        
        result = generator.process_lead_data(test_data)
        candidates = result.get('emailCandidates', [])
        
        print(f"\n📧 {first} {last} @ {domain}")
        print(f"   📊 Generated: {len(candidates)} unique candidates")
        print(f"   🏆 Top: {result['generatedEmail']} ({result['emailConfidence']:.1%})")
        print(f"   🔧 Pattern: {result['emailPattern']}")


def get_pattern_by_category():
    """
    Returns patterns organized by category for programmatic access
    """
    generator = EnhancedEmailPatternGenerator()
    all_patterns = generator.pattern_weights.get('tech', {})
    
    return {
        'basic_standards': ['firstname', 'lastname', 'firstname.lastname', 'firstname_lastname', 'firstname-lastname', 'firstinitial.lastname', 'firstname.lastinitial', 'firstinitiallastname', 'lastnamefirstinitial', 'lastname.firstname'],
        'middle_initials': ['firstname.middlename.lastname', 'firstname.middleinitial.lastname', 'firstinitial.middleinitial.lastname', 'firstname+middlename+lastname', 'firstinitial+middlename+lastname', 'firstname.middleinitial', 'firstname.middleinitiallastinitial', 'firstname.middlename'],
        'abbreviated': ['first3letterslastname', 'first4letterslastname', 'firstname+last2letters', 'firstname+first2letterslastname', 'first2letterslastname', 'first3letterslast3letters', 'firstnameinitials', 'shortenedname.lastname', 'nickname.lastname', 'initials'],
        'numeric': ['firstname.lastname1', 'firstname1', 'lastname1', 'firstinitiallastname1', 'firstname.lastname01', 'firstname.lastnameYY', 'firstnameYY'],
        'reversed': ['lastname_firstname', 'lastname-firstname', 'lastnamefirstname', 'lastnamefirstinitial'],
        'department': ['firstname.dept', 'firstname.location', 'firstname.lastname.dept', 'firstname.lastname.location'],
        'international': ['f.lastname', 'fn.lastname', 'firstname.l', 'lastname.fn', 'firstname.x.lastname', 'transliteratedfirstname.lastname']
    }


def show_pattern_examples():
    """
    Show practical examples of each pattern category
    """
    generator = EnhancedEmailPatternGenerator()
    
    examples = [
        ("Tech Startup", "Sarah", "Chen", "innovate.io", "Technology"),
        ("University", "Michael", "Johnson", "stanford.edu", "Education"), 
        ("Finance", "Emma", "Williams", "jpmorgan.com", "Finance"),
        ("Government", "David", "Smith", "government.gov", "Government")
    ]
    
    print("\n🎯 PATTERN EXAMPLES BY INDUSTRY:")
    print("=" * 60)
    
    for org_type, first, last, domain, industry in examples:
        print(f"\n🏢 {org_type}: {first} {last} @ {domain}")
        
        test_data = {
            'firstName': first,
            'lastName': last,
            'companyDomain': domain, 
            'companyIndustry': industry
        }
        
        result = generator.process_lead_data(test_data)
        candidates = result.get('emailCandidates', [])[:8]  # Show top 8
        
        print(f"   📊 Top {len(candidates)} patterns for {industry}:")
        for i, candidate in enumerate(candidates, 1):
            print(f"     {i}. {candidate['email']:35s} | {candidate['pattern']:25s} | {candidate['confidence']:.3f}")


if __name__ == "__main__":
    # THIS IS WHERE ALL PATTERNS ARE DISPLAYED!
    display_all_patterns()
    show_pattern_examples()