#!/usr/bin/env python3
"""
Example: Using configuration files with the anonymizer
Shows how to load and use different configuration strategies
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bias_anonymizer.config_loader import (
    create_anonymizer_from_config,
    get_config_summary,
    validate_config
)
from bias_anonymizer.anonymizer_wrapper import BiasAnonymizer

# Test profile
test_profile = {
    "core": {
        "businessTitle": "Senior Hispanic female engineer from wealthy family",
        "jobCode": "ENG_001",
        "rank": {
            "description": "White male dominated position"
        }
    },
    "experience": {
        "experiences": [{
            "company": "Stanford University",
            "description": "Led team of young Asian and Black engineers",
            "jobTitle": "Senior Engineering Manager"
        }]
    }
}

def test_default_config():
    """Test using the default_config.yaml file."""
    print("\n" + "="*60)
    print("TEST: Using default_config.yaml")
    print("="*60)
    
    # Load configuration summary
    summary = get_config_summary()
    print("\nConfiguration Summary:")
    print(f"  Primary bias strategy: {summary['primary_bias_strategy']}")
    print(f"  Total entity types configured: {summary['total_entity_types']}")
    print(f"  Operator distribution: {summary['operator_counts']}")
    
    # Validate config
    try:
        validate_config()
        print("  ✓ Configuration is valid")
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return
    
    # Create anonymizer from config
    anonymizer = create_anonymizer_from_config()
    
    # Test anonymization
    result = anonymizer.anonymize_talent_profile(test_profile)
    
    print("\nAnonymization Results:")
    print(f"  Original businessTitle: {test_profile['core']['businessTitle']}")
    print(f"  Anonymized businessTitle: {result['core']['businessTitle']}")
    print(f"  Original description: {test_profile['experience']['experiences'][0]['description']}")
    print(f"  Anonymized description: {result['experience']['experiences'][0]['description']}")

def test_programmatic_config():
    """Test using programmatic configuration."""
    print("\n" + "="*60)
    print("TEST: Programmatic Configuration")
    print("="*60)
    
    # Test different strategies
    strategies = ['redact', 'replace']
    
    for strategy in strategies:
        print(f"\n{strategy.upper()} Strategy:")
        anonymizer = BiasAnonymizer(strategy=strategy)
        result = anonymizer.anonymize(test_profile)
        
        print(f"  businessTitle: {result['core']['businessTitle']}")
        print(f"  description: {result['experience']['experiences'][0]['description']}")

def create_custom_config():
    """Create and test a custom configuration."""
    print("\n" + "="*60)
    print("TEST: Custom Configuration")
    print("="*60)
    
    # Create custom config file
    custom_config = {
        'detect_bias': True,
        'detect_pii': True,
        'confidence_threshold': 0.8,
        'operators': {
            'GENDER_BIAS': 'replace',
            'RACE_BIAS': 'replace',
            'AGE_BIAS': 'redact',
            'SOCIOECONOMIC_BIAS': 'redact',
            'DEFAULT': 'replace'
        },
        'replacements': {
            'GENDER_BIAS': '[GENDER]',
            'RACE_BIAS': '[ETHNICITY]',
            'DEFAULT': '[REDACTED]'
        }
    }
    
    # Save custom config
    import yaml
    custom_path = Path('custom_config.yaml')
    with open(custom_path, 'w') as f:
        yaml.dump(custom_config, f)
    
    print("\nCustom configuration created with:")
    print("  - Replace gender and race terms with tokens")
    print("  - Redact age and socioeconomic terms")
    
    # Use custom config
    try:
        anonymizer = create_anonymizer_from_config(str(custom_path))
        result = anonymizer.anonymize_talent_profile(test_profile)
        
        print("\nResults with custom config:")
        print(f"  businessTitle: {result['core']['businessTitle']}")
        
    finally:
        # Clean up
        if custom_path.exists():
            custom_path.unlink()

def compare_strategies():
    """Compare all strategies side by side."""
    print("\n" + "="*60)
    print("COMPARISON: All Strategies")
    print("="*60)
    
    test_text = "Senior white male engineer from wealthy family"
    print(f"\nOriginal text: {test_text}")
    print("-" * 40)
    
    simple_profile = {"text": test_text}
    
    # Test each strategy
    strategies = {
        'redact': 'Removes bias words completely',
        'replace': 'Replaces with generic tokens',
    }
    
    for strategy, description in strategies.items():
        anonymizer = BiasAnonymizer(strategy=strategy)
        # For this test, we'll just show the strategy
        print(f"\n{strategy.upper()}: {description}")
        
        # Create a simple test case
        test_case = {
            "core": {"businessTitle": test_text}
        }
        result = anonymizer.anonymize(test_case)
        print(f"  Result: {result['core']['businessTitle']}")

if __name__ == "__main__":
    print("CONFIGURATION SYSTEM DEMO")
    print("Demonstrating different ways to configure the anonymizer")
    
    try:
        # Run all tests
        test_default_config()
        test_programmatic_config()
        create_custom_config()
        compare_strategies()
        
        print("\n" + "="*60)
        print("✅ All configuration tests completed!")
        print("="*60)
        
        print("\nKey Takeaways:")
        print("1. default_config.yaml uses 'redact' for bias terms")
        print("2. You can override configuration programmatically")
        print("3. Custom YAML configs can mix strategies")
        print("4. All configurations use valid Presidio operators")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
