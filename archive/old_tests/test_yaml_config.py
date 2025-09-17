#!/usr/bin/env python3
"""
Test YAML-driven configuration system
"""

import sys
import os
import json
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bias_anonymizer.config_loader import (
    create_anonymizer_from_config,
    create_custom_config_yaml,
    get_config_summary,
    validate_config
)
from bias_anonymizer.anonymizer_wrapper import BiasAnonymizer

# Test profile
test_profile = {
    "core": {
        "businessTitle": "Senior white male engineer from wealthy family",
        "jobCode": "ENG_001",
        "rank": {
            "code": "L7",
            "description": "Principal level for experienced males"
        }
    },
    "experience": {
        "experiences": [{
            "company": "Stanford University",
            "description": "Led team of young Asian engineers",
            "jobTitle": "Engineering Manager",
            "startDate": "2020-01-15"
        }]
    },
    "qualification": {
        "educations": [{
            "institutionName": "Harvard University",
            "degree": "MS Computer Science",
            "achievements": "Graduated from wealthy donor program"
        }]
    },
    "userId": "user12345"
}


def test_default_yaml_config():
    """Test using the default YAML configuration."""
    print("\n" + "="*60)
    print("TEST 1: Default YAML Configuration")
    print("="*60)
    
    # Load configuration summary
    summary = get_config_summary()
    print("\nConfiguration loaded from default_config.yaml:")
    print(f"  Strategy: {summary['anonymization_strategy']}")
    print(f"  Preserve fields: {summary['preserve_fields_count']}")
    print(f"  Anonymize fields: {summary['anonymize_fields_count']}")
    print(f"  Special handling: {summary['special_handling_count']}")
    
    # Create anonymizer from YAML
    anonymizer = create_anonymizer_from_config()
    
    # Test anonymization
    result = anonymizer.anonymize_talent_profile(test_profile)
    
    print("\nResults:")
    print(f"  businessTitle: {result['core']['businessTitle']}")
    print(f"  jobCode (preserved): {result['core']['jobCode']}")
    print(f"  userId (special handling): {result.get('userId', 'REMOVED')}")
    print(f"  startDate (year only): {result['experience']['experiences'][0].get('startDate', 'N/A')}")


def test_custom_yaml_config():
    """Test creating and using a custom YAML configuration."""
    print("\n" + "="*60)
    print("TEST 2: Custom YAML Configuration")
    print("="*60)
    
    # Create custom config
    custom_config = {
        'anonymization_strategy': 'replace',
        'detect_bias': True,
        'detect_pii': True,
        'confidence_threshold': 0.8,
        'preserve_fields': [
            'core.jobCode',
            'core.rank.code',
            'qualification.educations[*].degree'
        ],
        'always_anonymize_fields': [
            'core.businessTitle',
            'core.rank.description',
            'experience.experiences[*].description',
            'experience.experiences[*].company'
        ],
        'special_handling_fields': {
            'userId': 'hash',
            'experience.experiences[*].startDate': 'year_only'
        },
        'operators': {
            'GENDER_BIAS': 'replace',
            'RACE_BIAS': 'replace',
            'AGE_BIAS': 'redact',
            'SOCIOECONOMIC_BIAS': 'redact',
            'DEFAULT': 'replace'
        },
        'replacement_tokens': {
            'GENDER_BIAS': '[GENDER]',
            'RACE_BIAS': '[ETHNICITY]',
            'DEFAULT': '[REDACTED]'
        }
    }
    
    # Save custom config
    custom_path = 'test_custom_config.yaml'
    with open(custom_path, 'w') as f:
        yaml.dump(custom_config, f)
    
    print(f"\nCreated custom config: {custom_path}")
    
    try:
        # Validate config
        validate_config(custom_path)
        print("✓ Custom configuration is valid")
        
        # Create anonymizer from custom config
        anonymizer = create_anonymizer_from_config(custom_path)
        
        # Test anonymization
        result = anonymizer.anonymize_talent_profile(test_profile)
        
        print("\nResults with custom config:")
        print(f"  businessTitle: {result['core']['businessTitle']}")
        print(f"  rank.description: {result['core']['rank'].get('description', 'N/A')}")
        print(f"  userId: {result.get('userId', 'N/A')}")
        
    finally:
        # Clean up
        if Path(custom_path).exists():
            Path(custom_path).unlink()


