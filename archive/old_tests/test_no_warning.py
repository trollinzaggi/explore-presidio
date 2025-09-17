#!/usr/bin/env python3
"""
Test script with warning suppression
"""

# Suppress the SSL warning
import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bias_anonymizer.anonymizer_wrapper import BiasAnonymizer

# Test data
test_profile = {
    "core": {
        "businessTitle": "Senior white male engineer",
        "jobCode": "ENG_001"
    }
}

print("Testing anonymizer (warning suppressed)...")
print("-" * 40)

# Test
anonymizer = BiasAnonymizer(strategy="redact")
result = anonymizer.anonymize(test_profile)

print(f"Original: {test_profile['core']['businessTitle']}")
print(f"Anonymized: {result['core']['businessTitle']}")
print("\n✅ Test complete - no warnings!")
