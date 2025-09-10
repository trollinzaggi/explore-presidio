"""
Talent Profile Anonymizer - Specialized for Enterprise Talent Management System
"""

import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

from bias_anonymizer import JSONAnonymizer, AnonymizerConfig
from bias_anonymizer.bias_words import BiasWords


@dataclass
class TalentProfileConfig:
    """Configuration specific to Talent Profile anonymization."""
    
    # Fields that should NEVER be anonymized (preserve for matching)
    preserve_fields: Set[str] = None
    
    # Fields that should ALWAYS be anonymized (contain PII/bias)
    always_anonymize_fields: Set[str] = None
    
    # Fields that need special handling
    special_handling_fields: Dict[str, str] = None
    
    def __post_init__(self):
        if self.preserve_fields is None:
            self.preserve_fields = {
                # Core business fields - needed for matching
                "core.rank.code",
                "core.rank.id",
                "core.employeeType.code",
                "core.jobCode",
                "core.gcrs.businessDivisionCode",
                "core.gcrs.businessUnitCode",
                "core.gcrs.businessAreaCode",
                "core.gcrs.businessSectorCode",
                "core.gcrs.businessSegmentCode",
                "core.gcrs.businessFunctionCode",
                
                # Work location codes (not descriptions)
                "core.workLocation.code",
                "core.workLocation.buildingCode",
                "core.workLocation.postalCode",
                "core.workLocation.stateCode",
                "core.workLocation.countryCode",
                
                # Experience metadata
                "experience.crossDivisionalExperience",
                "experience.internationalExperience",
                "experience.timeInCurrentRoleInDays",
                
                # Education and certifications (skills-based)
                "qualification.educations[*].degree",
                "qualification.educations[*].areaOfStudy",
                "qualification.educations[*].completionYear",
                "qualification.certifications",
                
                # System fields
                "version",
                "completionScore",
                "userId",  # May need to hash instead of preserve
                "externalSourceType"
            }
        
        if self.always_anonymize_fields is None:
            self.always_anonymize_fields = {
                # Descriptions that might contain bias
                "core.rank.description",
                "core.employeeType.description",
                "core.businessTitle",
                "core.gcrs.businessDivisionDescription",
                "core.gcrs.businessUnitDescription",
                "core.gcrs.businessAreaDescription",
                "core.gcrs.businessSectorDescription",
                "core.gcrs.businessSegmentDescription",
                "core.gcrs.businessFunctionDescription",
                
                # Location descriptions (might reveal demographic info)
                "core.workLocation.description",
                "core.workLocation.city",
                "core.workLocation.state",
                "core.workLocation.county",
                "core.workLocation.country",
                "core.workLocation.region",
                
                # Dates that could reveal age
                "core.enterpriseSeniorityDate",
                
                # Work eligibility (nationality/immigration status)
                "workEligibility",
                
                # Language proficiency (potential bias)
                "language.languages",
                
                # Affiliations (could reveal personal info)
                "affiliation.awards",
                "affiliation.boards",
                "affiliation.mandates",
                "affiliation.memberships",
                
                # Experience descriptions
                "experience.experiences[*].company",
                "experience.experiences[*].description",
                "experience.experiences[*].jobTitle",
                "experience.experiences[*].country.description",
                
                # Education institution names (could reveal background)
                "qualification.educations[*].institutionName",
                "qualification.educations[*].achievements",
                
                # Career preferences (might contain bias)
                "careerAspirationPreference",
                "careerLocationPreference",
                "careerRolePreference",
                
                # Audit fields (might contain names)
                "language.createdBy",
                "language.lastModifiedBy",
                "affiliation.createdBy",
                "affiliation.lastModifiedBy",
                "experience.createdBy",
                "experience.lastModifiedBy",
                "qualification.createdBy",
                "qualification.lastModifiedBy"
            }
        
        if self.special_handling_fields is None:
            self.special_handling_fields = {
                # Hash user ID instead of removing
                "userId": "hash",
                
                # Generalize dates to year only
                "experience.experiences[*].startDate": "year_only",
                "experience.experiences[*].endDate": "year_only",
                "createdDateTime": "remove",
                "lastModifiedDateTime": "remove",
                
                # Categorize reporting distance
                "core.reportingDistance.geb": "categorize",
                "core.reportingDistance.ceo": "categorize",
                "core.reportingDistance.chairman": "categorize"
            }


