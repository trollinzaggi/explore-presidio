# Microsoft Presidio Research Document
## Anonymizing Employee Talent Profiles for Bias Mitigation

### Table of Contents
1. [Executive Summary](#executive-summary)
2. [Introduction to Microsoft Presidio](#introduction-to-microsoft-presidio)
3. [Core Components](#core-components)
4. [PII Detection Methods](#pii-detection-methods)
5. [Anonymization Techniques](#anonymization-techniques)
6. [Handling JSON and Structured Data](#handling-json-and-structured-data)
7. [Custom Entity Recognition for Employee Data](#custom-entity-recognition-for-employee-data)
8. [Implementation Strategy](#implementation-strategy)
9. [Best Practices and Considerations](#best-practices-and-considerations)
10. [Code Examples](#code-examples)

---

## Executive Summary

Microsoft Presidio is an open-source framework specifically designed for detecting, redacting, masking, and anonymizing sensitive data (PII) across text, images, and structured data formats. For employee talent profiles stored in multi-level JSON structures, Presidio offers:

- **Comprehensive PII detection** using NLP, pattern matching, and custom rules
- **Support for structured/semi-structured data** including JSON and nested objects
- **Custom entity recognizers** for employee-specific identifiers
- **Multiple anonymization operators** (replace, mask, encrypt, hash, redact)
- **Extensibility** for domain-specific requirements
- **Bias mitigation** through systematic removal of identifying information

The framework is particularly well-suited for anonymizing employee data to ensure fair candidate matching while maintaining data utility.

---

## Introduction to Microsoft Presidio

Presidio (from Latin "praesidium" meaning "protection" or "garrison") is a Microsoft-developed SDK that democratizes de-identification technologies. It provides:

### Key Features
- **Multi-method PII detection**: Combines Named Entity Recognition (NER), regex patterns, checksums, and context analysis
- **Language support**: Multiple languages with customizable NLP engines (spaCy, Stanza, Transformers)
- **Scalability**: From Python packages to Docker containers and Kubernetes deployments
- **Transparency**: Explainable detection decisions with logging capabilities
- **Extensibility**: Easy addition of custom recognizers and anonymization methods

### Architecture Overview
```
Input Data → Analyzer Engine → Detection Results → Anonymizer Engine → Anonymized Output
                ↑                                           ↑
          Custom Recognizers                        Custom Operators
```

---

## Core Components

### 1. Presidio Analyzer
The Analyzer is responsible for detecting PII entities in text. It orchestrates multiple recognizers:

- **Built-in recognizers**: PERSON, EMAIL, PHONE_NUMBER, LOCATION, DATE, etc.
- **Custom recognizers**: Employee ID, Department codes, Project names, etc.
- **External services**: Integration with Azure AI Language, AWS Comprehend

### 2. Presidio Anonymizer
The Anonymizer replaces detected PII with anonymized values using operators:

- **Replace**: Substitute with fixed or generated values
- **Mask**: Replace characters with symbols (e.g., `****`)
- **Redact**: Complete removal of the PII
- **Hash**: One-way transformation using SHA256/512
- **Encrypt**: Reversible transformation for deanonymization
- **Custom operators**: User-defined transformation logic

### 3. Presidio Structured (NEW)
A specialized package for handling structured and semi-structured data:

- **JsonDataProcessor**: Handles JSON objects with nested structures
- **PandasDataProcessor**: For tabular data
- **Batch processing**: Efficient handling of large datasets

---

## PII Detection Methods

### 1. Named Entity Recognition (NER)
- Uses pre-trained models (spaCy, BERT, RoBERTa)
- Identifies entities like names, organizations, locations
- Context-aware detection

### 2. Pattern Recognition
- Regular expressions for structured data (SSN, phone numbers, emails)
- Format validation (credit cards, IBANs)
- Checksum verification

### 3. Context Enhancement
- Boosts confidence scores based on surrounding words
- Example: "employee" near an ID increases EMPLOYEE_ID confidence
- Supports external context injection

### 4. Deny-lists and Allow-lists
- **Deny-lists**: Always flag specific terms as PII
- **Allow-lists**: Never flag specific terms (e.g., company names)

---

## Handling JSON and Structured Data

### JSON Support Features

1. **Nested Object Handling**
   - Recursive analysis of nested JSON structures
   - Path-based field identification
   - Preservation of data structure post-anonymization

2. **Selective Field Processing**
   - Specify keys to analyze or skip
   - Pattern-based field selection
   - Context from field names

3. **Batch Processing**
   - Efficient processing of multiple JSON documents
   - Parallel analysis capabilities
   - Memory-efficient streaming

### Implementation with JsonDataProcessor

```python
from presidio_structured import StructuredEngine, JsonAnalysisBuilder
from presidio_structured import JsonDataProcessor

# Initialize engine with JSON processor
json_engine = StructuredEngine(data_processor=JsonDataProcessor())

# Sample employee profile
employee_profile = {
    "employee": {
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@company.com",
            "phone": "555-123-4567"
        },
        "professional": {
            "employee_id": "EMP12345",
            "department": "Engineering",
            "skills": ["Python", "Machine Learning"],
            "experience": [
                {
                    "company": "TechCorp",
                    "duration": "2 years",
                    "role": "Senior Developer"
                }
            ]
        }
    }
}
```

---

## Custom Entity Recognition for Employee Data

### Common Employee-Specific Entities

1. **Employee Identifiers**
   - Employee ID patterns (e.g., EMP[0-9]{5})
   - Badge numbers
   - Internal usernames

2. **Organizational Data**
   - Department codes
   - Project identifiers
   - Team names
   - Manager references

3. **Performance Metrics**
   - Review scores patterns
   - Ranking identifiers
   - Bonus/compensation references

### Creating Custom Recognizers

```python
from presidio_analyzer import Pattern, PatternRecognizer

class EmployeeIdRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern(
                name="employee_id_pattern",
                regex=r'\bEMP[0-9]{5}\b',
                score=0.9
            )
        ]
        super().__init__(
            supported_entity="EMPLOYEE_ID",
            patterns=patterns,
            context=["employee", "id", "emp", "identifier", "badge"]
        )

# Department Code Recognizer
dept_recognizer = PatternRecognizer(
    supported_entity="DEPARTMENT_CODE",
    patterns=[Pattern(r'\b(ENG|FIN|HR|MKT)-[0-9]{3}\b', score=0.8)],
    context=["department", "dept", "team", "division"]
)
```

---

## Implementation Strategy

### Phase 1: Analysis and Mapping
1. **Profile Structure Analysis**
   - Map JSON schema
   - Identify all PII-containing fields
   - Document nested structures

2. **Entity Identification**
   - List standard PII entities
   - Define custom employee entities
   - Create entity-field mapping

### Phase 2: Custom Recognizer Development
1. **Pattern Definition**
   - Regex patterns for structured IDs
   - Validation rules
   - Context words

2. **Testing and Validation**
   - Sample data testing
   - False positive/negative analysis
   - Confidence threshold tuning

### Phase 3: Anonymization Configuration
1. **Operator Selection**
   - Choose appropriate operators per entity type
   - Define replacement strategies
   - Configure reversibility requirements

2. **Consistency Management**
   - Maintain referential integrity
   - Consistent anonymization across documents
   - Preserve data relationships

### Phase 4: Integration
1. **Pipeline Development**
   - Input validation
   - Batch processing setup
   - Error handling

2. **Performance Optimization**
   - Parallel processing
   - Caching strategies
   - Memory management

---

## Best Practices and Considerations

### 1. Data Quality
- **Pre-processing**: Clean and normalize data before anonymization
- **Validation**: Verify JSON structure integrity
- **Post-processing**: Validate anonymized output maintains required structure

### 2. Bias Mitigation Strategies
- **Complete Removal**: Remove all demographic indicators
- **Generalization**: Replace specific values with categories
- **Consistent Application**: Apply same rules across all profiles
- **Audit Trail**: Log anonymization decisions for transparency

### 3. Performance Considerations
- **Batch Size**: Optimize for memory and speed
- **Parallel Processing**: Use multiprocessing for large datasets
- **Caching**: Cache recognizer results for repeated patterns

### 4. Security and Privacy
- **No Guarantees**: Presidio reduces risk but doesn't guarantee 100% PII removal
- **Layered Protection**: Combine with other security measures
- **Regular Updates**: Keep recognizers updated with new patterns
- **Testing**: Regular testing with synthetic and real data

### 5. Reversibility Requirements
- **Encryption**: For data that needs recovery
- **Mapping Tables**: Store original-anonymous mappings securely
- **Audit Compliance**: Maintain compliance with regulations

---

## Code Examples

### Complete Employee Profile Anonymization Pipeline

```python
import json
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_structured import StructuredEngine, JsonAnalysisBuilder
from faker import Faker

# Initialize components
fake = Faker()
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
json_engine = StructuredEngine()

# Add custom recognizers
def setup_custom_recognizers(analyzer):
    """Add employee-specific recognizers"""
    
    # Employee ID Recognizer
    emp_id_recognizer = PatternRecognizer(
        supported_entity="EMPLOYEE_ID",
        patterns=[Pattern(r'\bEMP[0-9]{5}\b', score=0.9)],
        context=["employee", "id", "identifier"]
    )
    
    # Performance Rating Recognizer
    rating_recognizer = PatternRecognizer(
        supported_entity="PERFORMANCE_RATING",
        patterns=[Pattern(r'\b[A-E][1-5]\b', score=0.7)],
        context=["rating", "performance", "review", "score"]
    )
    
    # Salary/Compensation Recognizer
    salary_recognizer = PatternRecognizer(
        supported_entity="COMPENSATION",
        patterns=[
            Pattern(r'\$[0-9]{1,3},[0-9]{3}', score=0.8),
            Pattern(r'\b[0-9]{5,7}\s*(USD|EUR|GBP)', score=0.8)
        ],
        context=["salary", "compensation", "pay", "wage", "bonus"]
    )
    
    # Add recognizers to registry
    analyzer.registry.add_recognizer(emp_id_recognizer)
    analyzer.registry.add_recognizer(rating_recognizer)
    analyzer.registry.add_recognizer(salary_recognizer)
    
    return analyzer

# Define anonymization operators
def get_anonymization_operators():
    """Configure anonymization operators for different entity types"""
    
    return {
        "PERSON": OperatorConfig("replace", {"new_value": "CANDIDATE"}),
        "EMAIL_ADDRESS": OperatorConfig("mask", {
            "type": "mask",
            "masking_char": "*",
            "chars_to_mask": 10,
            "from_end": False
        }),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "XXX-XXX-XXXX"}),
        "EMPLOYEE_ID": OperatorConfig("hash", {"hash_type": "sha256"}),
        "DATE_TIME": OperatorConfig("replace", {"new_value": "DATE_REDACTED"}),
        "LOCATION": OperatorConfig("replace", {"new_value": "LOCATION_REDACTED"}),
        "ORGANIZATION": OperatorConfig("keep", {}),  # Keep company names
        "COMPENSATION": OperatorConfig("replace", {"new_value": "CONFIDENTIAL"}),
        "PERFORMANCE_RATING": OperatorConfig("keep", {}),  # Keep for matching
        "DEFAULT": OperatorConfig("redact", {})
    }

# Main anonymization function
def anonymize_employee_profile(profile_json, custom_fields_to_skip=None):
    """
    Anonymize employee profile JSON
    
    Args:
        profile_json: Employee profile as JSON/dict
        custom_fields_to_skip: List of field paths to skip
        
    Returns:
        Anonymized profile maintaining structure
    """
    
    # Setup
    analyzer = setup_custom_recognizers(AnalyzerEngine())
    operators = get_anonymization_operators()
    
    # Fields to always preserve
    fields_to_skip = [
        "skills",
        "certifications",
        "education.degree",
        "experience.role",
        "preferences"
    ]
    
    if custom_fields_to_skip:
        fields_to_skip.extend(custom_fields_to_skip)
    
    # Generate analysis
    json_analysis = JsonAnalysisBuilder().generate_analysis(
        profile_json,
        language="en"
    )
    
    # Perform anonymization
    anonymized = json_engine.anonymize(
        profile_json,
        json_analysis,
        operators=operators
    )
    
    return anonymized

# Example usage
if __name__ == "__main__":
    
    # Sample employee profile
    employee_profile = {
        "metadata": {
            "profile_id": "PROF-2024-001",
            "last_updated": "2024-03-15",
            "version": "1.0"
        },
        "employee": {
            "personal": {
                "name": "Jane Smith",
                "email": "jane.smith@techcorp.com",
                "phone": "555-123-4567",
                "address": "123 Main St, San Francisco, CA",
                "date_of_birth": "1985-06-15",
                "employee_id": "EMP12345"
            },
            "professional": {
                "current_role": "Senior Software Engineer",
                "department": "Engineering",
                "manager": "John Manager",
                "tenure_years": 5,
                "performance_rating": "A2",
                "salary": "$125,000"
            },
            "skills": {
                "technical": ["Python", "AWS", "Machine Learning", "Docker"],
                "soft": ["Leadership", "Communication", "Problem Solving"]
            },
            "experience": [
                {
                    "company": "TechCorp",
                    "role": "Senior Software Engineer",
                    "duration": "2019-present",
                    "achievements": [
                        "Led team of 5 developers",
                        "Reduced deployment time by 40%"
                    ]
                },
                {
                    "company": "StartupXYZ",
                    "role": "Software Engineer",
                    "duration": "2016-2019",
                    "location": "New York, NY"
                }
            ],
            "education": [
                {
                    "degree": "MS Computer Science",
                    "institution": "Stanford University",
                    "year": "2016"
                },
                {
                    "degree": "BS Computer Science",
                    "institution": "UC Berkeley",
                    "year": "2014"
                }
            ]
        }
    }
    
    # Anonymize the profile
    anonymized_profile = anonymize_employee_profile(employee_profile)
    
    # Save anonymized profile
    with open('anonymized_employee_profile.json', 'w') as f:
        json.dump(anonymized_profile, f, indent=2)
    
    print("Profile anonymized successfully!")
    print(json.dumps(anonymized_profile, indent=2))
```

### Batch Processing Multiple Profiles

```python
from presidio_analyzer import BatchAnalyzerEngine
from presidio_anonymizer import BatchAnonymizerEngine
import concurrent.futures

def batch_anonymize_profiles(profiles_list, max_workers=4):
    """
    Anonymize multiple employee profiles in parallel
    
    Args:
        profiles_list: List of employee profile dictionaries
        max_workers: Number of parallel workers
        
    Returns:
        List of anonymized profiles
    """
    
    batch_analyzer = BatchAnalyzerEngine(analyzer_engine=analyzer)
    batch_anonymizer = BatchAnonymizerEngine(anonymizer_engine=anonymizer)
    
    anonymized_profiles = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all profiles for processing
        futures = []
        for profile in profiles_list:
            future = executor.submit(
                anonymize_employee_profile, 
                profile
            )
            futures.append(future)
        
        # Collect results
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                anonymized_profiles.append(result)
            except Exception as e:
                print(f"Error processing profile: {e}")
    
    return anonymized_profiles
```

### Validation and Quality Checks

```python
def validate_anonymization(original, anonymized):
    """
    Validate that anonymization was successful
    
    Args:
        original: Original profile
        anonymized: Anonymized profile
        
    Returns:
        Validation report
    """
    
    report = {
        "structure_preserved": True,
        "pii_removed": [],
        "fields_preserved": [],
        "warnings": []
    }
    
    # Check structure preservation
    def check_structure(orig, anon, path=""):
        if type(orig) != type(anon):
            report["structure_preserved"] = False
            report["warnings"].append(f"Structure mismatch at {path}")
            return
            
        if isinstance(orig, dict):
            for key in orig:
                if key not in anon:
                    report["warnings"].append(f"Missing key {path}.{key}")
                else:
                    check_structure(orig[key], anon[key], f"{path}.{key}")
        elif isinstance(orig, list):
            if len(orig) != len(anon):
                report["warnings"].append(f"List length mismatch at {path}")
    
    check_structure(original, anonymized)
    
    # Check PII removal
    sensitive_patterns = [
        (r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', 'name'),
        (r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', 'email'),
        (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'phone'),
        (r'\bEMP[0-9]{5}\b', 'employee_id')
    ]
    
    import re
    anon_str = json.dumps(anonymized)
    
    for pattern, pii_type in sensitive_patterns:
        matches = re.findall(pattern, anon_str)
        if matches:
            report["warnings"].append(f"Potential {pii_type} found: {matches[:3]}")
        else:
            report["pii_removed"].append(pii_type)
    
    return report
```

---

## Conclusion

Microsoft Presidio provides a robust, extensible framework for anonymizing employee talent profiles stored in JSON format. Its key strengths for this use case include:

1. **Native JSON support** through the presidio-structured package
2. **Custom entity recognition** for employee-specific identifiers
3. **Multiple anonymization techniques** to balance privacy and utility
4. **Scalability** for large-scale batch processing
5. **Extensibility** to adapt to evolving requirements

### Recommended Next Steps

1. **Analyze your JSON schema**: Map all fields containing PII
2. **Define custom entities**: Create recognizers for employee-specific patterns
3. **Test with sample data**: Validate detection accuracy
4. **Configure anonymization operators**: Choose appropriate methods per entity
5. **Implement validation**: Ensure data quality post-anonymization
6. **Deploy incrementally**: Start with non-critical data
7. **Monitor and refine**: Continuously improve based on results

### Important Considerations

- **No 100% guarantee**: Always combine with other security measures
- **Regular updates**: Keep patterns and recognizers current
- **Compliance**: Ensure approach meets regulatory requirements
- **Reversibility**: Plan for scenarios requiring data recovery
- **Performance**: Optimize for your scale requirements

By following this research and implementation guide, you can effectively use Microsoft Presidio to anonymize employee talent profiles, mitigating bias while maintaining the utility of the data for fair candidate matching.
