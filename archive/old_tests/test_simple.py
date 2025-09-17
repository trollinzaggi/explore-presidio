#!/usr/bin/env python3
"""
Simple test to verify the anonymizer is working
"""

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test imports one by one
print("Testing imports...")

try:
    print("1. Importing TalentProfileAnonymizer...")
    from bias_anonymizer.talent_profile_anonymizer import TalentProfileAnonymizer, TalentProfileConfig
    print("   ✓ Success")
except ImportError as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

try:
    print("2. Importing config_loader...")
    from bias_anonymizer.config_loader import create_anonymizer_from_config
    print("   ✓ Success")
except ImportError as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

try:
    print("3. Importing anonymizer_wrapper...")
    from bias_anonymizer.anonymizer_wrapper import BiasAnonymizer
    print("   ✓ Success")
except ImportError as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

print("\nAll imports successful!")

# Simple test
print("\n" + "="*60)
print("SIMPLE ANONYMIZATION TEST")
print("="*60)

test_profile = {
    "core": {
        "businessTitle": "Senior white male engineer",
        "jobCode": "ENG_001"
    }
}

print("\nOriginal profile:")
print(json.dumps(test_profile, indent=2))

# Test 1: Programmatic configuration (minimal)
print("\n1. Testing with programmatic configuration (strategy='redact')...")
try:
    config = TalentProfileConfig(
        anonymization_strategy="redact",
        preserve_fields={"core.jobCode"},
        always_anonymize_fields={"core.businessTitle"}
    )
    anonymizer = TalentProfileAnonymizer(config)
    result = anonymizer.anonymize_talent_profile(test_profile)
    print(f"   Result: {result['core']['businessTitle']}")
    print(f"   Job code preserved: {result['core']['jobCode']}")
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 2: Using wrapper with strategy
print("\n2. Testing BiasAnonymizer wrapper...")
try:
    anonymizer = BiasAnonymizer(strategy="redact")
    result = anonymizer.anonymize(test_profile)
    print(f"   Result: {result['core']['businessTitle']}")
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 3: Using default YAML config (if available)
print("\n3. Testing with default YAML config...")
try:
    anonymizer = BiasAnonymizer()  # Should load from default_config.yaml
    result = anonymizer.anonymize(test_profile)
    print(f"   Result: {result['core']['businessTitle']}")
    print("   ✓ Success")
except FileNotFoundError:
    print("   ⚠ default_config.yaml not found (this is OK if not set up yet)")
except Exception as e:
    print(f"   ✗ Failed: {e}")

print("\n" + "="*60)
print("Basic tests completed!")
print("="*60)
