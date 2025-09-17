#!/usr/bin/env python3
"""
Complete working example showing how to use the Bias Anonymizer
This script can be run standalone after installation
"""

# Suppress SSL warning (optional but recommended)
import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import json
import sys
from pathlib import Path

# IMPORTANT: Update this path to point to your bias-anonymizer folder
BIAS_ANONYMIZER_PATH = '/path/to/bias-anonymizer/src'  # <-- CHANGE THIS!

# Add the bias-anonymizer to Python path
sys.path.insert(0, BIAS_ANONYMIZER_PATH)

try:
    from bias_anonymizer.anonymizer_wrapper import BiasAnonymizer, anonymize_profile
    print("✅ Bias Anonymizer imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import Bias Anonymizer: {e}")
    print(f"   Please check that the path is correct: {BIAS_ANONYMIZER_PATH}")
    sys.exit(1)


def example_1_simple_text():
    """Example 1: Anonymizing simple text fields."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple Text Anonymization")
    print("="*60)
    
    data = {
        "name": "John Smith",
        "bio": "Senior white male engineer from wealthy family",
        "notes": "Married with children, graduated from Harvard"
    }
    
    print("\nOriginal:")
    print(json.dumps(data, indent=2))
    
    # Anonymize with redact strategy (removes bias words)
    anonymizer = BiasAnonymizer(strategy="redact")
    result = anonymizer.anonymize(data)
    
    print("\nAnonymized (redact):")
    print(json.dumps(result, indent=2))
    
    # Try with replace strategy (replaces with tokens)
    anonymizer = BiasAnonymizer(strategy="replace")
    result = anonymizer.anonymize(data)
    
    print("\nAnonymized (replace):")
    print(json.dumps(result, indent=2))


def example_2_nested_json():
    """Example 2: Anonymizing nested JSON structures."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Nested JSON Structure")
    print("="*60)
    
    employee_data = {
        "id": "EMP001",
        "personal": {
            "age": "45-year-old male",
            "background": "Hispanic immigrant from Mexico"
        },
        "work": {
            "title": "Senior Engineer",
            "team": "Manages young female developers"
        },
        "reviews": [
            "Great worker despite being elderly",
            "Works well with the other Christians on the team"
        ]
    }
    
    print("\nOriginal:")
    print(json.dumps(employee_data, indent=2))
    
    anonymizer = BiasAnonymizer()
    result = anonymizer.anonymize(employee_data)
    
    print("\nAnonymized:")
    print(json.dumps(result, indent=2))


def example_3_talent_profile():
    """Example 3: Full talent profile anonymization."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Complete Talent Profile")
    print("="*60)
    
    talent_profile = {
        "userId": "USER_12345",
        "core": {
            "businessTitle": "Senior white male software engineer",
            "jobCode": "ENG_001",  # This should be preserved
            "rank": {
                "code": "L7",  # This should be preserved
                "description": "Principal Engineer - mostly older white males"
            }
        },
        "experience": {
            "experiences": [{
                "company": "Google - known for young workforce",
                "description": "Led team of Asian and Hispanic engineers",
                "jobTitle": "Engineering Manager for diverse team"
            }]
        },
        "qualification": {
            "educations": [{
                "institutionName": "Stanford - elite school for wealthy",
                "degree": "MS Computer Science",  # This should be preserved
                "achievements": "Top student from donor family"
            }]
        },
        "workEligibility": "US Citizen, no visa required"
    }
    
    print("\nOriginal Profile:")
    print(json.dumps(talent_profile, indent=2))
    
    # Use the convenience function
    anonymized = anonymize_profile(talent_profile, strategy="redact")
    
    print("\nAnonymized Profile:")
    print(json.dumps(anonymized, indent=2))
    
    # Verify that important fields are preserved
    print("\n✅ Verification:")
    print(f"   jobCode preserved: {anonymized['core']['jobCode'] == 'ENG_001'}")
    print(f"   rank.code preserved: {anonymized['core']['rank']['code'] == 'L7'}")
    print(f"   Bias removed from title: 'white' not in anonymized['core']['businessTitle']")


def example_4_batch_processing():
    """Example 4: Processing multiple records."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Batch Processing")
    print("="*60)
    
    profiles = [
        {"id": 1, "desc": "Young Asian female developer"},
        {"id": 2, "desc": "Elderly white male manager"},
        {"id": 3, "desc": "Hispanic single mother in accounting"}
    ]
    
    print("\nOriginal profiles:")
    for p in profiles:
        print(f"  {p}")
    
    # Process all profiles
    anonymizer = BiasAnonymizer(strategy="replace")
    anonymized_profiles = [anonymizer.anonymize(p) for p in profiles]
    
    print("\nAnonymized profiles:")
    for p in anonymized_profiles:
        print(f"  {p}")


def example_5_save_to_file():
    """Example 5: Save anonymized data to file."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Saving Results to File")
    print("="*60)
    
    data = {
        "employee": "John Smith",
        "description": "50-year-old white male executive from wealthy family",
        "notes": "Married, Christian, Republican voter"
    }
    
    # Anonymize
    anonymizer = BiasAnonymizer()
    result = anonymizer.anonymize(data)
    
    # Save to file
    output_file = "anonymized_output.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"✅ Anonymized data saved to {output_file}")
    print(f"   Original: {data['description']}")
    print(f"   Anonymized: {result['description']}")


def main():
    """Run all examples."""
    print("\n🚀 BIAS ANONYMIZER - WORKING EXAMPLES")
    print("This script demonstrates how to use the anonymizer in your code")
    
    try:
        example_1_simple_text()
        example_2_nested_json()
        example_3_talent_profile()
        example_4_batch_processing()
        example_5_save_to_file()
        
        print("\n" + "="*60)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nYou can now use these patterns in your own code.")
        print("Remember to update the BIAS_ANONYMIZER_PATH at the top of your script!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
