#!/usr/bin/env python3
"""
Debug why 555-HR-HELP isn't being anonymized in the country field
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bias_anonymizer.config_loader import create_anonymizer_from_config
from presidio_analyzer import AnalyzerEngine
from bias_anonymizer.enhanced_recognizers import EnhancedPhoneRecognizer

print("=" * 60)
print("DEBUGGING 555-HR-HELP IN COUNTRY FIELD")
print("=" * 60)

# Create anonymizer
anonymizer = create_anonymizer_from_config()

# Test the exact text from the country field
test_text = "United States (visa sponsorship available, call HR at 555-HR-HELP)"

print("\n1. Direct analysis of the text:")
print("-" * 40)
print(f"Text: {test_text}")

# Analyze with the anonymizer's analyzer
results = anonymizer.analyzer.analyze(text=test_text, language='en', score_threshold=0.5)
print(f"\nEntities detected:")
for r in results:
    print(f"  {r.entity_type}: '{test_text[r.start:r.end]}' (score: {r.score:.2f}, pos: {r.start}-{r.end})")

# Check for overlaps
print("\n2. Checking for entity overlaps:")
print("-" * 40)
phone_entities = [r for r in results if r.entity_type == 'PHONE_NUMBER']
location_entities = [r for r in results if r.entity_type == 'LOCATION']

for phone in phone_entities:
    for loc in location_entities:
        if (phone.start >= loc.start and phone.start < loc.end) or \
           (phone.end > loc.start and phone.end <= loc.end):
            print(f"OVERLAP DETECTED:")
            print(f"  PHONE: '{test_text[phone.start:phone.end]}' at {phone.start}-{phone.end}")
            print(f"  LOCATION: '{test_text[loc.start:loc.end]}' at {loc.start}-{loc.end}")

print("\n3. Testing anonymization of the field:")
print("-" * 40)
test_profile = {
    "core": {
        "workLocation": {
            "country": test_text
        }
    }
}

result = anonymizer.anonymize_talent_profile(test_profile)
result_text = result['core']['workLocation']['country']

print(f"Original: {test_text}")
print(f"Result:   {result_text}")

# Check if 555-HR-HELP is still there
import re
if re.search(r'555-HR-HELP', result_text):
    print("\n❌ 555-HR-HELP NOT anonymized")
    print("\nPossible reasons:")
    print("1. Entity overlap - LOCATION might be taking priority")
    print("2. Field might not be in always_anonymize_fields")
    print("3. Operator conflict")
else:
    print("\n✅ 555-HR-HELP properly anonymized")

# Check if field is in always_anonymize_fields
print("\n4. Checking field configuration:")
print("-" * 40)
from bias_anonymizer.config_loader import load_config_from_yaml
config = load_config_from_yaml()
always_anonymize = config.get('always_anonymize_fields', [])

field_path = 'core.workLocation.country'
if field_path in always_anonymize:
    print(f"✅ '{field_path}' IS in always_anonymize_fields")
else:
    print(f"❌ '{field_path}' is NOT in always_anonymize_fields")
    print("   This would explain why it's not being anonymized!")
