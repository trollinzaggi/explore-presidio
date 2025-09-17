#!/usr/bin/env python3
"""
Final comprehensive test of all bias categories with actual anonymization.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bias_anonymizer.config_loader import create_anonymizer_from_config
from bias_anonymizer.bias_words import BiasWords

print("=" * 60)
print("FINAL TEST: All Bias Categories Detection & Anonymization")
print("=" * 60)

# Create anonymizer
anonymizer = create_anonymizer_from_config()

# Test comprehensive text with multiple bias categories
test_profile = {
    "summary": """
    John Smith, a white male engineer from a wealthy background, graduated from Harvard.
    His wife Mary, a Hispanic woman, is pregnant and on maternity leave. 
    They are both Christian conservatives who attend church regularly.
    Despite his disability (wheelchair user), John remains productive.
    The young millennial couple lives in an affluent neighborhood.
    John has depression but manages it with therapy. No criminal record.
    As a union member, he supports collective bargaining.
    They hired an immigrant nanny who is Muslim and wears hijab.
    Their gay neighbors, a lesbian couple, are atheist liberals.
    The elderly baby boomer CEO is retiring soon.
    """,
    
    "demographics": {
        "gender": "male, father, husband",
        "race": "Caucasian, white, European descent",
        "age": "young, millennial, twenties",
        "marital": "married, spouse, husband",
        "nationality": "American, US citizen, native-born",
        "orientation": "heterosexual, straight",
        "religion": "Christian, Catholic, church-going",
        "political": "conservative, Republican, traditional values",
        "socioeconomic": "wealthy, privileged, upper-class, private school",
        "health": "depression, anxiety, therapy, medication",
        "disability": "disabled, wheelchair user, mobility impaired",
        "criminal": "clean record, law-abiding, trustworthy",
        "union": "union member, collective bargaining, organized labor",
        "maternity": "pregnant wife, maternity leave, expecting"
    }
}

# Add fields to always_anonymize for this test
for field in ["summary", "demographics.gender", "demographics.race", "demographics.age",
              "demographics.marital", "demographics.nationality", "demographics.orientation",
              "demographics.religion", "demographics.political", "demographics.socioeconomic",
              "demographics.health", "demographics.disability", "demographics.criminal",
              "demographics.union", "demographics.maternity"]:
    anonymizer.profile_config.always_anonymize_fields.add(field)

print("\n1. Testing comprehensive summary text:")
print("-" * 40)
print("ORIGINAL:")
print(test_profile["summary"][:200] + "...")

# Anonymize
result = anonymizer.anonymize_talent_profile(test_profile)

print("\nANONYMIZED:")
print(result["summary"][:200] + "...")

# Check what was removed
print("\n2. Checking bias word removal by category:")
print("-" * 40)

categories_to_check = [
    ('gender', ['male', 'wife', 'father', 'husband']),
    ('race_ethnicity', ['white', 'Hispanic', 'Caucasian']),
    ('age', ['young', 'millennial', 'elderly', 'baby boomer']),
    ('disability', ['disability', 'wheelchair user']),
    ('religion', ['Christian', 'Muslim', 'atheist', 'church']),
    ('sexual_orientation', ['gay', 'lesbian', 'heterosexual', 'straight']),
    ('socioeconomic_background', ['wealthy', 'affluent', 'privileged']),
    ('health_condition', ['depression', 'therapy']),
    ('union_membership', ['union', 'collective bargaining']),
    ('pregnancy_maternity', ['pregnant', 'maternity leave'])
]

all_removed = True
for category, test_words in categories_to_check:
    found_words = []
    result_text = str(result).lower()
    for word in test_words:
        if word.lower() in result_text:
            found_words.append(word)
    
    if found_words:
        print(f"❌ {category:25s}: Still contains {found_words}")
        all_removed = False
    else:
        print(f"✅ {category:25s}: All test words removed")

print("\n3. Testing individual demographic fields:")
print("-" * 40)

for key, value in test_profile["demographics"].items():
    original = value
    anonymized = result.get("demographics", {}).get(key, "")
    
    # Count how many words were removed
    original_words = set(original.lower().split())
    anonymized_words = set(anonymized.lower().split())
    removed = original_words - anonymized_words
    
    if len(removed) > 0:
        print(f"✅ {key:15s}: Removed {len(removed)} bias words")
    else:
        print(f"❌ {key:15s}: No words removed")

print("\n4. Statistics:")
print("-" * 40)

# Get total statistics
stats = BiasWords.get_statistics()
print(f"Total bias categories: {stats['total_categories']}")
print(f"Total unique bias words: {stats['total_unique_words']}")

# Analyze what was detected
analysis = anonymizer.analyzer.analyze(
    text=test_profile["summary"], 
    language='en', 
    score_threshold=0.5
)

bias_entities = [r for r in analysis if 'BIAS' in r.entity_type]
pii_entities = [r for r in analysis if 'BIAS' not in r.entity_type]

print(f"Bias entities detected: {len(bias_entities)}")
print(f"PII entities detected: {len(pii_entities)}")

# Group by entity type
entity_counts = {}
for r in analysis:
    entity_counts[r.entity_type] = entity_counts.get(r.entity_type, 0) + 1

print("\nDetected entity types:")
for entity_type, count in sorted(entity_counts.items()):
    print(f"  {entity_type:30s}: {count}")

if all_removed:
    print("\n✅ SUCCESS: All bias categories are being properly detected and removed!")
else:
    print("\n⚠️  Some bias words may still be present - check configuration")

print("\n" + "=" * 60)
print("Test complete!")
