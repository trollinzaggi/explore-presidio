#!/usr/bin/env python3
"""
Test to PROVE whether BiasAnonymizer wrapper and create_anonymizer_from_config
produce the same or different results.
"""

import sys
import os
import json
import tempfile
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Suppress SSL warning
import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

from bias_anonymizer.anonymizer_wrapper import BiasAnonymizer
from bias_anonymizer.config_loader import create_anonymizer_from_config

# Test data with various field types
TEST_DATA = {
    "userId": "USER_12345",
    "core": {
        "businessTitle": "Senior white male engineer from wealthy family",
        "jobCode": "ENG_001",
        "rank": {
            "code": "L7",
            "description": "Principal level - mostly older white males"
        },
        "employeeType": {
            "code": "FTE",
            "description": "Full-time married employee with children"
        }
    },
    "experience": {
        "experiences": [{
            "company": "Google - known for young workforce",
            "description": "Led team of Asian and Hispanic engineers",
            "jobTitle": "Engineering Manager",
            "startDate": "2020-03-15",
            "endDate": "2023-12-31"
        }],
        "crossDivisionalExperience": "Yes"
    },
    "qualification": {
        "educations": [{
            "institutionName": "Stanford - elite school for wealthy families",
            "degree": "MS Computer Science",
            "areaOfStudy": "Machine Learning",
            "completionYear": 2020,
            "achievements": "Top of class from donor family"
        }],
        "certifications": ["AWS", "Azure", "GCP"]
    },
    "workEligibility": "US Citizen, no visa required",
    "customField": "This is a custom field with bias: old Hispanic woman"
}


def create_test_config(strategy="redact"):
    """Create a test configuration file."""
    config = {
        'anonymization_strategy': strategy,
        'detect_bias': True,
        'detect_pii': True,
        'confidence_threshold': 0.7,
        
        # Fields to preserve
        'preserve_fields': [
            'core.jobCode',
            'core.rank.code',
            'core.employeeType.code',
            'experience.crossDivisionalExperience',
            'qualification.educations[*].degree',
            'qualification.educations[*].areaOfStudy',
            'qualification.educations[*].completionYear',
            'qualification.certifications'
        ],
        
        # Fields to anonymize
        'always_anonymize_fields': [
            'core.businessTitle',
            'core.rank.description',
            'core.employeeType.description',
            'experience.experiences[*].company',
            'experience.experiences[*].description',
            'experience.experiences[*].jobTitle',
            'qualification.educations[*].institutionName',
            'qualification.educations[*].achievements',
            'workEligibility',
            'customField'
        ],
        
        # Special handling
        'special_handling_fields': {
            'userId': 'hash',
            'experience.experiences[*].startDate': 'year_only',
            'experience.experiences[*].endDate': 'year_only'
        },
        
        # Operators based on strategy
        'operators': {}
    }
    
    if strategy == "redact":
        config['operators'] = {
            'GENDER_BIAS': 'redact',
            'RACE_BIAS': 'redact',
            'AGE_BIAS': 'redact',
            'SOCIOECONOMIC_BIAS': 'redact',
            'DEFAULT': 'redact'
        }
    else:  # replace
        config['operators'] = {
            'GENDER_BIAS': 'replace',
            'RACE_BIAS': 'replace',
            'AGE_BIAS': 'replace',
            'SOCIOECONOMIC_BIAS': 'replace',
            'DEFAULT': 'replace'
        }
        config['replacement_tokens'] = {
            'GENDER_BIAS': '[GENDER]',
            'RACE_BIAS': '[RACE]',
            'AGE_BIAS': '[AGE]',
            'SOCIOECONOMIC_BIAS': '[BACKGROUND]',
            'DEFAULT': '[REDACTED]'
        }
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    yaml.dump(config, temp_file)
    temp_file.close()
    
    return temp_file.name


