#!/usr/bin/env python3
"""
Test script for TalentProfileAnonymizer with different strategies
"""

import json
import sys
import os

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bias_anonymizer.talent_profile_anonymizer import TalentProfileAnonymizer, TalentProfileConfig

# Test data
test_profile = {
    "core": {
        "rank": {
            "code": "L7",
            "description": "Senior white male engineer"
        },
        "businessTitle": "Hispanic female manager from wealthy family",
        "jobCode": "ENG_001"
    },
    "experience": {
        "experiences": [{
            "company": "Stanford University",
            "description": "Led team of Asian and Black engineers",
            "jobTitle": "Senior Engineering Manager"
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

def test_remove_strategy():
    """Test with remove strategy (default)"""
    print("\n" + "="*60)
    print("TEST 1: REMOVE STRATEGY (Default)")
    print("="*60)
    
    config = TalentProfileConfig(anonymization_strategy="remove")
    anonymizer = TalentProfileAnonymizer(config)
    
    result = anonymizer.anonymize_talent_profile(test_profile)
    
    print("\nOriginal businessTitle:", test_profile["core"]["businessTitle"])
    print("Anonymized businessTitle:", result["core"].get("businessTitle", "[EMPTY]"))
    
    print("\nOriginal experience description:", test_profile["experience"]["experiences"][0]["description"])
    print("Anonymized experience description:", result["experience"]["experiences"][0].get("description", "[EMPTY]"))
    
    print("\nOriginal institution:", test_profile["qualification"]["educations"][0]["institutionName"])
    print("Anonymized institution:", result["qualification"]["educations"][0].get("institutionName", "[EMPTY]"))
    
    # Verify preserved fields
    print("\n✓ Job code preserved:", result["core"]["jobCode"] == test_profile["core"]["jobCode"])
    print("✓ Degree preserved:", result["qualification"]["educations"][0]["degree"] == test_profile["qualification"]["educations"][0]["degree"])

def test_replace_strategy():
    """Test with replace strategy"""
    print("\n" + "="*60)
    print("TEST 2: REPLACE STRATEGY")
    print("="*60)
    
    config = TalentProfileConfig(anonymization_strategy="replace")
    anonymizer = TalentProfileAnonymizer(config)
    
    result = anonymizer.anonymize_talent_profile(test_profile)
    
    print("\nOriginal businessTitle:", test_profile["core"]["businessTitle"])
    print("Anonymized businessTitle:", result["core"].get("businessTitle", "[EMPTY]"))
    
    print("\nOriginal experience description:", test_profile["experience"]["experiences"][0]["description"])
    print("Anonymized experience description:", result["experience"]["experiences"][0].get("description", "[EMPTY]"))
    
    print("\nOriginal institution:", test_profile["qualification"]["educations"][0]["institutionName"])
    print("Anonymized institution:", result["qualification"]["educations"][0].get("institutionName", "[EMPTY]"))

def test_custom_strategy():
    """Test with custom replacement strategy"""
    print("\n" + "="*60)
    print("TEST 3: CUSTOM STRATEGY")
    print("="*60)
    
    config = TalentProfileConfig(
        anonymization_strategy="custom",
        replacement_tokens={
            "GENDER_BIAS": "person",
            "RACE_BIAS": "individual",
            "SOCIOECONOMIC_BIAS": "professional",
            "EDUCATION_BIAS": "[SCHOOL]"
        }
    )
    anonymizer = TalentProfileAnonymizer(config)
    
    result = anonymizer.anonymize_talent_profile(test_profile)
    
    print("\nOriginal businessTitle:", test_profile["core"]["businessTitle"])
    print("Anonymized businessTitle:", result["core"].get("businessTitle", "[EMPTY]"))
    
    print("\nOriginal experience description:", test_profile["experience"]["experiences"][0]["description"])
    print("Anonymized experience description:", result["experience"]["experiences"][0].get("description", "[EMPTY]"))

def test_analysis():
    """Test the analysis function"""
    print("\n" + "="*60)
    print("TEST 4: PROFILE ANALYSIS")
    print("="*60)
    
    anonymizer = TalentProfileAnonymizer()
    analysis = anonymizer.analyze_profile(test_profile)
    
    print(f"\nRisk Score: {analysis['risk_score']}/100")
    print(f"Fields with bias: {len(analysis['fields_with_bias'])}")
    print(f"Fields with PII: {len(analysis['fields_with_pii'])}")
    print(f"Bias categories found: {', '.join(analysis['bias_categories_found'])}")
    
    if analysis['details']:
        print("\nDetailed findings:")
        for detail in analysis['details'][:3]:  # Show first 3
            print(f"  - {detail['field']}: {detail['entities_found']} entities")

if __name__ == "__main__":
    print("TALENT PROFILE ANONYMIZER TEST")
    print("Testing different anonymization strategies...")
    
    test_remove_strategy()
    test_replace_strategy()
    test_custom_strategy()
    test_analysis()
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)
