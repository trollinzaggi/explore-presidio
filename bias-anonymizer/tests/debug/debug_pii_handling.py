#!/usr/bin/env python3
"""
Debug script to understand why PII isn't being handled correctly
"""

import sys
import os
import json
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Suppress SSL warning
import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

from bias_anonymizer.config_loader import create_anonymizer_from_config
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

print("=" * 60)
print("PII DETECTION AND ANONYMIZATION DEBUG")
print("=" * 60)

# Load config
config_path = Path(__file__).parent / "config" / "default_config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

print(f"\n1. Configuration Check:")
print(f"   Strategy: {config.get('anonymization_strategy')}")
print(f"   Operators defined: {len(config.get('operators', {}))}")

# Show specific operators
print(f"\n2. Operator Configuration:")
for entity, op in list(config.get('operators', {}).items())[:10]:
    print(f"   {entity}: {op}")

# Create anonymizer
print(f"\n3. Creating Anonymizer...")
anonymizer = create_anonymizer_from_config()

# Check what operators are actually configured
print(f"\n4. Checking Actual Operators in Anonymizer:")
if hasattr(anonymizer, 'operators'):
    for entity_type, operator in list(anonymizer.operators.items())[:10]:
        print(f"   {entity_type}: {operator}")
else:
    print("   ERROR: No operators attribute found!")

# Test specific text samples
print(f"\n5. Testing Individual PII Types:")
print("-" * 40)

test_cases = [
    ("SSN Test", "My SSN is 123-45-6789", "US_SSN"),
    ("Phone Test", "Call me at 555-123-4567", "PHONE_NUMBER"),
    ("Email Test", "Email me at john@example.com", "EMAIL_ADDRESS"),
    ("Address Test", "I live at 123 Main Street, NY 10001", "LOCATION"),
    ("Name Test", "My name is John Smith", "PERSON"),
    ("Credit Card", "Card number: 4111-1111-1111-1111", "CREDIT_CARD"),
    ("IP Address", "Connect to 192.168.1.100", "IP_ADDRESS"),
]

# Test with Presidio directly
analyzer = AnalyzerEngine()
anonymizer_engine = AnonymizerEngine()

for test_name, test_text, expected_entity in test_cases:
    print(f"\n{test_name}:")
    print(f"  Text: {test_text}")
    
    # Analyze
    results = analyzer.analyze(text=test_text, language='en')
    print(f"  Detected: {[r.entity_type for r in results]}")
    
    # Check if expected entity was detected
    detected_types = [r.entity_type for r in results]
    if expected_entity in detected_types:
        print(f"  ✅ {expected_entity} detected")
    else:
        print(f"  ❌ {expected_entity} NOT detected")
        print(f"     Available types: {detected_types}")
    
    # Try to anonymize with custom operators
    if results:
        # Get operator from config
        op_type = config.get('operators', {}).get(expected_entity, 'redact')
        print(f"  Config operator: {op_type}")
        
        # Create operator with proper parameters
        if op_type == 'mask':
            operator = OperatorConfig("mask", {
                "masking_char": "*",
                "chars_to_mask": 100,
                "from_end": False
            })
        elif op_type == 'hash':
            operator = OperatorConfig("hash")
        elif op_type == 'replace':
            token = config.get('replacement_tokens', {}).get(expected_entity, '[REDACTED]')
            operator = OperatorConfig("replace", {"new_value": token})
        else:
            operator = OperatorConfig("redact")
        
        # Anonymize
        anonymized = anonymizer_engine.anonymize(
            text=test_text,
            analyzer_results=results,
            operators={expected_entity: operator}
        )
        print(f"  Anonymized: {anonymized.text}")

# Test with actual anonymizer
print(f"\n6. Testing with TalentProfileAnonymizer:")
print("-" * 40)

test_profile = {
    "core": {
        "businessTitle": "Contact John Smith at 555-123-4567, SSN: 123-45-6789"
    }
}

result = anonymizer.anonymize_talent_profile(test_profile)
print(f"Original: {test_profile['core']['businessTitle']}")
print(f"Result:   {result['core']['businessTitle']}")

# Check for remaining PII
import re

remaining_pii = []
if re.search(r'\b\d{3}-\d{2}-\d{4}\b', result['core']['businessTitle']):
    remaining_pii.append("SSN")
if re.search(r'\b\d{3}-\d{3}-\d{4}\b', result['core']['businessTitle']):
    remaining_pii.append("Phone")
if re.search(r'\b[\w._%+-]+@[\w.-]+\.[A-Z|a-z]{2,}\b', result['core']['businessTitle']):
    remaining_pii.append("Email")

if remaining_pii:
    print(f"\n❌ PROBLEM: These PII types still visible: {remaining_pii}")
else:
    print(f"\n✅ All PII properly anonymized")

# Debug the _configure_operators method
print(f"\n7. Checking _configure_operators Method:")
print("-" * 40)

# Get the profile config
if hasattr(anonymizer, 'profile_config'):
    pc = anonymizer.profile_config
    print(f"Strategy in profile_config: {pc.anonymization_strategy}")
    print(f"Operators in profile_config: {len(pc.operators) if pc.operators else 0}")
    if pc.operators:
        for entity, op in list(pc.operators.items())[:5]:
            print(f"  {entity}: {op}")
