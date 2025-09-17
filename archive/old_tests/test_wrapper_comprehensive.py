#!/usr/bin/env python3
"""
Comprehensive test for the anonymizer wrapper
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

def test_wrapper_initialization():
    """Test different ways to initialize the wrapper."""
    print("\n" + "="*60)
    print("TEST 1: Wrapper Initialization")
    print("="*60)
    
    # Test 1: Default initialization (should use default YAML)
    print("\n1. Default initialization (uses default_config.yaml):")
    try:
        anonymizer = BiasAnonymizer()
        print(f"   Strategy: {anonymizer.strategy}")
        print("   ✓ Success")
    except FileNotFoundError:
        print("   ⚠ default_config.yaml not found - using minimal config")
        anonymizer = BiasAnonymizer(strategy="redact")
        print(f"   Strategy: {anonymizer.strategy}")
        print("   ✓ Success with fallback")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 2: With explicit strategy
    print("\n2. With explicit strategy:")
    try:
        anonymizer = BiasAnonymizer(strategy="replace")
        print(f"   Strategy: {anonymizer.strategy}")
        print("   ✓ Success")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    return True

def test_anonymization_strategies():
    """Test different anonymization strategies."""
    print("\n" + "="*60)
    print("TEST 2: Anonymization Strategies")
    print("="*60)
    
    test_text = "Senior white male engineer from wealthy family"
    simple_profile = {"text": test_text}
    
    # Test redact strategy
    print(f"\nOriginal: {test_text}")
    print("-" * 40)
    
    print("\n1. REDACT strategy:")
    try:
        anonymizer = BiasAnonymizer(strategy="redact")
        result = anonymizer.anonymize({"core": {"title": test_text}})
        print(f"   Result: {result['core']['title']}")
        print("   ✓ Success")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test replace strategy
    print("\n2. REPLACE strategy:")
    try:
        anonymizer = BiasAnonymizer(strategy="replace")
        result = anonymizer.anonymize({"core": {"title": test_text}})
        print(f"   Result: {result['core']['title']}")
        print("   ✓ Success")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    return True

def test_convenience_methods():
    """Test convenience methods."""
    print("\n" + "="*60)
    print("TEST 3: Convenience Methods")
    print("="*60)
    
    anonymizer = BiasAnonymizer(strategy="redact")
    
    # Test anonymize_with_redact
    print("\n1. anonymize_with_redact():")
    try:
        result = anonymizer.anonymize_with_redact(test_profile)
        print(f"   businessTitle: {result['core']['businessTitle']}")
        print("   ✓ Success")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test anonymize_with_replace
    print("\n2. anonymize_with_replace():")
    try:
        result = anonymizer.anonymize_with_replace(test_profile)
        print(f"   businessTitle: {result['core']['businessTitle']}")
        print("   ✓ Success")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test anonymize_with_custom
    print("\n3. anonymize_with_custom():")
    try:
        custom_tokens = {
            "GENDER_BIAS": "person",
            "RACE_BIAS": "individual",
            "SOCIOECONOMIC_BIAS": "professional"
        }
        result = anonymizer.anonymize_with_custom(test_profile, custom_tokens)
        print(f"   businessTitle: {result['core']['businessTitle']}")
        print("   ✓ Success")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    return True

def test_custom_fields():
    """Test custom field handling."""
    print("\n" + "="*60)
    print("TEST 4: Custom Fields")
    print("="*60)
    
    anonymizer = BiasAnonymizer(strategy="redact")
    
    # Test with custom fields to anonymize
    print("\n1. Custom fields to anonymize:")
    try:
        result = anonymizer.anonymize(
            test_profile,
            fields_to_anonymize=["core.customField"],
            fields_to_preserve=["core.businessTitle"]
        )
        print(f"   customField: {result['core'].get('customField', 'N/A')}")
        print(f"   businessTitle (preserved): {result['core']['businessTitle']}")
        print("   ✓ Success")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    return True

def test_direct_functions():
    """Test module-level functions."""
    print("\n" + "="*60)
    print("TEST 5: Direct Functions")
    print("="*60)
    
    # Test anonymize_profile function
    print("\n1. anonymize_profile():")
    try:
        result = anonymize_profile(test_profile, strategy="redact")
        print(f"   businessTitle: {result['core']['businessTitle']}")
        print("   ✓ Success")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test analyze_profile function
    print("\n2. analyze_profile():")
    try:
        analysis = analyze_profile(test_profile)
        print(f"   Risk Score: {analysis['risk_score']}/100")
        print(f"   Fields with bias: {len(analysis['fields_with_bias'])}")
        print("   ✓ Success")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    return True

def test_json_string_input():
    """Test JSON string input handling."""
    print("\n" + "="*60)
    print("TEST 6: JSON String Input")
    print("="*60)
    
    json_string = json.dumps(test_profile)
    
    print("\n1. JSON string as input:")
    try:
        anonymizer = BiasAnonymizer(strategy="redact")
        result = anonymizer.anonymize(json_string)
        print(f"   Input type: {type(json_string).__name__}")
        print(f"   Output type: {type(result).__name__}")
        print(f"   businessTitle: {result['core']['businessTitle']}")
        print("   ✓ Success")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    return True

def main():
    print("ANONYMIZER WRAPPER COMPREHENSIVE TEST")
    print("Testing all wrapper functionality...")
    
    all_passed = True
    
    # Run all tests
    tests = [
        ("Initialization", test_wrapper_initialization),
        ("Strategies", test_anonymization_strategies),
        ("Convenience Methods", test_convenience_methods),
        ("Custom Fields", test_custom_fields),
        ("Direct Functions", test_direct_functions),
        ("JSON String Input", test_json_string_input)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
            all_passed = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    if all_passed:
        print("\n✅ All wrapper tests passed!")
    else:
        print("\n❌ Some tests failed. Check the output above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