def test_identical_results():
    """Test if both methods produce identical results."""
    print("="*60)
    print("TEST 1: Are Results Identical?")
    print("="*60)
    
    # Create config file
    config_path = create_test_config(strategy="redact")
    
    try:
        # Method A: BiasAnonymizer wrapper
        print("\nMethod A: BiasAnonymizer wrapper")
        anonymizer_a = BiasAnonymizer(config_path=config_path)
        result_a = anonymizer_a.anonymize(TEST_DATA)
        
        # Method B: create_anonymizer_from_config
        print("Method B: create_anonymizer_from_config")
        anonymizer_b = create_anonymizer_from_config(config_path)
        result_b = anonymizer_b.anonymize_talent_profile(TEST_DATA)
        
        # Compare results
        print("\n" + "-"*40)
        print("COMPARISON:")
        
        # Check if results are identical
        identical = (result_a == result_b)
        print(f"Results identical: {identical}")
        
        if not identical:
            # Find differences
            print("\nDIFFERENCES FOUND:")
            compare_nested(result_a, result_b)
        else:
            print("✅ Results are IDENTICAL!")
            
        # Show sample outputs
        print("\n" + "-"*40)
        print("Sample field comparisons:")
        print(f"businessTitle A: {result_a['core']['businessTitle']}")
        print(f"businessTitle B: {result_b['core']['businessTitle']}")
        print(f"Match: {result_a['core']['businessTitle'] == result_b['core']['businessTitle']}")
        
        return identical
        
    finally:
        # Clean up
        Path(config_path).unlink()


def test_different_strategies():
    """Test both methods with different strategies."""
    print("\n" + "="*60)
    print("TEST 2: Different Strategies")
    print("="*60)
    
    strategies = ["redact", "replace"]
    
    for strategy in strategies:
        print(f"\nTesting with strategy: {strategy}")
        print("-"*40)
        
        config_path = create_test_config(strategy=strategy)
        
        try:
            # Method A
            anonymizer_a = BiasAnonymizer(config_path=config_path)
            result_a = anonymizer_a.anonymize(TEST_DATA)
            
            # Method B
            anonymizer_b = create_anonymizer_from_config(config_path)
            result_b = anonymizer_b.anonymize_talent_profile(TEST_DATA)
            
            # Compare
            identical = (result_a == result_b)
            print(f"Results identical for {strategy}: {identical}")
            
            if not identical:
                print(f"❌ DIFFERENCE in {strategy} strategy!")
                compare_nested(result_a, result_b)
            else:
                print(f"✅ Same results for {strategy}")
                
        finally:
            Path(config_path).unlink()


def test_field_preservation():
    """Test if both methods preserve the same fields."""
    print("\n" + "="*60)
    print("TEST 3: Field Preservation")
    print("="*60)
    
    config_path = create_test_config()
    
    try:
        # Method A
        anonymizer_a = BiasAnonymizer(config_path=config_path)
        result_a = anonymizer_a.anonymize(TEST_DATA)
        
        # Method B
        anonymizer_b = create_anonymizer_from_config(config_path)
        result_b = anonymizer_b.anonymize_talent_profile(TEST_DATA)
        
        # Check preserved fields
        preserved_fields = [
            ('jobCode', result_a['core']['jobCode'], result_b['core']['jobCode'], TEST_DATA['core']['jobCode']),
            ('rank.code', result_a['core']['rank']['code'], result_b['core']['rank']['code'], TEST_DATA['core']['rank']['code']),
            ('degree', result_a['qualification']['educations'][0]['degree'], 
             result_b['qualification']['educations'][0]['degree'],
             TEST_DATA['qualification']['educations'][0]['degree'])
        ]
        
        print("\nPreserved Fields Check:")
        all_preserved = True
        for field_name, val_a, val_b, original in preserved_fields:
            match_a = (val_a == original)
            match_b = (val_b == original)
            both_match = (match_a and match_b and val_a == val_b)
            
            print(f"{field_name}:")
            print(f"  Original: {original}")
            print(f"  Method A: {val_a} {'✅' if match_a else '❌'}")
            print(f"  Method B: {val_b} {'✅' if match_b else '❌'}")
            print(f"  Both same: {'✅' if both_match else '❌'}")
            
            if not both_match:
                all_preserved = False
        
        return all_preserved
        
    finally:
        Path(config_path).unlink()