class TalentProfileAnonymizer:
    """
    Specialized anonymizer for Talent Profile data structure.
    Handles the specific nested structure and business rules.
    """
    
    def __init__(self, config: Optional[TalentProfileConfig] = None):
        """
        Initialize the Talent Profile Anonymizer.
        
        Args:
            config: Optional custom configuration
        """
        self.profile_config = config or TalentProfileConfig()
        
        # Initialize base anonymizer with bias detection
        self.base_config = AnonymizerConfig(
            detect_bias=True,
            detect_pii=True,
            confidence_threshold=0.7,
            operators={
                "PERSON": "replace",
                "EMAIL_ADDRESS": "mask",
                "PHONE_NUMBER": "hash",
                "DATE_TIME": "replace",
                "LOCATION": "replace",
                "BIAS_INDICATOR": "remove",
                "DEFAULT": "replace"
            },
            replacements={
                "PERSON": "[REDACTED]",
                "EMAIL_ADDRESS": "[EMAIL]",
                "PHONE_NUMBER": "[PHONE]",
                "LOCATION": "[LOCATION]",
                "DATE_TIME": "[DATE]",
                "DEFAULT": ""
            }
        )
        
        self.anonymizer = JSONAnonymizer(config=self.base_config)
    
    def anonymize_talent_profile(self, 
                                 profile: Dict[str, Any],
                                 custom_fields_to_anonymize: Optional[List[str]] = None,
                                 custom_fields_to_preserve: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Anonymize a talent profile with business logic awareness.
        
        Args:
            profile: The talent profile JSON
            custom_fields_to_anonymize: Additional fields to anonymize
            custom_fields_to_preserve: Additional fields to preserve
            
        Returns:
            Anonymized talent profile
        """
        import copy
        anonymized = copy.deepcopy(profile)
        
        # Build the list of fields to process
        fields_to_anonymize = self._get_fields_to_anonymize(
            anonymized,
            custom_fields_to_anonymize,
            custom_fields_to_preserve
        )
        
        # Process each field
        for field_path in fields_to_anonymize:
            self._anonymize_field(anonymized, field_path)
        
        # Apply special handling
        self._apply_special_handling(anonymized)
        
        # Clean empty structures
        self._clean_empty_structures(anonymized)
        
        return anonymized
    
    def _get_fields_to_anonymize(self,
                                 profile: Dict,
                                 custom_anonymize: Optional[List[str]],
                                 custom_preserve: Optional[List[str]]) -> Set[str]:
        """
        Determine which fields should be anonymized.
        
        Returns:
            Set of field paths to anonymize
        """
        # Start with always anonymize fields
        fields = set(self.profile_config.always_anonymize_fields)
        
        # Add custom fields to anonymize
        if custom_anonymize:
            fields.update(custom_anonymize)
        
        # Remove fields that should be preserved
        preserve = set(self.profile_config.preserve_fields)
        if custom_preserve:
            preserve.update(custom_preserve)
        
        # Remove preserved fields from anonymization list
        fields = fields - preserve
        
        # Expand wildcard patterns
        expanded_fields = set()
        for field in fields:
            if "[*]" in field:
                # Handle array wildcards
                expanded_fields.update(self._expand_array_paths(profile, field))
            else:
                expanded_fields.add(field)
        
        return expanded_fields
    
    def _expand_array_paths(self, data: Dict, pattern: str) -> List[str]:
        """
        Expand array wildcard patterns to actual paths.
        
        Args:
            data: The data structure
            pattern: Pattern with [*] wildcards
            
        Returns:
            List of expanded paths
        """
        paths = []
        parts = pattern.split("[*]")
        
        if len(parts) == 2:
            base_path = parts[0]
            suffix = parts[1].lstrip(".")
            
            # Navigate to the array
            current = data
            for part in base_path.split("."):
                if part and isinstance(current, dict):
                    current = current.get(part, {})
            
            # Expand for each array item
            if isinstance(current, list):
                for i in range(len(current)):
                    if suffix:
                        paths.append(f"{base_path}[{i}].{suffix}")
                    else:
                        paths.append(f"{base_path}[{i}]")
        
        return paths
    
    def _anonymize_field(self, data: Dict, field_path: str):
        """
        Anonymize a specific field in the data structure.
        
        Args:
            data: The data structure (modified in place)
            field_path: Dot-notation path to the field
        """
        # Parse the path
        parts = []
        current_part = ""
        in_bracket = False
        
        for char in field_path:
            if char == "[":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                in_bracket = True
            elif char == "]":
                if current_part:
                    parts.append(int(current_part))
                    current_part = ""
                in_bracket = False
            elif char == "." and not in_bracket:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char
        
        if current_part:
            parts.append(current_part)
        
        # Navigate to the field
        current = data
        for i, part in enumerate(parts[:-1]):
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list) and isinstance(part, int) and part < len(current):
                current = current[part]
            else:
                return  # Path doesn't exist
        
        # Anonymize the final field
        last_part = parts[-1]
        if isinstance(current, dict) and last_part in current:
            value = current[last_part]
            if isinstance(value, str):
                # Use the base anonymizer for string values
                current[last_part] = self.anonymizer.anonymize_text(value)
            elif isinstance(value, list):
                # Anonymize each item in the list
                for i, item in enumerate(value):
                    if isinstance(item, str):
                        value[i] = self.anonymizer.anonymize_text(item)
                    elif isinstance(item, dict):
                        # Recursively anonymize dict items
                        self._anonymize_dict_values(item)
    
    def _anonymize_dict_values(self, data: Dict):
        """
        Recursively anonymize all string values in a dictionary.
        
        Args:
            data: Dictionary to anonymize (modified in place)
        """
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = self.anonymizer.anonymize_text(value)
            elif isinstance(value, dict):
                self._anonymize_dict_values(value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, str):
                        value[i] = self.anonymizer.anonymize_text(item)
                    elif isinstance(item, dict):
                        self._anonymize_dict_values(item)
    
    def _apply_special_handling(self, data: Dict):
        """
        Apply special handling rules to specific fields.
        
        Args:
            data: The data structure (modified in place)
        """
        for field_path, handling in self.profile_config.special_handling_fields.items():
            if handling == "hash":
                self._apply_hash(data, field_path)
            elif handling == "year_only":
                self._apply_year_only(data, field_path)
            elif handling == "categorize":
                self._apply_categorization(data, field_path)
            elif handling == "remove":
                self._apply_removal(data, field_path)
    
    def _apply_hash(self, data: Dict, field_path: str):
        """Apply hashing to a field."""
        import hashlib
        value = self._get_field_value(data, field_path)
        if value and isinstance(value, str):
            hashed = hashlib.sha256(value.encode()).hexdigest()[:16]
            self._set_field_value(data, field_path, f"HASH_{hashed}")
    
    def _apply_year_only(self, data: Dict, field_path: str):
        """Extract only year from date fields."""
        if "[*]" in field_path:
            # Handle array patterns
            paths = self._expand_array_paths(data, field_path)
            for path in paths:
                self._apply_year_only(data, path)
        else:
            value = self._get_field_value(data, field_path)
            if value and isinstance(value, str):
                # Extract year from various date formats
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', value)
                if year_match:
                    self._set_field_value(data, field_path, year_match.group())
                else:
                    self._set_field_value(data, field_path, "[YEAR]")
    
    def _apply_categorization(self, data: Dict, field_path: str):
        """Categorize numeric values into ranges."""
        value = self._get_field_value(data, field_path)
        if value:
            try:
                num_value = int(value) if isinstance(value, str) else value
                if num_value <= 2:
                    category = "Direct"
                elif num_value <= 4:
                    category = "Close"
                elif num_value <= 6:
                    category = "Mid-level"
                else:
                    category = "Distant"
                self._set_field_value(data, field_path, category)
            except (ValueError, TypeError):
                self._set_field_value(data, field_path, "[LEVEL]")
    
    def _apply_removal(self, data: Dict, field_path: str):
        """Remove a field entirely."""
        parts = field_path.split(".")
        current = data
        
        for part in parts[:-1]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return
        
        if isinstance(current, dict) and parts[-1] in current:
            del current[parts[-1]]
    
    def _get_field_value(self, data: Dict, field_path: str) -> Any:
        """Get value at a field path."""
        parts = field_path.split(".")
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def _set_field_value(self, data: Dict, field_path: str, value: Any):
        """Set value at a field path."""
        parts = field_path.split(".")
        current = data
        
        for part in parts[:-1]:
            if isinstance(current, dict):
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        if isinstance(current, dict):
            current[parts[-1]] = value
    
    def _clean_empty_structures(self, data: Dict):
        """
        Remove empty strings, lists, and nested structures.
        
        Args:
            data: The data structure (modified in place)
        """
        keys_to_remove = []
        
        for key, value in data.items():
            if value == "" or value == [] or value == {} or value is None:
                keys_to_remove.append(key)
            elif isinstance(value, dict):
                self._clean_empty_structures(value)
                if not value:  # Dictionary became empty after cleaning
                    keys_to_remove.append(key)
            elif isinstance(value, list):
                # Clean list items
                cleaned_list = []
                for item in value:
                    if isinstance(item, dict):
                        self._clean_empty_structures(item)
                        if item:  # Only keep non-empty dicts
                            cleaned_list.append(item)
                    elif item not in ["", None]:
                        cleaned_list.append(item)
                
                if cleaned_list:
                    data[key] = cleaned_list
                else:
                    keys_to_remove.append(key)
        
        # Remove empty keys
        for key in keys_to_remove:
            del data[key]
    
    def analyze_profile(self, profile: Dict) -> Dict[str, Any]:
        """
        Analyze a talent profile for bias and PII without anonymizing.
        
        Args:
            profile: The talent profile to analyze
            
        Returns:
            Analysis report
        """
        fields_to_check = self.profile_config.always_anonymize_fields
        
        report = {
            "total_fields_checked": len(fields_to_check),
            "fields_with_bias": [],
            "fields_with_pii": [],
            "bias_categories_found": set(),
            "pii_types_found": set(),
            "risk_score": 0,
            "details": []
        }
        
        for field_path in fields_to_check:
            value = self._get_field_value(profile, field_path)
            if value and isinstance(value, str):
                analysis = self.anonymizer.analyze({"text": value})
                
                if analysis["total_entities"] > 0:
                    field_report = {
                        "field": field_path,
                        "entities_found": analysis["total_entities"],
                        "bias_categories": analysis["bias_categories"],
                        "pii_types": analysis["pii_types"]
                    }
                    
                    report["details"].append(field_report)
                    
                    if analysis["bias_categories"]:
                        report["fields_with_bias"].append(field_path)
                        report["bias_categories_found"].update(analysis["bias_categories"])
                    
                    if analysis["pii_types"]:
                        report["fields_with_pii"].append(field_path)
                        report["pii_types_found"].update(analysis["pii_types"])
        
        # Convert sets to lists for JSON serialization
        report["bias_categories_found"] = list(report["bias_categories_found"])
        report["pii_types_found"] = list(report["pii_types_found"])
        
        # Calculate risk score (0-100)
        bias_risk = len(report["fields_with_bias"]) * 3
        pii_risk = len(report["fields_with_pii"]) * 5
        report["risk_score"] = min(100, bias_risk + pii_risk)
        
        return report


# Example usage function
def example_usage():
    """Demonstrate usage with a sample talent profile."""
    
    sample_profile = {
        "externalSourceType": "LinkedIn",
        "core": {
            "rank": {
                "code": "L7",
                "description": "Senior Principal Engineer",
                "id": "RANK_007"
            },
            "employeeType": {
                "code": "FTE",
                "description": "Full Time Employee - Male, 45 years old"
            },
            "businessTitle": "Senior Asian Male Engineer from wealthy background",
            "jobCode": "ENG_SR_001",
            "enterpriseSeniorityDate": "1995-06-15",
            "gcrs": {
                "businessDivisionCode": "TECH",
                "businessDivisionDescription": "Technology Division - Predominantly white males",
                "businessUnitCode": "CLOUD",
                "businessUnitDescription": "Cloud Computing Unit"
            },
            "workLocation": {
                "code": "SF_HQ_01",
                "description": "San Francisco Headquarters - Liberal area",
                "city": "San Francisco",
                "stateCode": "CA",
                "state": "California",
                "country": "United States"
            },
            "reportingDistance": {
                "geb": "3",
                "ceo": "4",
                "chairman": "5"
            }
        },
        "workEligibility": "US Citizen, no visa required",
        "language": {
            "languages": ["English - Native", "Mandarin - Mother tongue"],
            "createdBy": "John Smith",
            "lastModifiedBy": "Jane Doe"
        },
        "experience": {
            "experiences": [
                {
                    "company": "Google - Known for young workforce",
                    "description": "Led team of mostly Indian engineers",
                    "jobTitle": "Senior Engineering Manager",
                    "startDate": "2015-03-01",
                    "endDate": "2020-12-31"
                }
            ],
            "crossDivisionalExperience": "Yes",
            "internationalExperience": "Yes",
            "timeInCurrentRoleInDays": "1095"
        },
        "qualification": {
            "educations": [
                {
                    "institutionName": "Stanford University - Elite private school",
                    "degree": "MS Computer Science",
                    "areaOfStudy": "Machine Learning",
                    "completionYear": 2000,
                    "achievements": "Summa Cum Laude, wealthy donor family"
                }
            ],
            "certifications": ["AWS Solutions Architect", "Google Cloud Professional"]
        },
        "careerAspirationPreference": "Looking to lead young, energetic team",
        "careerLocationPreference": "Prefer working with other Christians",
        "careerRolePreference": "No women or minorities in reporting structure",
        "userId": "user_12345",
        "completionScore": "95"
    }
    
    # Initialize anonymizer
    anonymizer = TalentProfileAnonymizer()
    
    # Analyze first
    print("ANALYSIS REPORT")
    print("=" * 50)
    analysis = anonymizer.analyze_profile(sample_profile)
    print(f"Risk Score: {analysis['risk_score']}/100")
    print(f"Fields with bias: {len(analysis['fields_with_bias'])}")
    print(f"Fields with PII: {len(analysis['fields_with_pii'])}")
    print(f"Bias categories found: {', '.join(analysis['bias_categories_found'])}")
    print(f"PII types found: {', '.join(analysis['pii_types_found'])}")
    
    # Anonymize
    print("\n\nANONYMIZED PROFILE")
    print("=" * 50)
    anonymized = anonymizer.anonymize_talent_profile(sample_profile)
    print(json.dumps(anonymized, indent=2))
    
    # Verify critical fields are preserved
    print("\n\nVERIFICATION")
    print("=" * 50)
    print(f"Job code preserved: {anonymized['core']['jobCode'] == sample_profile['core']['jobCode']}")
    print(f"Rank code preserved: {anonymized['core']['rank']['code'] == sample_profile['core']['rank']['code']}")
    print(f"Certifications preserved: {anonymized['qualification']['certifications'] == sample_profile['qualification']['certifications']}")
    print(f"Bias removed from title: {'Male' not in anonymized['core'].get('businessTitle', '')}")
    print(f"Bias removed from preferences: {'Christian' not in anonymized.get('careerLocationPreference', '')}")


if __name__ == "__main__":
    example_usage()
