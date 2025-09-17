#!/usr/bin/env python3
"""
Test to verify that custom strategy with specific operators works correctly.
Testing if EMAIL gets redacted and PHONE_NUMBER gets replaced as configured.
"""

import sys
import os
import json
import tempfile
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Suppress SSL warning
import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

from bias_anonymizer.anonymizer_wrapper import BiasAnonymizer
from bias_anonymizer.config_loader import create_anonymizer_from_config
from bias_anonymizer.talent_profile_anonymizer import TalentProfileAnonymizer, TalentProfileConfig


def create_custom_strategy_config():
    """Create a config with custom strategy and mixed operators."""
    config = {
        'anonymization_strategy': 'custom',  # Custom strategy
        'detect_bias': True,
        'detect_pii': True,
        'confidence_threshold': 0.7,
        
        # Empty field lists for this test
        'preserve_fields': [],
        'always_anonymize_fields': ['text', 'description', 'notes'],
        
        # Custom operators - mix of redact and replace
        'operators': {
            'EMAIL_ADDRESS': 'redact',      # Should remove completely
            'PHONE_NUMBER': 'replace',      # Should replace with token
            'PERSON': 'replace',             # Should replace with token
            'LOCATION': 'redact',           # Should remove
            'CREDIT_CARD': 'redact',        # Should remove
            'DATE_TIME': 'replace',         # Should replace
            'DEFAULT': 'replace'             # Default behavior
        },
        
        # Replacement tokens (only used when operator is 'replace')
        'replacement_tokens': {
            'EMAIL_ADDRESS': '[EMAIL]',     # Should NOT be used (redact)
            'PHONE_NUMBER': '[PHONE]',      # Should be used
            'PERSON': '[NAME]',              # Should be used
            'LOCATION': '[LOCATION]',       # Should NOT be used (redact)
            'DATE_TIME': '[DATE]',          # Should be used
            'DEFAULT': '[REDACTED]'
        }
    }
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    yaml.dump(config, temp_file)
    temp_file.close()
    
    return temp_file.name


def test_custom_operators():
    """Test if custom strategy respects individual operator settings."""
    print("="*60)
    print("TEST: Custom Strategy with Mixed Operators")
    print("="*60)
    
    # Test data with various PII types
    test_data = {
        "text": "My name is Sam Johnson, my email is sam.sam@sammy.com and my telephone number is 917-234-7890",
        "description": "Contact John Smith at john@example.com or call 555-123-4567",
        "notes": "Meeting on January 15, 2024 at New York office. Credit card 4111-1111-1111-1111"
    }
    
    print("\nOriginal Data:")
    print(json.dumps(test_data, indent=2))
    
    # Create config
    config_path = create_custom_strategy_config()
    
    try:
        # Test with BiasAnonymizer
        print("\n" + "-"*40)
        print("Testing with BiasAnonymizer wrapper:")
        anonymizer = BiasAnonymizer(config_path=config_path)
        result = anonymizer.anonymize(test_data)
        
        print("\nAnonymized Result:")
        print(json.dumps(result, indent=2))
        
        # Analyze what happened
        print("\n" + "-"*40)
        print("ANALYSIS OF RESULTS:")
        
        # Check EMAIL behavior (should be redacted - removed completely)
        if "sam.sam@sammy.com" in result['text']:
            print("❌ EMAIL NOT REDACTED - still present in text")
        elif "[EMAIL]" in result['text']:
            print("❌ EMAIL REPLACED instead of REDACTED - token found")
        elif "my email is  and" in result['text'] or "my email is and" in result['text']:
            print("✅ EMAIL REDACTED correctly (removed)")
        else:
            print(f"⚠️  EMAIL handling unclear: {result['text']}")
        
        # Check PHONE behavior (should be replaced with [PHONE])
        if "917-234-7890" in result['text']:
            print("❌ PHONE NOT REPLACED - still present in text")
        elif "[PHONE]" in result['text']:
            print("✅ PHONE REPLACED correctly with [PHONE]")
        elif "telephone number is  " in result['text']:
            print("❌ PHONE REDACTED instead of REPLACED")
        else:
            print(f"⚠️  PHONE handling unclear: {result['text']}")
        
        # Check PERSON behavior (should be replaced)
        if "Sam Johnson" in result['text']:
            print("❌ PERSON names not replaced")
        elif "[NAME]" in result['text']:
            print("✅ PERSON replaced with [NAME]")
        
        # Check LOCATION behavior (should be redacted)
        if "New York" in result['notes']:
            print("❌ LOCATION not redacted")
        elif "[LOCATION]" in result['notes']:
            print("❌ LOCATION replaced instead of redacted")
        else:
            print("✅ LOCATION redacted (removed)")
        
        # Check CREDIT_CARD behavior (should be redacted)
        if "4111-1111-1111-1111" in result['notes']:
            print("❌ CREDIT_CARD not redacted")
        else:
            print("✅ CREDIT_CARD redacted")
            
    finally:
        Path(config_path).unlink()


