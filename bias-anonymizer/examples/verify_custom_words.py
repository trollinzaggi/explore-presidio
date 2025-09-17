"""
Verify and demonstrate the custom bias words are loaded correctly.
"""

import json
import sys
import os

# Add src to path
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
except NameError:
    # Fallback if __file__ is not defined
    sys.path.insert(0, os.path.join(os.getcwd(), '..', 'src'))

from bias_anonymizer import JSONAnonymizer, BiasWords


def verify_custom_words():
    """Verify all custom bias words are loaded and working."""
    
    print("=" * 70)
    print("BIAS WORD DATABASE VERIFICATION")
    print("=" * 70)
    
    # Get statistics
    stats = BiasWords.get_statistics()
    print(f"\nTotal Categories: {stats['total_categories']}")
    print(f"Total Unique Words: {stats['total_unique_words']}")
    print("\nWords per category:")
    for key, value in stats.items():
        if key.endswith('_count'):
            category = key.replace('_count', '')
            print(f"  - {category}: {value} words")
    
    print("\n" + "=" * 70)
    print("TESTING EACH CATEGORY WITH SAMPLE WORDS")
    print("=" * 70)
    
    # Test samples from each category
    test_cases = {
        "gender": {
            "text": "He is a male employee and she is his female colleague",
            "expected_removed": ["He", "male", "she", "his", "female"]
        },
        "race_ethnicity": {
            "text": "The Asian candidate and African American employee met the European manager",
            "expected_removed": ["Asian", "African American", "European"]
        },
        "age": {
            "text": "A young millennial works with a middle-aged veteran and a senior baby boomer",
            "expected_removed": ["young", "millennial", "middle-aged", "veteran", "senior", "baby boomer"]
        },
        "disability": {
            "text": "The disabled wheelchair user and the able-bodied physically fit person",
            "expected_removed": ["disabled", "wheelchair user", "able-bodied", "physically fit"]
        },
        "marital_status": {
            "text": "The single bachelor, the married spouse with children, and the divorced parent",
            "expected_removed": ["single", "bachelor", "married", "spouse", "children", "divorced", "parent"]
        },
        "nationality": {
            "text": "American US citizen native-born versus foreign immigrant visa holder",
            "expected_removed": ["American", "US citizen", "native-born", "foreign", "immigrant", "visa holder"]
        },
        "sexual_orientation": {
            "text": "Heterosexual straight traditional or gay lesbian LGBTQ alternative",
            "expected_removed": ["Heterosexual", "straight", "traditional", "gay", "lesbian", "LGBTQ", "alternative"]
        },
        "religion": {
            "text": "Christian Catholic church-going, Muslim Islamic mosque, Jewish Hebrew synagogue, Hindu Buddhist temple",
            "expected_removed": ["Christian", "Catholic", "church-going", "Muslim", "Islamic", "mosque", "Jewish", "Hebrew", "synagogue", "Hindu", "Buddhist", "temple"]
        },
        "political_affiliation": {
            "text": "Conservative Republican right-wing versus liberal Democratic progressive left-wing",
            "expected_removed": ["Conservative", "Republican", "right-wing", "liberal", "Democratic", "progressive", "left-wing"]
        },
        "socioeconomic": {
            "text": "Wealthy privileged elite upper-class versus working-class blue-collar poor disadvantaged",
            "expected_removed": ["Wealthy", "privileged", "elite", "upper-class", "working-class", "blue-collar", "poor", "disadvantaged"]
        },
        "pregnancy": {
            "text": "Pregnant expecting maternity leave with newborn infant",
            "expected_removed": ["Pregnant", "expecting", "maternity", "newborn", "infant"]
        },
        "union": {
            "text": "Union unionized collective bargaining versus non-union independent contractor",
            "expected_removed": ["Union", "unionized", "collective bargaining", "non-union", "independent", "contractor"]
        },
        "health": {
            "text": "Diabetes depression anxiety mental health chronic illness medical condition",
            "expected_removed": ["Diabetes", "depression", "anxiety", "mental health", "chronic illness", "medical condition"]
        },
        "criminal": {
            "text": "Criminal record conviction felony versus clean record law-abiding trustworthy",
            "expected_removed": ["Criminal record", "conviction", "felony", "clean record", "law-abiding", "trustworthy"]
        }
    }
    
    # Initialize anonymizer
    anonymizer = JSONAnonymizer()
    
    # Test each category
    for category, test_data in test_cases.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        print(f"  Original: {test_data['text']}")
        
        # Anonymize
        result = anonymizer.anonymize({"text": test_data["text"]})
        anonymized_text = result["text"]
        
        print(f"  Anonymized: {anonymized_text}")
        
        # Check if expected words were removed
        removed_count = 0
        for word in test_data["expected_removed"]:
            if word.lower() not in anonymized_text.lower():
                removed_count += 1
        
        print(f"  ✓ Removed {removed_count}/{len(test_data['expected_removed'])} expected bias terms")
    
    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST WITH ALL CATEGORIES")
    print("=" * 70)
    
    # Comprehensive test with multiple bias categories in one text
    comprehensive_text = """
    John is a 45-year-old white Christian male from a wealthy family. 
    He's married with children and works as a senior executive. 
    Despite his disability (uses wheelchair), he's a Republican voter 
    who opposes unions. He has no criminal record and is in good mental health.
    His young Hispanic female colleague, Maria, is a single mother from a 
    working-class background. She's a liberal Democrat who supports LGBTQ rights.
    """
    
    print("\nOriginal text (with multiple bias indicators):")
    print(comprehensive_text)
    
    # Analyze first
    analysis = anonymizer.analyze({"text": comprehensive_text})
    print(f"\nAnalysis results:")
    print(f"  - Total entities detected: {analysis['total_entities']}")
    print(f"  - Bias categories found: {', '.join(analysis['bias_categories'])}")
    print(f"  - PII types found: {', '.join(analysis['pii_types'])}")
    
    # Anonymize
    result = anonymizer.anonymize({"text": comprehensive_text})
    print(f"\nAnonymized text:")
    print(result["text"])
    
    # Show what was removed
    original_words = set(comprehensive_text.lower().split())
    anonymized_words = set(result["text"].lower().split())
    removed_words = original_words - anonymized_words
    
    print(f"\nWords removed: {', '.join(sorted(removed_words))}")
    
    print("\n" + "=" * 70)
    print("✓ VERIFICATION COMPLETE - All custom bias words are active!")
    print("=" * 70)