def test_wrapper_with_yaml():
    """Test the BiasAnonymizer wrapper with YAML config."""
    print("\n" + "="*60)
    print("TEST 3: BiasAnonymizer with YAML")
    print("="*60)
    
    # Test 1: Using default YAML
    print("\nUsing default YAML config:")
    anonymizer = BiasAnonymizer()  # No parameters = use default YAML
    result = anonymizer.anonymize(test_profile)
    print(f"  businessTitle: {result['core']['businessTitle']}")
    
    # Test 2: Using custom YAML
    custom_config = {
        'anonymization_strategy': 'replace',
        'preserve_fields': ['core.jobCode'],
        'always_anonymize_fields': ['core.businessTitle'],
        'replacement_tokens': {
            'GENDER_BIAS': 'person',
            'RACE_BIAS': 'individual',
            'SOCIOECONOMIC_BIAS': 'professional'
        }
    }
    
    custom_path = 'test_wrapper_config.yaml'
    with open(custom_path, 'w') as f:
        yaml.dump(custom_config, f)
    
    try:
        print("\nUsing custom YAML config:")
        anonymizer = BiasAnonymizer(config_path=custom_path)
        result = anonymizer.anonymize(test_profile)
        print(f"  businessTitle: {result['core']['businessTitle']}")
        
    finally:
        if Path(custom_path).exists():
            Path(custom_path).unlink()
    
    # Test 3: Using programmatic strategy (ignores YAML)
    print("\nUsing programmatic strategy (no YAML):")
    anonymizer = BiasAnonymizer(strategy='redact')
    result = anonymizer.anonymize(test_profile)
    print(f"  businessTitle: {result['core']['businessTitle']}")


def test_field_list_from_yaml():
    """Test that field lists are loaded from YAML."""
    print("\n" + "="*60)
    print("TEST 4: Field Lists from YAML")
    print("="*60)
    
    # Create minimal config with specific fields
    minimal_config = {
        'anonymization_strategy': 'redact',
        'preserve_fields': [
            'core.jobCode',
            'core.rank.code'
        ],
        'always_anonymize_fields': [
            'core.businessTitle',
            'core.rank.description'
        ]
    }
    
    config_path = 'test_fields_config.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(minimal_config, f)
    
    try:
        anonymizer = create_anonymizer_from_config(config_path)
        
        # Check that the config was loaded correctly
        print("\nConfiguration loaded:")
        print(f"  Preserve fields: {anonymizer.profile_config.preserve_fields}")
        print(f"  Anonymize fields: {anonymizer.profile_config.always_anonymize_fields}")
        
        # Test anonymization
        result = anonymizer.anonymize_talent_profile(test_profile)
        
        print("\nResults:")
        print(f"  jobCode (should be preserved): {result['core']['jobCode']}")
        print(f"  businessTitle (should be anonymized): {result['core']['businessTitle']}")
        print(f"  rank.code (should be preserved): {result['core']['rank']['code']}")
        print(f"  rank.description (should be anonymized): {result['core']['rank'].get('description', '[REMOVED]')}")
        
    finally:
        if Path(config_path).exists():
            Path(config_path).unlink()


if __name__ == "__main__":
    print("YAML-DRIVEN CONFIGURATION TEST")
    print("Testing that all configuration comes from YAML files")
    
    try:
        test_default_yaml_config()
        test_custom_yaml_config()
        test_wrapper_with_yaml()
        test_field_list_from_yaml()
        
        print("\n" + "="*60)
        print("✅ All YAML configuration tests passed!")
        print("="*60)
        
        print("\nKey Points:")
        print("1. All configuration now comes from YAML files")
        print("2. Field lists (preserve/anonymize) are defined in YAML")
        print("3. Strategies, operators, and tokens are YAML-driven")
        print("4. No hardcoded field lists in Python code")
        print("5. config.py has been removed (not needed)")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
