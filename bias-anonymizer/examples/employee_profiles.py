"""
Example of anonymizing employee profiles.
"""

import json
import sys
import os

# Add src to path
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
except NameError:
    # Fallback if __file__ is not defined
    sys.path.insert(0, os.path.join(os.getcwd(), '..', 'src'))

from bias_anonymizer import JSONAnonymizer, AnonymizerConfig


def anonymize_employee_profile():
    """Complete employee profile anonymization example."""
    
    # Realistic employee profile with various bias indicators
    employee_profile = {
        "employee_id": "EMP-2024-1234",
        "personal_info": {
            "full_name": "Michael Chen",
            "date_of_birth": "1978-03-15",
            "gender": "Male",
            "ethnicity": "Asian",
            "nationality": "US Citizen",
            "marital_status": "Married with three children",
            "address": {
                "street": "123 Oak Street",
                "city": "San Francisco",
                "state": "CA",
                "zip": "94105"
            },
            "emergency_contact": {
                "name": "Lisa Chen",
                "relationship": "Wife",
                "phone": "555-234-5678"
            }
        },
        "professional_info": {
            "job_title": "Senior Software Engineer",
            "department": "Engineering",
            "manager": "Sarah Johnson",
            "hire_date": "2019-06-01",
            "employment_type": "Full-time",
            "salary": "$145,000",
            "performance_rating": "Exceeds Expectations"
        },
        "background": {
            "summary": "Experienced Asian male engineer in his mid-forties. "
                      "Christian background, attends church regularly. "
                      "From middle-class family, first-generation immigrant. "
                      "Recently recovered from back surgery.",
            "education": [
                {
                    "degree": "MS Computer Science",
                    "institution": "Stanford University",
                    "year": "2002"
                },
                {
                    "degree": "BS Computer Engineering",
                    "institution": "UC Berkeley",
                    "year": "2000"
                }
            ],
            "experience": [
                {
                    "company": "TechCorp",
                    "role": "Senior Software Engineer",
                    "duration": "2019-present",
                    "description": "Leading development of cloud infrastructure"
                },
                {
                    "company": "StartupXYZ",
                    "role": "Software Engineer",
                    "duration": "2015-2019",
                    "description": "Full-stack development"
                }
            ]
        },
        "skills_and_qualifications": {
            "technical_skills": [
                "Python", "Java", "JavaScript", "AWS", "Docker", 
                "Kubernetes", "Machine Learning", "System Design"
            ],
            "soft_skills": [
                "Leadership", "Communication", "Problem Solving", 
                "Team Collaboration", "Mentoring"
            ],
            "certifications": [
                "AWS Solutions Architect",
                "Kubernetes Administrator",
                "Scrum Master"
            ],
            "languages": [
                {"language": "English", "proficiency": "Native"},
                {"language": "Mandarin", "proficiency": "Fluent"},
                {"language": "Spanish", "proficiency": "Basic"}
            ]
        },
        "preferences": {
            "work_arrangement": "Hybrid",
            "relocation": "Not willing",
            "travel": "Up to 20%",
            "interests": ["AI/ML", "Cloud Computing", "DevOps"]
        },
        "diversity_info": {
            "veteran_status": "Not a veteran",
            "disability_status": "Recent back surgery, requires ergonomic setup",
            "pronouns": "He/Him"
        }
    }
    
    print("=== EMPLOYEE PROFILE ANONYMIZATION ===\n")
    print("Original Profile (with bias and PII):")
    print(json.dumps(employee_profile, indent=2)[:500] + "...\n")
    
    # Configure anonymizer for employee data
    config = AnonymizerConfig(
        detect_bias=True,
        detect_pii=True,
        operators={
            # PII handling
            "PERSON": "replace",
            "EMAIL_ADDRESS": "mask",
            "PHONE_NUMBER": "replace",
            "DATE_TIME": "replace",
            "LOCATION": "replace",
            "US_SSN": "mask",
            
            # Bias handling - remove completely
            "GENDER_BIAS": "remove",
            "RACE_ETHNICITY_BIAS": "remove",
            "AGE_BIAS": "remove",
            "DISABILITY_BIAS": "remove",
            "RELIGION_BIAS": "remove",
            "MARITAL_STATUS_BIAS": "remove",
            "NATIONALITY_BIAS": "remove",
            "SOCIOECONOMIC_BACKGROUND_BIAS": "remove",
            "HEALTH_CONDITION_BIAS": "remove",
            
            # Keep certain fields
            "PERFORMANCE_RATING": "keep",
            
            # Default action
            "DEFAULT": "replace"
        },
        replacements={
            "PERSON": "[NAME]",
            "PHONE_NUMBER": "[PHONE]",
            "LOCATION": "[LOCATION]",
            "DATE_TIME": "[DATE]",
            "DEFAULT": "[REDACTED]"
        }
    )
    
    # Fields to preserve (job-relevant only)
    fields_to_skip = [
        "employee_id",
        "professional_info.job_title",
        "professional_info.department",
        "professional_info.employment_type",
        "professional_info.performance_rating",
        "skills_and_qualifications.technical_skills",
        "skills_and_qualifications.soft_skills",
        "skills_and_qualifications.certifications",
        "background.education.degree",
        "background.education.institution",
        "background.experience.company",
        "background.experience.role",
        "background.experience.duration",
        "preferences",
    ]
    
    # Initialize anonymizer
    anonymizer = JSONAnonymizer(config=config)
    
    # First, analyze the profile
    print("Analysis of original profile:")
    analysis = anonymizer.analyze(employee_profile)
    print(f"  - Total entities detected: {analysis['total_entities']}")
    print(f"  - Bias categories found: {', '.join(analysis['bias_categories'])}")
    print(f"  - PII types found: {', '.join(analysis['pii_types'])}\n")
    
    # Anonymize the profile
    anonymized_profile = anonymizer.anonymize(employee_profile)
    
    print("Anonymized Profile (bias and PII removed):")
    print(json.dumps(anonymized_profile, indent=2))
    
    # Verify anonymization
    print("\n=== VERIFICATION ===")
    post_analysis = anonymizer.analyze(anonymized_profile)
    print(f"Entities remaining after anonymization: {post_analysis['total_entities']}")
    print(f"Bias categories remaining: {post_analysis['bias_categories'] or 'None'}")
    print(f"PII types remaining: {post_analysis['pii_types'] or 'None'}")
    
    return anonymized_profile


def batch_anonymize_profiles():
    """Batch process multiple employee profiles."""
    
    profiles = [
        {
            "id": "EMP001",
            "name": "Alice Johnson",
            "description": "Young female developer, recently graduated, Hispanic background"
        },
        {
            "id": "EMP002",
            "name": "Robert Smith",
            "description": "Senior white male executive, Republican, wealthy background"
        },
        {
            "id": "EMP003",
            "name": "Priya Patel",
            "description": "Indian woman, Hindu, experienced engineer, mother of two"
        }
    ]
    
    print("\n=== BATCH PROCESSING ===\n")
    
    anonymizer = JSONAnonymizer()
    
    anonymized_profiles = []
    for profile in profiles:
        print(f"Processing {profile['id']}...")
        anonymized = anonymizer.anonymize(profile, keys_to_anonymize=["name", "description"])
        anonymized_profiles.append(anonymized)
    
    print("\nAnonymized profiles:")
    for profile in anonymized_profiles:
        print(json.dumps(profile, indent=2))


if __name__ == "__main__":
    # Run employee profile anonymization
    anonymized = anonymize_employee_profile()
    
    # Run batch processing
    batch_anonymize_profiles()
