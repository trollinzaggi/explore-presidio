# Configuration Guide - Bias Anonymizer

## Overview

The Bias Anonymizer system detects and removes/anonymizes:
- **14 categories of bias** (gender, race, age, disability, etc.)
- **PII (Personally Identifiable Information)** (SSN, phone, email, addresses, etc.)

## Bias Categories Detected

The system detects and removes bias across 14 comprehensive categories:

1. **Gender** - male, female, gender-neutral terms
2. **Race/Ethnicity** - European, African, Asian, Hispanic, Middle Eastern terms  
3. **Age** - young, middle-aged, older age references
4. **Disability** - disabled and able-bodied references
5. **Marital/Family Status** - single, married, parent status terms
6. **Nationality** - domestic and foreign nationality references
7. **Sexual Orientation** - heterosexual and LGBTQ+ terms
8. **Religion** - Christian, Muslim, Jewish, Eastern religions, secular terms
9. **Political Affiliation** - conservative and liberal references
10. **Socioeconomic Background** - wealthy and working-class terms
11. **Pregnancy/Maternity** - pregnancy and maternity-related terms
12. **Union Membership** - union and non-union references
13. **Health Conditions** - mental and physical health conditions
14. **Criminal Background** - criminal record and clean background terms

## Anonymization Strategies

### 1. **CUSTOM** (Default - Recommended)
- **Action**: Different operators for different entity types
- **Example**: 
  - Emails → Masked: `john@example.com` → `****************`
  - Phones → Hashed: `555-1234` → `24886b1e9942f612...`
  - Names → Replaced: `John Smith` → `[NAME]`
  - Bias words → Redacted: `white male` → ` `
- **Use Case**: Production use with appropriate handling per data type

### 2. **REDACT**
- **Action**: Removes all detected text completely
- **Example**: `Senior white male engineer` → `Senior engineer`
- **Use Case**: Maximum privacy, removes all sensitive content

### 3. **REPLACE**
- **Action**: Replaces all detected text with tokens
- **Example**: `John Smith, white male` → `[NAME], [RACE] [GENDER]`
- **Use Case**: Maintain text structure while removing sensitive content

## Configuration File Structure

### Main Configuration: `config/default_config.yaml`

```yaml
# Strategy selection
anonymization_strategy: custom  # Options: custom, redact, replace

# Fields to preserve (never anonymize)
preserve_fields:
  - core.rank.code
  - core.rank.id
  - core.employeeType.code
  - core.jobCode
  # ... (26 fields total)

# Fields to always anonymize  
always_anonymize_fields:
  - core.businessTitle
  - core.rank.description
  - core.employeeType.description
  # ... (39 fields total)

# Special handling fields
special_handling_fields:
  userId: hash
  core.reportingDistance.ceo: categorize
  # ... etc

# Custom operators per entity type (when strategy = custom)
operators:
  # PII operators
  PERSON: replace
  EMAIL_ADDRESS: mask
  PHONE_NUMBER: hash
  LOCATION: replace
  DATE_TIME: replace
  CREDIT_CARD: mask
  IP_ADDRESS: mask
  US_SSN: mask
  
  # Bias operators (all 14 categories)
  GENDER_BIAS: redact
  RACE_BIAS: redact
  AGE_BIAS: redact
  DISABILITY_BIAS: redact
  FAMILY_STATUS_BIAS: redact
  NATIONALITY_BIAS: redact
  SEXUAL_ORIENTATION_BIAS: redact
  RELIGION_BIAS: redact
  POLITICAL_BIAS: redact
  SOCIOECONOMIC_BIAS: redact
  MATERNITY_BIAS: redact
  UNION_BIAS: redact
  HEALTH_BIAS: redact
  CRIMINAL_BIAS: redact

# Replacement tokens (when using replace operator)
replacement_tokens:
  PERSON: "[NAME]"
  LOCATION: "[LOCATION]"
  DATE_TIME: "[DATE]"
  # ... etc
```

## Available Operators

