#!/usr/bin/env python3
"""
Test phone number detection specifically for edge cases
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from presidio_analyzer import AnalyzerEngine
from bias_anonymizer.enhanced_recognizers import EnhancedPhoneRecognizer
from bias_anonymizer.config_loader import create_anonymizer_from_config

print("=" * 60)
print("PHONE NUMBER EDGE CASE TEST")
print("=" * 60)

# Test texts with various phone formats
test_texts = [
    "Call me at 555-123-4567",
    "Phone: 555-1234",
    "Contact HR at 555-HR-HELP",
    "Dial 415-555-0100",
    "Short number: 555-1234",
    "Call 1-800-FLOWERS",
    "555-AB-CDEF format",
]

print("\n1. Testing with Enhanced Phone Recognizer directly:")
print("-" * 40)
analyzer = AnalyzerEngine()
phone_recognizer = EnhancedPhoneRecognizer()
analyzer.registry.add_recognizer(phone_recognizer)

for text in test_texts:
    results = analyzer.analyze(text=text, language='en', score_threshold=0.5)
    detected = [(r.entity_type, r.score) for r in results]
    print(f"Text: '{text}'")
    print(f"  Detected: {detected}")
    if any(r.entity_type == 'PHONE_NUMBER' for r in results):
        print("  ✅ Phone detected")
    else:
        print("  ❌ Phone NOT detected")
    print()

print("\n2. Testing with TalentProfileAnonymizer:")
print("-" * 40)
anonymizer = create_anonymizer_from_config()

for text in test_texts:
    test_data = {"careerAspirationPreference": text}
    result = anonymizer.anonymize_talent_profile(test_data)
    result_text = result.get("careerAspirationPreference", "")
    
    print(f"Original: {text}")
    print(f"Result:   {result_text}")
    if text != result_text:
        print("  ✅ Anonymized")
    else:
        print("  ❌ NOT anonymized")
    print()

print("\n3. Testing specific pattern for 555-HR-HELP:")
print("-" * 40)
import re

patterns = [
    (r"(?i)\b\d{3}-[A-Z]{2}-[A-Z]{4}\b", "General letter pattern"),
    (r"(?i)\b555-[A-Z]{2}-[A-Z]{4}\b", "555 vanity pattern"),
    (r"555-HR-HELP", "Exact match"),
]

test = "call HR at 555-HR-HELP for assistance"
for pattern, description in patterns:
    matches = re.findall(pattern, test, re.IGNORECASE)
    print(f"{description}:")
    print(f"  Pattern: {pattern}")
    print(f"  Matches: {matches}")
