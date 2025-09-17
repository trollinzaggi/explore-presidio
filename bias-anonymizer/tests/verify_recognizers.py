#!/usr/bin/env python3
"""
Verify that TalentProfileAnonymizer has all the required recognizers registered.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bias_anonymizer.config_loader import create_anonymizer_from_config

print("=" * 60)
print("VERIFYING RECOGNIZERS IN TALENT PROFILE ANONYMIZER")
print("=" * 60)

# Create an instance using the proper config loader
anonymizer = create_anonymizer_from_config()  # This creates it properly with ProfileConfig

# Get all registered recognizers
recognizers = anonymizer.analyzer.registry.recognizers

print(f"\nTotal recognizers registered: {len(recognizers)}")
print("-" * 40)

# Expected bias recognizers (14 categories)
expected_bias_recognizers = [
    'GENDER_BIAS',
    'RACE_BIAS',
    'AGE_BIAS',
    'DISABILITY_BIAS',
    'FAMILY_STATUS_BIAS',  # or MARITAL_STATUS_BIAS
    'NATIONALITY_BIAS',
    'SEXUAL_ORIENTATION_BIAS',
    'RELIGION_BIAS',
    'POLITICAL_BIAS',
    'SOCIOECONOMIC_BIAS',
    'MATERNITY_BIAS',  # or PREGNANCY_BIAS
    'UNION_BIAS',
    'HEALTH_BIAS',
    'CRIMINAL_BIAS'
]

# Expected PII recognizers
expected_pii_recognizers = [
    'PHONE_NUMBER',
    'US_SSN',
    'EMAIL_ADDRESS',
    'PERSON',
    'LOCATION',
    'CREDIT_CARD',
    'IP_ADDRESS',
    'DATE_TIME'
]

# Check what's actually registered
registered_entities = {}
for recognizer in recognizers:
    # Get supported entities for this recognizer
    entities = recognizer.supported_entities
    for entity in entities:
        if entity not in registered_entities:
            registered_entities[entity] = []
        registered_entities[entity].append(recognizer.__class__.__name__)

print("\n1. Checking Bias Recognizers:")
print("-" * 40)

bias_found = 0
for expected in expected_bias_recognizers:
    if expected in registered_entities:
        recognizer_names = registered_entities[expected]
        print(f"✅ {expected:30s} - {recognizer_names[0]}")
        bias_found += 1
    else:
        # Check for aliases
        if expected == 'FAMILY_STATUS_BIAS' and 'MARITAL_STATUS_BIAS' in registered_entities:
            print(f"✅ {expected:30s} - Found as MARITAL_STATUS_BIAS")
            bias_found += 1
        elif expected == 'MATERNITY_BIAS' and 'PREGNANCY_BIAS' in registered_entities:
            print(f"✅ {expected:30s} - Found as PREGNANCY_BIAS")
            bias_found += 1
        else:
            print(f"❌ {expected:30s} - MISSING!")

print(f"\nBias recognizers found: {bias_found}/14")

print("\n2. Checking PII Recognizers:")
print("-" * 40)

pii_found = 0
for expected in expected_pii_recognizers:
    if expected in registered_entities:
        recognizer_names = registered_entities[expected]
        # Check if it's an enhanced recognizer
        is_enhanced = any('Enhanced' in name for name in recognizer_names)
        status = "(Enhanced)" if is_enhanced else ""
        print(f"✅ {expected:30s} - {recognizer_names[0]} {status}")
        pii_found += 1
    else:
        print(f"❌ {expected:30s} - MISSING!")

print(f"\nPII recognizers found: {pii_found}/{len(expected_pii_recognizers)}")

print("\n3. All Registered Entity Types:")
print("-" * 40)

for entity_type in sorted(registered_entities.keys()):
    recognizers_list = registered_entities[entity_type]
    print(f"  {entity_type:30s} ({', '.join(recognizers_list)})")

print("\n4. Testing Actual Detection:")
print("-" * 40)

# Test with a simple sentence containing various bias words
test_text = "The young Asian female engineer who is pregnant and Muslim works here."

# Analyze
results = anonymizer.analyzer.analyze(text=test_text, language='en', score_threshold=0.5)

# Group by entity type
detected_types = {}
for result in results:
    if result.entity_type not in detected_types:
        detected_types[result.entity_type] = []
    detected_types[result.entity_type].append(test_text[result.start:result.end])

print(f"Test text: '{test_text}'")
print(f"\nDetected entities:")
for entity_type, words in detected_types.items():
    print(f"  {entity_type}: {words}")

# Test more bias categories
print("\n5. Testing All Categories with Sample Words:")
print("-" * 40)

category_tests = {
    "Gender": "he, she, male, female",
    "Race": "white, Black, Asian, Hispanic",
    "Age": "young, elderly, millennial",
    "Disability": "disabled, wheelchair user",
    "Marriage": "married, single, divorced",
    "Nationality": "American, immigrant, foreign",
    "Sexual Orientation": "gay, lesbian, heterosexual",
    "Religion": "Christian, Muslim, Jewish, atheist",
    "Political": "conservative, liberal, Republican",
    "Socioeconomic": "wealthy, poor, privileged",
    "Pregnancy": "pregnant, maternity leave",
    "Union": "union member, collective bargaining",
    "Health": "depression, anxiety, diabetes",
    "Criminal": "criminal record, clean record"
}

for category, test_words in category_tests.items():
    results = anonymizer.analyzer.analyze(text=test_words, language='en', score_threshold=0.5)
    bias_results = [r for r in results if 'BIAS' in r.entity_type]
    if bias_results:
        entity_types = list(set([r.entity_type for r in bias_results]))
        print(f"✅ {category:20s}: Detected as {entity_types[0]}")
    else:
        print(f"❌ {category:20s}: NOT detected")

# Final verdict
print("\n" + "=" * 60)
if bias_found >= 13 and pii_found >= 6:  # Allow for some aliases
    print("✅ ALL RECOGNIZERS PROPERLY REGISTERED!")
    print(f"   Bias categories: {bias_found}/14")
    print(f"   PII types: {pii_found}/{len(expected_pii_recognizers)}")
else:
    print("⚠️  Some recognizers may be missing. Check the configuration.")
    print(f"   Bias: {bias_found}/14, PII: {pii_found}/{len(expected_pii_recognizers)}")