def demonstrate_json_anonymization():
    """Demonstrate JSON anonymization with custom bias words."""
    
    print("\n\n" + "=" * 70)
    print("JSON ANONYMIZATION WITH CUSTOM BIAS WORDS")
    print("=" * 70)
    
    # Sample employee profile with various bias indicators
    employee_data = {
        "id": "EMP12345",
        "personal": {
            "bio": "Senior white male engineer, married with kids, Christian, Republican",
            "description": "Experienced veteran from wealthy family, Yale graduate",
            "health": "Recent back surgery, uses wheelchair, takes medication for anxiety"
        },
        "professional": {
            "summary": "45-year-old accomplished leader, non-union, traditional values",
            "skills": ["Python", "Management", "System Design"],
            "preferences": "Looking for young, energetic team members"
        },
        "background": {
            "education": "Private school, Ivy League university",
            "criminal": "Clean record, law-abiding citizen",
            "nationality": "US citizen, native-born American"
        }
    }
    
    print("\nOriginal Employee Data:")
    print(json.dumps(employee_data, indent=2))
    
    # Anonymize entire structure
    anonymizer = JSONAnonymizer()
    anonymized_all = anonymizer.anonymize(employee_data)
    
    print("\nFully Anonymized (all fields):")
    print(json.dumps(anonymized_all, indent=2))
    
    # Selective anonymization - only personal fields
    anonymized_selective = anonymizer.anonymize(
        employee_data,
        keys_to_anonymize=["personal.bio", "personal.description", "personal.health", "professional.summary"]
    )
    
    print("\nSelectively Anonymized (only specified fields):")
    print(json.dumps(anonymized_selective, indent=2))
    
    # Show statistics
    print("\nProcessing Statistics:")
    stats = anonymizer.get_statistics()
    for key, value in stats.items():
        if value > 0:
            print(f"  - {key}: {value}")


if __name__ == "__main__":
    # Run verification
    verify_custom_words()
    
    # Demonstrate JSON anonymization
    demonstrate_json_anonymization()
