#!/usr/bin/env python3
"""
Diagnostic script to check the anonymizer setup
"""

import sys
import os
from pathlib import Path

print("ANONYMIZER DIAGNOSTIC CHECK")
print("="*60)

# Check Python version
print(f"Python version: {sys.version}")

# Check current directory
print(f"Current directory: {os.getcwd()}")

# Add src to path
src_path = os.path.join(os.getcwd(), 'src')
sys.path.insert(0, src_path)
print(f"Added to path: {src_path}")

# Check for required files
print("\nChecking for required files:")
required_files = [
    "src/bias_anonymizer/__init__.py",
    "src/bias_anonymizer/anonymizer.py",
    "src/bias_anonymizer/talent_profile_anonymizer.py",
    "src/bias_anonymizer/anonymizer_wrapper.py",
    "src/bias_anonymizer/config_loader.py",
    "src/bias_anonymizer/bias_words.py",
    "src/bias_anonymizer/bias_recognizers.py",
    "config/default_config.yaml"
]

for file in required_files:
    path = Path(file)
    if path.exists():
        print(f"  ✓ {file}")
    else:
        print(f"  ✗ {file} - MISSING!")

# Check for files that should NOT exist
print("\nChecking for removed files:")
removed_files = [
    "src/bias_anonymizer/config.py"
]

for file in removed_files:
    path = Path(file)
    if path.exists():
        print(f"  ✗ {file} - SHOULD BE DELETED!")
    else:
        print(f"  ✓ {file} - correctly removed")

# Try imports
print("\n" + "="*60)
print("Testing imports:")

# Test 1: Basic imports
try:
    print("\n1. Testing basic imports...")
    from bias_anonymizer.bias_words import BiasWords
    print("   ✓ BiasWords imported")
except ImportError as e:
    print(f"   ✗ Failed to import BiasWords: {e}")

try:
    from bias_anonymizer.bias_recognizers import GenderBiasRecognizer
    print("   ✓ Bias recognizers imported")
except ImportError as e:
    print(f"   ✗ Failed to import recognizers: {e}")

# Test 2: Core modules
try:
    print("\n2. Testing core modules...")
    from bias_anonymizer.talent_profile_anonymizer import TalentProfileAnonymizer, TalentProfileConfig
    print("   ✓ TalentProfileAnonymizer imported")
except ImportError as e:
    print(f"   ✗ Failed to import TalentProfileAnonymizer: {e}")

try:
    from bias_anonymizer.config_loader import create_anonymizer_from_config
    print("   ✓ config_loader imported")
except ImportError as e:
    print(f"   ✗ Failed to import config_loader: {e}")

# Test 3: Wrapper
try:
    print("\n3. Testing wrapper...")
    from bias_anonymizer.anonymizer_wrapper import BiasAnonymizer
    print("   ✓ BiasAnonymizer wrapper imported")
except ImportError as e:
    print(f"   ✗ Failed to import wrapper: {e}")

# Test basic functionality
print("\n" + "="*60)
print("Testing basic functionality:")

try:
    from bias_anonymizer.anonymizer_wrapper import BiasAnonymizer
    
    test_data = {
        "text": "Senior white male engineer"
    }
    
    # Test with strategy
    print("\n1. Testing with strategy parameter...")
    anonymizer = BiasAnonymizer(strategy="redact")
    result = anonymizer.anonymize(test_data)
    print(f"   Input: {test_data['text']}")
    print(f"   Output: {result['text']}")
    print("   ✓ Basic anonymization works")
    
except Exception as e:
    print(f"   ✗ Basic functionality test failed: {e}")
    import traceback
    traceback.print_exc()

# Check YAML configuration
print("\n" + "="*60)
print("Testing YAML configuration:")

try:
    from bias_anonymizer.config_loader import load_config_from_yaml, get_config_summary
    
    print("\n1. Checking default_config.yaml...")
    config = load_config_from_yaml()
    summary = get_config_summary()
    
    print(f"   Strategy: {summary['anonymization_strategy']}")
    print(f"   Preserve fields: {summary['preserve_fields_count']}")
    print(f"   Anonymize fields: {summary['anonymize_fields_count']}")
    print("   ✓ YAML configuration loads correctly")
    
except FileNotFoundError:
    print("   ⚠ default_config.yaml not found")
    print("   This is OK - wrapper can work without it")
except Exception as e:
    print(f"   ✗ YAML configuration test failed: {e}")

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)

# Summary
print("\nSummary:")
print("- If all checks passed, the system is ready to use")
print("- Run 'python3 -m streamlit run streamlit_app_fixed.py' to start the app")
print("- Run 'python3 test_wrapper_comprehensive.py' for detailed tests")
