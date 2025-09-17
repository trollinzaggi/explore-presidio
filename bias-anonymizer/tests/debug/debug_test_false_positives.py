#!/usr/bin/env python3
"""
Debug what the test is actually detecting as phone/email
"""

import sys
import os
import json
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bias_anonymizer.config_loader import create_anonymizer_from_config
from test_comprehensive_config import create_comprehensive_test_profile

print("=" * 60)
print("DEBUGGING FALSE POSITIVES IN TEST")
print("=" * 60)

# Create and anonymize the profile
anonymizer = create_anonymizer_from_config()
test_profile = create_comprehensive_test_profile()
anonymized_profile = anonymizer.anonymize_talent_profile(test_profile)

# Convert to JSON string like the test does
anon_json = json.dumps(anonymized_profile, indent=2)

# Check for patterns
print("\n1. Checking for phone patterns:")
print("-" * 40)

phone_patterns = [
    r'\b\d{3}-\d{3}-\d{4}\b',  # 555-123-4567
    r'\b\d{3}-\d{4}\b',  # 555-1234
    r'(?i)\b\d{3}-[A-Z]{2}-[A-Z]{4}\b',  # 555-HR-HELP
]

for pattern in phone_patterns:
    matches = re.findall(pattern, anon_json, re.IGNORECASE if '(?i)' in pattern else 0)
    if matches:
        print(f"Pattern: {pattern}")
        print(f"  Matches found: {matches[:5]}")  # Show first 5

print("\n2. Checking for email patterns:")
print("-" * 40)

email_pattern = r'\b[\w._%+-]+@[\w.-]+\.[A-Z|a-z]{2,}\b'
email_matches = re.findall(email_pattern, anon_json)
if email_matches:
    print(f"Email pattern matches: {email_matches[:5]}")

print("\n3. Looking for specific problematic text:")
print("-" * 40)

# Search for specific strings
problem_strings = ['555-HR-HELP', '555-1234', '@', '.com']
for s in problem_strings:
    if s in anon_json:
        # Find context
        idx = anon_json.find(s)
        start = max(0, idx - 50)
        end = min(len(anon_json), idx + 50)
        print(f"Found '{s}' at position {idx}:")
        print(f"  Context: ...{anon_json[start:end]}...")

print("\n4. Checking specific fields that might have issues:")
print("-" * 40)

# Check specific fields
fields_to_check = [
    ('core.workLocation.country', anonymized_profile.get('core', {}).get('workLocation', {}).get('country')),
    ('experience.experiences[0].company', anonymized_profile.get('experience', {}).get('experiences', [{}])[0].get('company')),
]

for field_name, value in fields_to_check:
    if value:
        print(f"{field_name}:")
        print(f"  Value: {value}")
        # Check if it contains patterns
        if re.search(r'\b\d{3}-[A-Z]{2}-[A-Z]{4}\b', str(value), re.IGNORECASE):
            print(f"  ⚠️ Contains phone pattern!")
        if '@' in str(value):
            print(f"  ⚠️ Contains @ symbol!")
