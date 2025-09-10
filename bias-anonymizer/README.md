# Bias Anonymizer

A powerful Python library for detecting and anonymizing bias-inducing information and PII in structured JSON data using Microsoft Presidio.

## Features

- 🔍 **Comprehensive Bias Detection**: Detects 14+ categories of potential bias including gender, race, age, disability, and more
- 🛡️ **PII Protection**: Identifies and removes personal identifiable information
- 🏗️ **Structure Preservation**: Maintains JSON structure while anonymizing only values
- 🎯 **Selective Anonymization**: Choose specific keys to anonymize or process entire JSON
- 🔧 **Highly Configurable**: Customize detection patterns and anonymization strategies
- 📊 **Detailed Reporting**: Generate bias analysis reports with confidence scores

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from source

```bash
# Clone the repository
git clone <repository-url>
cd bias-anonymizer

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Install dependencies only

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

## Quick Start

### Basic Usage

```python
from bias_anonymizer import JSONAnonymizer

# Initialize anonymizer
anonymizer = JSONAnonymizer()

# Sample JSON with bias and PII
data = {
    "employee": {
        "name": "John Smith",
        "bio": "45-year-old white male engineer",
        "email": "john.smith@company.com",
        "skills": ["Python", "Machine Learning"]
    }
}

# Anonymize all values
anonymized = anonymizer.anonymize(data)
print(anonymized)
# Output: {"employee": {"name": "[PERSON]", "bio": "engineer", "email": "[EMAIL]", "skills": ["Python", "Machine Learning"]}}
```

### Selective Anonymization

```python
# Only anonymize specific keys
anonymized = anonymizer.anonymize(
    data, 
    keys_to_anonymize=["bio", "name", "email"]
)

# Or use dot notation for nested keys
anonymized = anonymizer.anonymize(
    data,
    keys_to_anonymize=["employee.bio", "employee.name"]
)
```

### Advanced Configuration

```python
from bias_anonymizer import JSONAnonymizer, AnonymizerConfig

# Custom configuration
config = AnonymizerConfig(
    detect_bias=True,
    detect_pii=True,
    bias_categories=["gender", "age", "race_ethnicity"],
    confidence_threshold=0.7,
    operators={
        "PERSON": "replace",
        "EMAIL": "mask",
        "PHONE_NUMBER": "hash",
        "BIAS_INDICATOR": "remove"
    }
)

anonymizer = JSONAnonymizer(config=config)
```

## CLI Usage

The package includes a command-line interface for easy file processing:

```bash
# Anonymize a JSON file
bias-anonymizer input.json -o output.json

# Only anonymize specific keys
bias-anonymizer input.json -o output.json -k name,email,bio

# Generate bias report
bias-anonymizer input.json --report

# Specify configuration file
bias-anonymizer input.json -c config.yaml -o output.json

# Process entire directory
bias-anonymizer --dir ./data --output-dir ./anonymized
```

## Configuration

### Using Configuration Files

Create a `config.yaml` file:

```yaml
# Anonymization settings
detect_bias: true
detect_pii: true

# Specific bias categories to detect
bias_categories:
  - gender
  - race_ethnicity
  - age
  - disability

# Detection settings
confidence_threshold: 0.7
language: en

# Anonymization operators
operators:
  PERSON: replace
  EMAIL: mask
  PHONE_NUMBER: hash
  BIAS_INDICATOR: remove
  
# Replacement values
replacements:
  PERSON: "[REDACTED]"
  EMAIL: "[EMAIL]"
  DEFAULT: ""
```

## API Reference

### JSONAnonymizer

Main class for anonymizing JSON data.

#### Methods

- `anonymize(data, keys_to_anonymize=None, preserve_structure=True)`
  - Anonymizes JSON data
  - Parameters:
    - `data`: Dict or JSON string to anonymize
    - `keys_to_anonymize`: Optional list of keys to process
    - `preserve_structure`: Whether to maintain JSON structure
  - Returns: Anonymized JSON

- `analyze(data, keys_to_analyze=None)`
  - Analyzes JSON for bias and PII without anonymizing
  - Returns: Analysis report with detected entities

- `anonymize_file(input_path, output_path, keys_to_anonymize=None)`
  - Processes JSON files
  
- `anonymize_batch(files, output_dir, keys_to_anonymize=None)`
  - Batch process multiple files

### Configuration Classes

- `AnonymizerConfig`: Main configuration class
- `BiasCategories`: Enum of available bias categories
- `OperatorTypes`: Available anonymization operators

## Bias Categories

The anonymizer detects the following bias categories:

1. **Gender**: Male, female, non-binary terms
2. **Race/Ethnicity**: Racial and ethnic identifiers
3. **Age**: Age-related terms and generations
4. **Disability**: Disability status and related terms
5. **Marital Status**: Marriage and family status
6. **Nationality**: Citizenship and origin
7. **Sexual Orientation**: LGBTQ+ and orientation terms
8. **Religion**: Religious affiliations
9. **Political Affiliation**: Political leanings
10. **Socioeconomic Background**: Class and wealth indicators
11. **Pregnancy/Maternity**: Pregnancy-related terms
12. **Union Membership**: Labor organization terms
13. **Health Conditions**: Medical and health terms
14. **Criminal Background**: Legal history terms

## Examples

See the `examples/` directory for more detailed examples:

- `basic_usage.py`: Simple anonymization examples
- `employee_profiles.py`: Employee data anonymization
- `batch_processing.py`: Processing multiple files
- `custom_config.py`: Advanced configuration examples
- `api_integration.py`: REST API integration example

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bias_anonymizer

# Run specific test file
pytest tests/test_anonymizer.py
```

## Performance

- Processes ~1000 JSON objects/second on average hardware
- Memory efficient streaming for large files
- Parallel processing support for batch operations

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

## License

MIT License - see `LICENSE` file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the documentation
- See examples in the `examples/` directory

## Acknowledgments

Built on top of:
- [Microsoft Presidio](https://github.com/microsoft/presidio) - PII detection framework
- [spaCy](https://spacy.io/) - NLP library
- Additional open-source libraries

## Roadmap

- [ ] Support for additional file formats (CSV, XML, YAML)
- [ ] Machine learning-based bias detection
- [ ] Custom entity training interface
- [ ] Real-time streaming support
- [ ] Integration with popular data platforms
- [ ] Multi-language support