| Operator | Description | Example | Use For |
|----------|-------------|---------|----------|
| **redact** | Removes text completely | `John Smith` → ` ` | Bias words |
| **replace** | Replaces with token | `John Smith` → `[NAME]` | Names, locations |
| **mask** | Masks with asterisks | `john@email.com` → `****************` | Emails, SSN |
| **hash** | Replaces with SHA256 hash | `555-1234` → `24886b1e9942...` | Phone numbers |
| **encrypt** | Encrypts (reversible) | `John Smith` → `encrypted_string` | Reversible anonymization |
| **keep** | Keeps original | `John Smith` → `John Smith` | Testing only |

## Enhanced Recognizers

The system includes enhanced recognizers for better detection:

### Enhanced SSN Recognizer
- Detects: `123-45-6789`, `123 45 6789`, `123456789`
- Confidence threshold: 0.85

### Enhanced Phone Recognizer
- US formats: `(555) 123-4567`, `555-123-4567`, `555.123.4567`
- Short formats: `555-1234`
- Vanity numbers: `555-HR-HELP`, `1-800-FLOWERS`
- International: `+1-555-123-4567`

### Enhanced Address Recognizer
- Street addresses: `123 Main Street`, `456 Park Ave, Apt 4B`
- PO Boxes: `PO Box 123`
- Zip codes: `94105`, `94105-1234`

## Usage Examples

### Python API - Simple Usage
```python
from bias_anonymizer.config_loader import create_anonymizer_from_config

# Use default configuration (custom strategy)
anonymizer = create_anonymizer_from_config()
result = anonymizer.anonymize_talent_profile(your_data)
```

### Python API - Custom Configuration
```python
# Use specific config file
anonymizer = create_anonymizer_from_config("path/to/custom_config.yaml")
result = anonymizer.anonymize_talent_profile(your_data)
```

### Using the Wrapper (Simplified API)
```python
from bias_anonymizer.anonymizer_wrapper import BiasAnonymizer

# Default (custom strategy)
anonymizer = BiasAnonymizer()
result = anonymizer.anonymize(your_data)

# Specific strategy
anonymizer = BiasAnonymizer(strategy="redact")
result = anonymizer.anonymize(your_data)
```

## Field Configuration

### Preserve Fields
These fields are never anonymized (IDs, codes, etc.):
- System identifiers
- Job codes
- Rank codes
- Numerical scores
- Boolean flags

### Always Anonymize Fields
These fields are always processed for PII/bias:
- Descriptions
- Free text fields
- Names and titles
- Contact information
- Biographical data

### Special Handling Fields
Fields with custom processing:
- `userId`: Hashed for consistency
- `reportingDistance`: Categorized (1-2 = "close", 3-4 = "medium", 5+ = "far")
- Date fields: Year only or replaced

## Testing Your Configuration

Run the comprehensive test to verify your configuration:

```bash
cd bias-anonymizer
python3 tests/test_comprehensive_config.py
```

This will show:
- All detected bias categories
- PII detection results
- Operator application per entity type
- Before/after comparison

## Performance Considerations

1. **Batch Processing**: For large datasets, process in batches
2. **Caching**: The analyzer caches NLP models for efficiency
3. **Confidence Thresholds**: Default is 0.5, adjust for precision/recall balance

## Troubleshooting

### Issue: Bias words not being removed
- Check `anonymization_strategy` is set to `custom` or `redact`
- Verify the field is in `always_anonymize_fields`
- Run `verify_bias_words.py` to check word lists

### Issue: PII not detected
- Check confidence threshold (default 0.5)
- Verify enhanced recognizers are loaded
- Run `test_phone_edge_cases.py` for phone number issues

### Issue: Field not being processed
- Check if field is in `preserve_fields` (won't be processed)
- Check if field is in `always_anonymize_fields` (will be processed)
- Fields not in either list are ignored

## Best Practices

1. **Use Custom Strategy** for production - appropriate handling per data type
2. **Test Thoroughly** - Use provided test scripts before deployment
3. **Review Output** - Manually review samples to ensure quality
4. **Monitor Performance** - Large texts may take longer to process
5. **Update Regularly** - Keep bias word lists current with your needs
