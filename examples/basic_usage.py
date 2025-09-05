"""
Basic usage examples for the bias anonymizer.
"""

import json
from bias_anonymizer import JSONAnonymizer, AnonymizerConfig


def example_simple_anonymization():
    """Simple anonymization of all fields."""
    print("=== Simple Anonymization Example ===\n")
    
    # Sample data with bias and PII
    data = {
        "employee": {
            "name": "John Smith",
            "age": 45,
            "bio": "Senior white male engineer with 20 years experience",
            "email": "john.smith@company.com",
            "phone": "555-123-4567",
            "skills": ["Python", "Machine Learning", "Leadership"]
        }
    }
    
    print("Original data:")
    print(json.dumps(data, indent=2))
    
    # Anonymize
    anonymizer = JSONAnonymizer()
    anonymized = anonymizer.anonymize(data)
    
    print("\nAnonymized data:")
    print(json.dumps(anonymized, indent=2))


def example_selective_anonymization():
    """Anonymize only specific fields."""
    print("\n=== Selective Anonymization Example ===\n")
    
    data = {
        "profile": {
            "personal": {
                "name": "Jane Doe",
                "ethnicity": "Asian American",
                "marital_status": "married with two kids"
            },
            "professional": {
                "title": "Software Engineer",
                "experience": "10 years",
                "certifications": ["AWS", "Kubernetes"]
            }
        }
    }
    
    print("Original data:")
    print(json.dumps(data, indent=2))
    
    # Anonymize only personal fields
    anonymizer = JSONAnonymizer()
    anonymized = anonymizer.anonymize(
        data, 
        keys_to_anonymize=["profile.personal.name", "profile.personal.ethnicity", "profile.personal.marital_status"]
    )
    
    print("\nAnonymized data (only personal fields):")
    print(json.dumps(anonymized, indent=2))


def example_custom_configuration():
    """Use custom configuration for anonymization."""
    print("\n=== Custom Configuration Example ===\n")
    
    data = {
        "candidate": {
            "background": "Young Hispanic woman from working-class family",
            "education": "First-generation college graduate",
            "contact": {
                "email": "maria.garcia@email.com",
                "phone": "555-987-6543"
            }
        }
    }
    
    print("Original data:")
    print(json.dumps(data, indent=2))
    
    # Custom configuration
    config = AnonymizerConfig(
        detect_bias=True,
        detect_pii=True,
        bias_categories=["age", "race_ethnicity", "gender", "socioeconomic_background"],
        operators={
            "EMAIL_ADDRESS": "mask",
            "PHONE_NUMBER": "replace",
            "BIAS_INDICATOR": "remove"
        },
        replacements={
            "PHONE_NUMBER": "[REDACTED_PHONE]"
        }
    )
    
    anonymizer = JSONAnonymizer(config=config)
    anonymized = anonymizer.anonymize(data)
    
    print("\nAnonymized data (custom config):")
    print(json.dumps(anonymized, indent=2))


def example_nested_json():
    """Handle deeply nested JSON structures."""
    print("\n=== Nested JSON Example ===\n")
    
    data = {
        "employees": [
            {
                "id": "EMP001",
                "profile": {
                    "name": "Bob Johnson",
                    "demographics": {
                        "age_group": "baby boomer",
                        "gender": "male",
                        "disability": "uses wheelchair"
                    }
                }
            },
            {
                "id": "EMP002",
                "profile": {
                    "name": "Sarah Williams",
                    "demographics": {
                        "age_group": "millennial",
                        "gender": "female",
                        "disability": "none"
                    }
                }
            }
        ],
        "department": "Engineering"
    }
    
    print("Original data:")
    print(json.dumps(data, indent=2))
    
    # Anonymize all demographic fields
    anonymizer = JSONAnonymizer()
    anonymized = anonymizer.anonymize(data)
    
    print("\nAnonymized data:")
    print(json.dumps(anonymized, indent=2))


def example_analysis_only():
    """Analyze data without anonymizing."""
    print("\n=== Analysis Only Example ===\n")
    
    data = {
        "description": "Looking for a young, energetic Christian male developer. "
                      "Must be from upper-class background and willing to work long hours. "
                      "No disabilities or health conditions.",
        "requirements": {
            "technical": ["Python", "React", "AWS"],
            "other": "US citizen only, non-union preferred"
        }
    }
    
    print("Data to analyze:")
    print(json.dumps(data, indent=2))
    
    # Analyze for bias and PII
    anonymizer = JSONAnonymizer()
    analysis = anonymizer.analyze(data)
    
    print("\nAnalysis Results:")
    print(f"Total entities found: {analysis['total_entities']}")
    print(f"Bias categories: {analysis['bias_categories']}")
    print(f"PII types: {analysis['pii_types']}")
    
    print("\nEntity breakdown:")
    for entity_type, count in analysis['entities_by_type'].items():
        print(f"  {entity_type}: {count}")


if __name__ == "__main__":
    example_simple_anonymization()
    example_selective_anonymization()
    example_custom_configuration()
    example_nested_json()
    example_analysis_only()