def test_special_handling():
    """Test if special handling works the same."""
    print("\n" + "="*60)
    print("TEST 4: Special Handling")
    print("="*60)
    
    config_path = create_test_config()
    
    try:
        # Method A
        anonymizer_a = BiasAnonymizer(config_path=config_path)
        result_a = anonymizer_a.anonymize(TEST_DATA)
        
        # Method B
        anonymizer_b = create_anonymizer_from_config(config_path)
        result_b = anonymizer_b.anonymize_talent_profile(TEST_DATA)
        
        print("\nSpecial Handling Check:")
        
        # Check userId (should be hashed)
        print(f"userId (should be hashed):")
        print(f"  Original: {TEST_DATA['userId']}")
        print(f"  Method A: {result_a.get('userId', 'MISSING')}")
        print(f"  Method B: {result_b.get('userId', 'MISSING')}")
        print(f"  Both same: {result_a.get('userId') == result_b.get('userId')} ✅" 
              if result_a.get('userId') == result_b.get('userId') else "❌")
        
        # Check dates (should be year only)
        print(f"\nstartDate (should be year only):")
        print(f"  Original: {TEST_DATA['experience']['experiences'][0]['startDate']}")
        print(f"  Method A: {result_a['experience']['experiences'][0].get('startDate', 'MISSING')}")
        print(f"  Method B: {result_b['experience']['experiences'][0].get('startDate', 'MISSING')}")
        
        date_a = result_a['experience']['experiences'][0].get('startDate')
        date_b = result_b['experience']['experiences'][0].get('startDate')
        print(f"  Both same: {'✅' if date_a == date_b else '❌'}")
        
    finally:
        Path(config_path).unlink()


def test_edge_cases():
    """Test edge cases and complex nested structures."""
    print("\n" + "="*60)
    print("TEST 5: Edge Cases")
    print("="*60)
    
    edge_case_data = {
        "empty_field": "",
        "null_field": None,
        "nested": {
            "deep": {
                "deeper": {
                    "text": "Young Asian female developer"
                }
            }
        },
        "array": [
            "White male manager",
            "Black female engineer",
            "Hispanic elderly person"
        ],
        "mixed": {
            "text": "Senior engineer",
            "number": 42,
            "boolean": True,
            "array": ["item1", "white male", "item3"]
        }
    }
    
    config_path = create_test_config()
    
    try:
        # Method A
        anonymizer_a = BiasAnonymizer(config_path=config_path)
        result_a = anonymizer_a.anonymize(edge_case_data)
        
        # Method B
        anonymizer_b = create_anonymizer_from_config(config_path)
        result_b = anonymizer_b.anonymize_talent_profile(edge_case_data)
        
        # Compare
        identical = (result_a == result_b)
        print(f"Edge cases identical: {identical}")
        
        if not identical:
            print("\nDifferences in edge cases:")
            compare_nested(result_a, result_b)
        else:
            print("✅ Edge cases handled identically!")
            
    finally:
        Path(config_path).unlink()


def compare_nested(dict1, dict2, path=""):
    """Helper to find differences in nested dictionaries."""
    for key in set(list(dict1.keys()) + list(dict2.keys())):
        current_path = f"{path}.{key}" if path else key
        
        if key not in dict1:
            print(f"  Missing in A: {current_path}")
        elif key not in dict2:
            print(f"  Missing in B: {current_path}")
        elif dict1[key] != dict2[key]:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                compare_nested(dict1[key], dict2[key], current_path)
            else:
                print(f"  Difference at {current_path}:")
                print(f"    A: {dict1[key]}")
                print(f"    B: {dict2[key]}")


def main():
    print("\n🔬 TESTING: BiasAnonymizer vs create_anonymizer_from_config")
    print("This will prove whether they produce the same results or not\n")
    
    results = {
        "Test 1 (Identical Results)": test_identical_results(),
        "Test 2 (Strategies)": test_different_strategies(),
        "Test 3 (Field Preservation)": test_field_preservation(),
        "Test 4 (Special Handling)": test_special_handling(),
        "Test 5 (Edge Cases)": test_edge_cases()
    }
    
    print("\n" + "="*60)
    print("FINAL RESULTS:")
    print("="*60)
    
    all_passed = all(results.values() if isinstance(results.values(), bool) else True)
    
    if all_passed:
        print("✅ CONFIRMED: Both methods produce IDENTICAL results!")
        print("   The BiasAnonymizer wrapper and create_anonymizer_from_config")
        print("   are functionally equivalent when using the same configuration.")
    else:
        print("❌ DIFFERENCES FOUND: The methods do NOT produce identical results!")
        print("   There are behavioral differences between the two approaches.")
    
    print("\nConclusion:")
    print("-----------")
    if all_passed:
        print("You can use either method - they're equivalent.")
        print("Choose based on API preference:")
        print("  - BiasAnonymizer: Simpler method names")
        print("  - create_anonymizer_from_config: More methods available")
    else:
        print("The methods have different behaviors.")
        print("Review the differences above to choose the right one.")


if __name__ == "__main__":
    main()
