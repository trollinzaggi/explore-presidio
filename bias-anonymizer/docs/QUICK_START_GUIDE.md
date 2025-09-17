# 🚀 Bias Anonymizer - Quick Start Guide

## 📋 Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Using in Python Code](#using-in-python-code)
- [Running the Streamlit App](#running-the-streamlit-app)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## 📊 Overview

The Bias Anonymizer removes bias and PII from talent profiles and other HR data:
- **14 bias categories** (gender, race, age, disability, etc.)
- **Enhanced PII detection** (SSN, phones, emails, addresses, names, etc.)
- **Configurable anonymization** (mask, hash, replace, redact)
- **Field-level control** (preserve important fields, anonymize sensitive ones)

---

## 📦 Installation

### Step 1: Clone or Copy the Project
```bash
# Navigate to your projects directory
cd "/Users/bijoykarnani/VS Code/explore-presidio"

# The bias-anonymizer folder should be here
cd bias-anonymizer
```

### Step 2: Install Dependencies
```bash
# Core dependencies
pip install presidio-analyzer presidio-anonymizer
pip install spacy pyyaml
pip install streamlit  # For web interface

# Download spaCy language model (required)
python -m spacy download en_core_web_lg
```

### Step 3: Verify Installation
```bash
# Run the recognizer verification
python3 tests/verify_recognizers.py

# You should see:
# ✅ ALL RECOGNIZERS PROPERLY REGISTERED!
#    Bias categories: 14/14
#    PII types: 8/8
```

---

## ⚡ Quick Start

### Simplest Usage - One Line
```python
from bias_anonymizer.anonymizer_wrapper import anonymize_profile

result = anonymize_profile({"text": "John Smith, white male engineer"})
# Result: {"text": " engineer"}
```

### Basic Script
```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')  # Add src to path

from bias_anonymizer.config_loader import create_anonymizer_from_config

# Create anonymizer with default config
anonymizer = create_anonymizer_from_config()

# Your data
data = {
    "name": "John Smith",
    "description": "Senior white male engineer from Harvard",
    "email": "john@example.com",
    "phone": "555-123-4567"
}

# Anonymize
result = anonymizer.anonymize_talent_profile(data)
print(result)
# Output: {
#   "name": "[NAME]",
#   "description": "Senior engineer from [LOCATION]", 
#   "email": "****************",
#   "phone": "d36e83082288d9f2c98b3f3f87cd317a31e95527cb09972090d3456a7430ad4d"
# }
```

---

## 🐍 Using in Python Code

### Method 1: Using Config Loader (Recommended)
```python
from bias_anonymizer.config_loader import create_anonymizer_from_config

# Use default configuration (custom strategy with appropriate operators per type)
anonymizer = create_anonymizer_from_config()
result = anonymizer.anonymize_talent_profile(your_data)

# Use custom config file
anonymizer = create_anonymizer_from_config("path/to/custom_config.yaml")
result = anonymizer.anonymize_talent_profile(your_data)
```

### Method 2: Using Wrapper (Simplified API)
```python
from bias_anonymizer.anonymizer_wrapper import BiasAnonymizer

# Default strategy (custom)
anonymizer = BiasAnonymizer()
result = anonymizer.anonymize(your_data)

# Specific strategy
anonymizer = BiasAnonymizer(strategy="redact")  # Remove all
result = anonymizer.anonymize(your_data)

anonymizer = BiasAnonymizer(strategy="replace")  # Replace with tokens
result = anonymizer.anonymize(your_data)
```

### Method 3: Direct Functions
```python
from bias_anonymizer.anonymizer_wrapper import anonymize_profile, analyze_profile

# Quick anonymization
result = anonymize_profile(your_data)

# Just analyze (no anonymization)
analysis = analyze_profile(your_data)
print(f"Risk Score: {analysis['risk_score']}/100")
print(f"Bias Categories Found: {analysis['bias_categories_found']}")
print(f"PII Types Found: {analysis['pii_types_found']}")
```

### Real-World Example
```python
import json
from bias_anonymizer.config_loader import create_anonymizer_from_config

# Load your talent profile data
with open('employee_profile.json') as f:
    profile = json.load(f)

# Create anonymizer
anonymizer = create_anonymizer_from_config()

# Analyze first to see what will be anonymized
analysis = anonymizer.analyze_profile(profile)
print(f"Risk Score: {analysis['risk_score']}/100")
print(f"Fields with bias: {len(analysis['fields_with_bias'])}")
print(f"Fields with PII: {len(analysis['fields_with_pii'])}")

# Anonymize
anonymized = anonymizer.anonymize_talent_profile(profile)

# Save result
with open('employee_profile_anonymized.json', 'w') as f:
    json.dump(anonymized, f, indent=2)

print("✅ Profile anonymized and saved!")
```

---

## 🎯 Running the Streamlit App

### Main Production App (Professional UI)
```bash
cd bias-anonymizer
streamlit run streamlit_apps/streamlit_app_professional.py
```

### Alternative Production Version
```bash
streamlit run streamlit_apps/talent_profile_streamlit_app_production.py
```

### Using the App:
1. Open browser to `http://localhost:8501`
2. Select a sample profile or paste your JSON
3. The app uses the strategy from config/default_config.yaml
   - **Custom** (default): Different handling per data type
   - **Redact**: Remove all sensitive content
   - **Replace**: Replace with tokens
   (Note: Strategy cannot be changed in the UI)
4. Click "Anonymize Profile"
5. Download the anonymized result

---

## 🧪 Testing

### Run All Tests
```bash
cd bias-anonymizer

# Comprehensive test of all features
python3 tests/test_comprehensive_config.py

# Test all bias categories
python3 tests/test_all_bias_categories.py

# Verify recognizers
python3 tests/verify_recognizers.py

# Verify bias words
python3 tests/verify_bias_words.py
```

### Test Specific Features
```bash
# Test phone number edge cases
python3 tests/test_phone_edge_cases.py

# Test SSN detection
python3 tests/test_ssn_detection.py

# Final bias test
python3 tests/final_bias_test.py
```

---

## 📁 Project Structure

```
bias-anonymizer/
├── src/
│   └── bias_anonymizer/
│       ├── config_loader.py         # Load and apply YAML configs
│       ├── talent_profile_anonymizer.py  # Main anonymizer class
│       ├── anonymizer_wrapper.py    # Simplified API wrapper
│       ├── bias_recognizers.py      # 14 bias category recognizers
│       ├── bias_words.py            # Comprehensive bias word lists
│       └── enhanced_recognizers.py  # Enhanced PII recognizers
├── config/
│   └── default_config.yaml          # Main configuration
├── tests/
│   ├── test_comprehensive_config.py # Main test suite
│   ├── verify_recognizers.py        # Verify all recognizers
│   └── ...                          # Other tests
├── streamlit_apps/
│   └── talent_profile_streamlit_app.py  # Web interface
└── docs/
    ├── CONFIGURATION_GUIDE.md       # Detailed config documentation
    └── QUICK_START_GUIDE.md          # This file
```

---

## 🔧 Troubleshooting

### Common Issues

#### "No module named 'bias_anonymizer'"
```python
# Add src to Python path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
```

#### spaCy Model Error
```bash
# Download the model
python -m spacy download en_core_web_lg
```

#### SSL Warning
```python
# Suppress the warning
import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')
```

#### Streamlit Not Found
```bash
# Install streamlit
pip install streamlit

# Or use python -m
python -m streamlit run app.py
```

#### Configuration Issues
```bash
# Check config exists
ls config/default_config.yaml

# Verify config is valid
python3 -c "import yaml; yaml.safe_load(open('config/default_config.yaml'))"
```

### Debug Scripts
```bash
# Debug PII handling
python3 tests/debug/debug_pii_handling.py

# Debug specific field
python3 tests/debug/debug_country_field.py

# Check for false positives
python3 tests/debug/debug_test_false_positives.py
```

---

## 🎯 What Gets Anonymized

### Bias Categories (14 total)
- Gender, Race/Ethnicity, Age, Disability
- Marital/Family Status, Nationality
- Sexual Orientation, Religion
- Political Affiliation, Socioeconomic Background  
- Pregnancy/Maternity, Union Membership
- Health Conditions, Criminal Background

### PII Types
- **Names**: Replaced with [NAME]
- **Emails**: Masked with asterisks
- **Phones**: Hashed to 64-char string
- **SSN**: Masked with asterisks
- **Addresses**: Replaced with [LOCATION]
- **Dates**: Replaced with [DATE]
- **Credit Cards**: Masked
- **IP Addresses**: Masked

### Field Control
- **Preserved**: IDs, codes, scores, flags
- **Anonymized**: Descriptions, free text, names, contact info
- **Special**: userId (hashed), dates (year only)

---

## 💡 Tips

1. **Default Config**: The system uses `config/default_config.yaml` which has optimal settings for most use cases

2. **Custom Strategy**: The default "custom" strategy applies appropriate operators per data type (mask emails, hash phones, redact bias)

3. **Performance**: For large datasets, process in batches of 100-1000 records

4. **Validation**: Always run `test_comprehensive_config.py` after configuration changes

5. **Bias Words**: Review `src/bias_anonymizer/bias_words.py` to understand what's being detected

---

## 📞 Support

If issues persist:
1. Run `python3 tests/verify_recognizers.py`
2. Check Python version (3.7+ required)
3. Ensure all dependencies installed
4. Review error messages in test outputs

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] spaCy model downloaded
- [ ] Verification test passes (14/14 bias, 8/8 PII)
- [ ] Comprehensive test passes
- [ ] Can run Streamlit app
- [ ] Can import and use in Python code

You're ready to anonymize! 🚀
