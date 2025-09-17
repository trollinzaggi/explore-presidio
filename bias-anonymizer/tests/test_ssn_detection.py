#!/usr/bin/env python3
"""
Test SSN detection specifically
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from presidio_analyzer import AnalyzerEngine
from bias_anonymizer.enhanced_recognizers import EnhancedSSNRecognizer

print("=" * 60)
print("SSN DETECTION TEST")
print("=" * 60)

# Test texts
test_texts = [
    "My SSN is 123-45-6789",
    "SSN: 123-45-6789",
    "social security: 123-45-6789",
    "123-45-6789",
    "ssn 123 45 6789",
    "Social Security Number 123456789",
]

print("\n1. Testing with default Presidio analyzer:")
print("-" * 40)
analyzer = AnalyzerEngine()

for text in test_texts:
    results = analyzer.analyze(text=text, language='en')
    detected = [r.entity_type for r in results]
    print(f"Text: '{text}'")
    print(f"  Detected: {detected}")
    if 'US_SSN' in detected:
        print("  ✅ SSN detected")
    else:
        print("  ❌ SSN NOT detected")
    print()

print("\n2. Testing with Enhanced SSN Recognizer:")
print("-" * 40)
analyzer2 = AnalyzerEngine()
enhanced_ssn = EnhancedSSNRecognizer()
analyzer2.registry.add_recognizer(enhanced_ssn)

for text in test_texts:
    results = analyzer2.analyze(text=text, language='en')
    detected = [r.entity_type for r in results]
    print(f"Text: '{text}'")
    print(f"  Detected: {detected}")
    if 'US_SSN' in detected:
        print("  ✅ SSN detected")
        for r in results:
            if r.entity_type == 'US_SSN':
                print(f"    Score: {r.score}")
    else:
        print("  ❌ SSN NOT detected")
    print()

print("\n3. Testing recognizer patterns directly:")
print("-" * 40)
import re

patterns = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "Basic SSN with dashes"),
    (r"(?i)(?:ssn|social\s*security|ss#|ss\s*#|social)\s*:?\s*\d{3}[-\s]?\d{2}[-\s]?\d{4}\b", "SSN with prefix"),
]

test_text = "My SSN is 123-45-6789 and social security: 987-65-4321"
for pattern, description in patterns:
    matches = re.findall(pattern, test_text)
    print(f"{description}:")
    print(f"  Pattern: {pattern}")
    print(f"  Matches: {matches}")

print("\n4. Checking analyzer configuration:")
print("-" * 40)

# Check if SSN recognizer is present
recognizer_names = [r.__class__.__name__ for r in analyzer.registry.recognizers]
print(f"Default recognizers: {recognizer_names}")

# Check supported entities
entities = analyzer.get_supported_entities()
print(f"Supported entities: {entities}")

# Check if US_SSN is supported
if 'US_SSN' in entities:
    print("✅ US_SSN is supported")
else:
    print("❌ US_SSN is NOT supported - this is the problem!")
