#!/usr/bin/env python3
"""
Test comprehensive bias word detection across all 14 categories.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bias_anonymizer.config_loader import create_anonymizer_from_config
from bias_anonymizer.bias_words import BiasWords

print("=" * 60)
print("COMPREHENSIVE BIAS DETECTION TEST")
print("=" * 60)

# Create anonymizer
anonymizer = create_anonymizer_from_config()

# Test sentences for each category
test_cases = {
    'gender': "The male engineer and female designer worked together. He said she was talented.",
    'race_ethnicity': "The team included Asian, African, Hispanic, and Caucasian members.",
    'age': "Young millennials and elderly baby boomers have different perspectives.",
    'disability': "The disabled employee needed wheelchair access, while able-bodied workers used stairs.",
    'marital_status': "Single bachelor, married couple, and divorced parent attended the meeting.",
    'nationality': "American citizens and foreign immigrants work in our diverse office.",
    'sexual_orientation': "Gay, lesbian, and heterosexual employees celebrated pride month.",
    'religion': "Christian, Muslim, Jewish, Hindu, and atheist colleagues respect each other.",
    'political_affiliation': "Conservative Republicans and liberal Democrats debated policies.",
    'socioeconomic_background': "Wealthy elite from private schools met working-class scholarship students.",
    'pregnancy_maternity': "Pregnant employee on maternity leave returned after childbirth.",
    'union_membership': "Union members and non-union contractors negotiated collective bargaining.",
    'health_condition': "Employee with depression and anxiety sought mental health treatment.",
    'criminal_background': "Criminal record from past conviction versus clean record applicant."
}

print("\n1. Testing each bias category:")
print("-" * 40)

for category, text in test_cases.items():
    print(f"\nCategory: {category}")
    print(f"Original: {text}")
    
    # Test with anonymizer
    test_data = {"test_field": text}
    # Add field to always_anonymize for testing
    anonymizer.profile_config.always_anonymize_fields.add("test_field")
    result = anonymizer.anonymize_talent_profile(test_data)
    result_text = result.get("test_field", "")
    
    print(f"Result:   {result_text}")
    
    # Check if bias words were removed
    category_words = BiasWords.get_category_words(category)
    words_found = []
    for word in category_words:
        if word.lower() in result_text.lower():
            words_found.append(word)
    
    if words_found:
        print(f"❌ Still contains: {words_found[:5]}")  # Show first 5
    else:
        print(f"✅ All {category} bias words removed")

print("\n2. Testing mixed bias text:")
print("-" * 40)

mixed_text = """
The young Asian female engineer, a single mother from a working-class background,
overcame her disability and depression to become successful. Despite being an immigrant
Muslim with liberal political views, she earned respect from the elderly white male
CEO who came from wealthy private school background.
"""

print(f"Original: {mixed_text}")
test_data = {"test_field": mixed_text}
result = anonymizer.anonymize_talent_profile(test_data)
result_text = result.get("test_field", "")
print(f"\nResult: {result_text}")

# Analyze what was detected
analysis = anonymizer.analyzer.analyze(text=mixed_text, language='en', score_threshold=0.5)
categories_detected = set()
for r in analysis:
    if 'BIAS' in r.entity_type:
        categories_detected.add(r.entity_type)

print(f"\nCategories detected: {sorted(categories_detected)}")

print("\n3. Bias word statistics:")
print("-" * 40)
stats = BiasWords.get_statistics()
for key, value in stats.items():
    print(f"{key}: {value}")
