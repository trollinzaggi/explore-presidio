#!/usr/bin/env python3
"""
Verify all bias words are included and test detection.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bias_anonymizer.bias_words import BiasWords

print("=" * 60)
print("VERIFICATION: All Bias Words Included")
print("=" * 60)

# Count expected words per category
expected_counts = {
    'male_words': 18,  # Including duplicates
    'female_words': 18,
    'gender_neutral_words': 12,
    'european_words': 12,
    'african_words': 12,
    'asian_words': 12,
    'hispanic_words': 12,
    'middle_eastern_words': 12,
    'young_age_words': 12,
    'middle_age_words': 12,
    'older_age_words': 11,
    'disabled_words': 13,
    'able_bodied_words': 11,
    'single_status_words': 12,
    'married_status_words': 12,
    'parent_status_words': 12,
    'domestic_nationality_words': 11,
    'foreign_nationality_words': 12,
    'heterosexual_words': 11,
    'lgbtq_words': 12,
    'christian_words': 12,
    'muslim_words': 12,
    'jewish_words': 12,
    'eastern_religion_words': 12,
    'secular_words': 12,
    'conservative_words': 11,
    'liberal_words': 11,
    'wealthy_words': 12,
    'working_class_words': 11,
    'pregnancy_maternity_words': 12,
    'union_words': 11,
    'non_union_words': 11,
    'health_condition_words': 12,
    'criminal_background_words': 12,
    'clean_background_words': 11
}

print("\n1. Checking word counts per category:")
print("-" * 40)

all_correct = True
for category_name, expected_count in expected_counts.items():
    actual_words = getattr(BiasWords, category_name, [])
    actual_count = len(actual_words)
    
    if actual_count >= expected_count - 1:  # Allow for minor deduplication
        status = "✅"
    else:
        status = "❌"
        all_correct = False
    
    print(f"{category_name:30s}: {actual_count:3d} words {status}")

print("\n2. Checking all categories in get_all_categories():")
print("-" * 40)

all_categories = BiasWords.get_all_categories()
print(f"Total categories: {len(all_categories)}")

expected_categories = [
    'gender', 'race_ethnicity', 'age', 'disability', 'marital_status',
    'nationality', 'sexual_orientation', 'religion', 'political_affiliation',
    'socioeconomic_background', 'pregnancy_maternity', 'union_membership',
    'health_condition', 'criminal_background'
]

for cat in expected_categories:
    if cat in all_categories:
        word_count = len(all_categories[cat])
        print(f"✅ {cat:25s}: {word_count:3d} words")
    else:
        print(f"❌ {cat:25s}: MISSING")
        all_correct = False

print("\n3. Total word statistics:")
print("-" * 40)
stats = BiasWords.get_statistics()
print(f"Total unique words: {stats.get('total_unique_words', 0)}")
print(f"Total categories: {stats.get('total_categories', 0)}")

print("\n4. Sample words from each category:")
print("-" * 40)
for category, words in all_categories.items():
    sample = words[:3] if len(words) >= 3 else words
    print(f"{category}: {sample}")

if all_correct:
    print("\n✅ All bias words are properly included!")
else:
    print("\n❌ Some categories may be missing words")

print("\n5. Testing specific words that should be detected:")
print("-" * 40)

test_words = [
    ("he", "gender"),
    ("gay", "sexual_orientation"),
    ("Muslim", "religion"),
    ("wealthy", "socioeconomic_background"),
    ("pregnant", "pregnancy_maternity"),
    ("union", "union_membership"),
    ("depression", "health_condition"),
    ("conviction", "criminal_background"),
    ("disabled", "disability"),
    ("young", "age"),
    ("Hispanic", "race_ethnicity"),
    ("immigrant", "nationality")
]

for word, expected_category in test_words:
    identified_category = BiasWords.identify_bias_category(word)
    if identified_category == expected_category:
        print(f"✅ '{word}' correctly identified as {expected_category}")
    else:
        print(f"❌ '{word}' identified as {identified_category}, expected {expected_category}")