def test_expected_behavior():
    """Test your specific example."""
    print("\n" + "="*60)
    print("TEST: Your Specific Example")
    print("="*60)
    
    config = {
        'anonymization_strategy': 'custom',
        'detect_pii': True,
        'detect_bias': False,  # Focus on PII for this test
        'confidence_threshold': 0.7,
        'always_anonymize_fields': ['text'],
        'preserve_fields': [],
        
        'operators': {
            'EMAIL_ADDRESS': 'redact',
            'PHONE_NUMBER': 'replace',
            'PERSON': 'keep',  # Keep names as-is for your example
            'DEFAULT': 'replace'
        },
        
        'replacement_tokens': {
            'EMAIL_ADDRESS': '[EMAIL]',  # Should NOT be used
            'PHONE_NUMBER': '[PHONE_NUMBER]',
            'DEFAULT': '[REDACTED]'
        }
    }
    
    # Save config
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    yaml.dump(config, temp_file)
    config_path = temp_file.name
    temp_file.close()
    
    test_text = {
        "text": "My name is Sam, my email is sam.sam@sammy.com and my telephone number is 917-234-7890"
    }
    
    expected_result = "My name is Sam, my email is  and my telephone number is [PHONE_NUMBER]"
    
    print(f"Original: {test_text['text']}")
    print(f"Expected: {expected_result}")
    
    try:
        anonymizer = BiasAnonymizer(config_path=config_path)
        result = anonymizer.anonymize(test_text)
        actual = result['text']
        
        print(f"Actual:   {actual}")
        
        # Check if it matches expected
        print("\n" + "-"*40)
        if actual.strip() == expected_result.strip():
            print("✅ PERFECT MATCH! Behavior is correct.")
        else:
            print("❌ MISMATCH - Behavior is not as expected")
            
            # Detailed analysis
            if "sam.sam@sammy.com" in actual:
                print("  - Email was not redacted")
            if "[EMAIL]" in actual:
                print("  - Email was replaced instead of redacted")
            if "917-234-7890" in actual:
                print("  - Phone was not replaced")
            if "[PHONE_NUMBER]" not in actual and "[PHONE]" in actual:
                print("  - Phone token is wrong")
                
    finally:
        Path(config_path).unlink()


def test_strategy_differences():
    """Test how different strategies handle the same operators config."""
    print("\n" + "="*60)
    print("TEST: Strategy Impact on Operators")
    print("="*60)
    
    test_text = {"text": "Email: test@example.com, Phone: 555-123-4567"}
    
    # Same operators config, different strategies
    strategies = ['custom', 'replace', 'redact']
    
    for strategy in strategies:
        config = {
            'anonymization_strategy': strategy,
            'detect_pii': True,
            'detect_bias': False,
            'always_anonymize_fields': ['text'],
            
            # These operators should only work with 'custom' strategy
            'operators': {
                'EMAIL_ADDRESS': 'redact',
                'PHONE_NUMBER': 'replace',
                'DEFAULT': 'replace'
            },
            
            'replacement_tokens': {
                'PHONE_NUMBER': '[PHONE]',
                'EMAIL_ADDRESS': '[EMAIL]'
            }
        }
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(config, temp_file)
        config_path = temp_file.name
        temp_file.close()
        
        try:
            anonymizer = BiasAnonymizer(config_path=config_path)
            result = anonymizer.anonymize(test_text)
            
            print(f"\nStrategy: {strategy}")
            print(f"Result: {result['text']}")
            
            # Check if operators were respected
            if strategy == 'custom':
                # Should respect individual operators
                email_redacted = "test@example.com" not in result['text'] and "[EMAIL]" not in result['text']
                phone_replaced = "[PHONE]" in result['text'] or "[PHONE_NUMBER]" in result['text']
                
                if email_redacted and phone_replaced:
                    print("  ✅ Respects individual operators")
                else:
                    print("  ❌ Does NOT respect individual operators correctly")
            else:
                print(f"  ℹ️  Uses {strategy} for everything (ignores individual operators)")
                
        finally:
            Path(config_path).unlink()


def check_implementation():
    """Check how the current implementation handles custom strategy."""
    print("\n" + "="*60)
    print("IMPLEMENTATION CHECK")
    print("="*60)
    
    print("\nChecking TalentProfileAnonymizer code for strategy handling...")
    
    # Let's trace through what should happen
    print("""
Expected flow for 'custom' strategy:
1. TalentProfileAnonymizer._get_operators() is called
2. For each entity:
   - Check self.profile_config.operators[entity_type]
   - Use that specific operator (redact, replace, etc.)
3. Only use replacement_tokens when operator is 'replace'

Current implementation might:
- Override individual operators based on strategy
- Always use strategy instead of checking operators dict
- Need modification to respect 'custom' strategy
""")


def main():
    print("\n🔬 TESTING CUSTOM STRATEGY OPERATOR BEHAVIOR")
    print("Testing if individual operators work correctly with 'custom' strategy\n")
    
    # Run all tests
    test_custom_operators()
    test_expected_behavior()
    test_strategy_differences()
    check_implementation()
    
    print("\n" + "="*60)
    print("CONCLUSION")
    print("="*60)
    print("""
If the tests show that operators are not being respected with 'custom' strategy,
we need to modify TalentProfileAnonymizer._get_operators() to:

1. Check if strategy == 'custom'
2. If yes, use the operators dict as-is
3. If no, apply the strategy to all entities

This would give you fine-grained control over each entity type.
""")


if __name__ == "__main__":
    main()
