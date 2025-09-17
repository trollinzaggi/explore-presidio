#!/usr/bin/env python3
"""
Test script for the anonymizer wrapper
"""

import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bias_anonymizer.anonymizer_wrapper import BiasAnonymizer, anonymize_profile, analyze_profile

# Test data
test_profile = {
    "core": {
        "rank": {
            "code": "L7",
            "description": "Senior white male engineer"
        },
        "businessTitle": "Hispanic female manager from wealthy family",
        "jobCode": "ENG_001",
        "customField": "This is a custom field with bias: young Asian developer"
    },
    "experience": {
        "experiences": [{
            "company": "Stanford University",
            "description": "Led team of Black and Hispanic engineers",
            "jobTitle": "Senior Engineering Manager",
            "customNote": "Worked with disabled colleague"
        }]
    },
    "qualification": {
        "educations": [{
            "institutionName": "Harvard University - Elite school",
            "degree": "MS Computer Science",
            "achievements": "Graduated from wealthy donor family"
        }]
    }
}

def test_wrapper_class():
    """Test the BiasAnonymizer class."""
    print("\n" + "="*60)
    print("TEST: BiasAnonymizer Class")
    print("="*60)
    
    # Test 1: Default (remove) strategy
    anonymizer = BiasAnonymizer()
    result = anonymizer.anonymize(test_profile)
    print("\n1. Remove Strategy:")
    print("   Original:", test_profile["core"]["businessTitle"])
    print("   Anonymized:", result["core"]["businessTitle"])
    
    # Test 2: Replace strategy
    result = anonymizer.anonymize_with_replace(test_profile)
    print("\n2. Replace Strategy:")
    print("   Original:", test_profile["experience"]["experiences"][0]["description"])
    print("   Anonymized:", result["experience"]["experiences"][0]["description"])
    
    # Test 3: Custom tokens
    custom_tokens = {
        "GENDER_BIAS": "person",
        "RACE_BIAS": "individual",
        "SOCIOECONOMIC_BIAS": "professional"
    }
    result = anonymizer.anonymize_with_custom(test_profile, custom_tokens)
    print("\n3. Custom Tokens:")
    print("   Original:", test_profile["core"]["businessTitle"])
    print("   Anonymized:", result["core"]["businessTitle"])

def test_custom_fields():
    """Test custom field handling."""
    print("\n" + "="*60)
    print("TEST: Custom Fields")
    print("="*60)
    
    anonymizer = BiasAnonymizer()
    
    # Test adding custom fields to anonymize
    result = anonymizer.anonymize(
        test_profile,
        fields_to_anonymize=["core.customField", "experience.experiences[0].customNote"]
    )
    
    print("\n1. Additional fields to anonymize:")
    print("   Original customField:", test_profile["core"]["customField"])
    print("   Anonymized customField:", result["core"].get("customField", "[REMOVED]"))
    print("   Original customNote:", test_profile["experience"]["experiences"][0]["customNote"])
    print("   Anonymized customNote:", result["experience"]["experiences"][0].get("customNote", "[REMOVED]"))
    
    # Test preserving normally anonymized fields
    result = anonymizer.anonymize(
        test_profile,
        fields_to_preserve=["core.businessTitle"]
    )
    
    print("\n2. Preserve normally anonymized field:")
    print("   Original businessTitle:", test_profile["core"]["businessTitle"])
    print("   After processing:", result["core"]["businessTitle"])
    print("   (Should be unchanged)")

def test_direct_functions():
    """Test direct function calls."""
    print("\n" + "="*60)
    print("TEST: Direct Functions")
    print("="*60)
    
    # Test anonymize_profile function
    result = anonymize_profile(test_profile, strategy="remove")
    print("\n1. anonymize_profile (remove):")
    print("   Institution:", result["qualification"]["educations"][0]["institutionName"])
    
    result = anonymize_profile(
        test_profile,
        strategy="replace",
        fields_to_anonymize=["core.jobCode"]
    )
    print("\n2. anonymize_profile (replace + custom field):")
    print("   Description:", result["experience"]["experiences"][0]["description"])
    print("   JobCode:", result["core"].get("jobCode", "[ANONYMIZED]"))
    
    # Test analyze function
    analysis = analyze_profile(test_profile)
    print("\n3. analyze_profile:")
    print(f"   Risk Score: {analysis['risk_score']}/100")
    print(f"   Fields with bias: {len(analysis['fields_with_bias'])}")
    print(f"   Bias categories: {', '.join(analysis['bias_categories_found'][:3])}...")

def test_json_string_input():
    """Test with JSON string input."""
    print("\n" + "="*60)
    print("TEST: JSON String Input")
    print("="*60)
    
    json_string = json.dumps(test_profile)
    
    anonymizer = BiasAnonymizer()
    result = anonymizer.anonymize(json_string)
    
    print("\n1. String input handling:")
    print("   Input type:", type(json_string).__name__)
    print("   Output type:", type(result).__name__)
    print("   Anonymized businessTitle:", result["core"]["businessTitle"])

if __name__ == "__main__":
    print("ANONYMIZER WRAPPER TEST SUITE")
    print("Testing the BiasAnonymizer wrapper functionality...")
    
    try:
        test_wrapper_class()
        test_custom_fields()
        test_direct_functions()
        test_json_string_input()
        
        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
