"""
Enhanced Talent Profile Anonymizer with automatic nested structure handling
"""

import json
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum

from bias_anonymizer import JSONAnonymizer, AnonymizerConfig
from bias_anonymizer.bias_words import BiasWords


@dataclass
class FieldRule:
    """Rules for handling specific field types."""
    action: str  # "preserve", "anonymize", "hash", "remove", "year_only", "categorize"
    apply_to_nested: bool = True  # Apply rule to nested structures
    nested_fields: Dict[str, str] = field(default_factory=dict)  # Specific rules for nested fields


@dataclass
class TalentProfileConfig:
    """Enhanced configuration for Talent Profile anonymization."""
    
    # Field patterns that should be preserved across all nested structures
    preserve_patterns: Set[str] = None
    
    # Field patterns that should always be anonymized
    anonymize_patterns: Set[str] = None
    
    # Rules for specific structures
    structure_rules: Dict[str, FieldRule] = None
    
    # Auto-detect and process nested structures
    auto_process_nested: bool = True
    
    # Fields that commonly contain PII/bias in nested structures
    common_pii_fields: Set[str] = None
    
    # Fields that are typically safe in nested structures
    common_safe_fields: Set[str] = None
    
    def __post_init__(self):
        if self.preserve_patterns is None:
            self.preserve_patterns = {
                # Patterns to preserve anywhere they appear
                "*code",  # Any field ending with 'code'
                "*Code",
                "*id",    # Any field ending with 'id'
                "*Id",
                "*ID",
                "degree",
                "areaOfStudy",
                "certifications",
                "completionYear",
                "year",
                "score",
                "level",
                "type",
                "category",
                "status"
            }
        
        if self.anonymize_patterns is None:
            self.anonymize_patterns = {
                # Patterns to anonymize anywhere they appear
                "*description",
                "*Description",
                "*name",
                "*Name",
                "title",
                "*Title",
                "company",
                "organization",
                "institution*",
                "*By",  # createdBy, modifiedBy, etc.
                "achievements",
                "comments",
                "notes",
                "summary",
                "bio",
                "*Location",
                "address",
                "city",
                "state",
                "country",
                "email",
                "phone",
                "*Date",
                "*Time"
            }
        
        if self.common_pii_fields is None:
            self.common_pii_fields = {
                "name", "firstName", "lastName", "fullName",
                "email", "emailAddress", "phone", "phoneNumber",
                "address", "street", "city", "state", "country",
                "description", "bio", "summary", "about",
                "title", "position", "role",
                "company", "organization", "employer",
                "institution", "school", "university",
                "date", "startDate", "endDate", "birthDate",
                "age", "gender", "race", "ethnicity",
                "nationality", "citizenship",
                "achievements", "accomplishments",
                "notes", "comments", "remarks"
            }
        
        if self.common_safe_fields is None:
            self.common_safe_fields = {
                "id", "code", "type", "category", "status",
                "level", "score", "rank", "priority",
                "year", "month", "duration", "count",
                "percentage", "rate", "ratio",
                "isActive", "isEnabled", "isRequired",
                "version", "revision"
            }
        
        if self.structure_rules is None:
            self.structure_rules = {
                # Affiliation structures
                "affiliation.awards": FieldRule(
                    action="anonymize",
                    apply_to_nested=True,
                    nested_fields={
                        "name": "anonymize",
                        "organization": "anonymize", 
                        "description": "anonymize",
                        "date": "year_only",
                        "id": "preserve",
                        "type": "preserve",
                        "category": "preserve"
                    }
                ),
                "affiliation.boards": FieldRule(
                    action="anonymize",
                    apply_to_nested=True,
                    nested_fields={
                        "organizationName": "anonymize",
                        "position": "anonymize",
                        "description": "anonymize",
                        "startDate": "year_only",
                        "endDate": "year_only",
                        "boardType": "preserve",
                        "id": "preserve"
                    }
                ),
                "affiliation.mandates": FieldRule(
                    action="anonymize",
                    apply_to_nested=True,
                    nested_fields={
                        "title": "anonymize",
                        "organization": "anonymize",
                        "description": "anonymize",
                        "scope": "anonymize",
                        "mandateId": "preserve",
                        "type": "preserve",
                        "status": "preserve"
                    }
                ),
                "affiliation.memberships": FieldRule(
                    action="anonymize",
                    apply_to_nested=True,
                    nested_fields={
                        "organizationName": "anonymize",
                        "membershipType": "preserve",
                        "role": "anonymize",
                        "description": "anonymize",
                        "since": "year_only",
                        "membershipId": "preserve",
                        "status": "preserve"
                    }
                ),
                # Experience structures
                "experience.experiences": FieldRule(
                    action="partial",
                    apply_to_nested=True,
                    nested_fields={
                        "company": "anonymize",
                        "jobTitle": "anonymize",
                        "description": "anonymize",
                        "startDate": "year_only",
                        "endDate": "year_only",
                        "id": "preserve",
                        "country.code": "preserve",
                        "country.description": "anonymize"
                    }
                ),
                # Education structures
                "qualification.educations": FieldRule(
                    action="partial",
                    apply_to_nested=True,
                    nested_fields={
                        "institutionName": "anonymize",
                        "achievements": "anonymize",
                        "degree": "preserve",
                        "areaOfStudy": "preserve",
                        "completionYear": "preserve",
                        "id": "preserve"
                    }
                ),
                # Language structures
                "language.languages": FieldRule(
                    action="partial",
                    apply_to_nested=True,
                    nested_fields={
                        "language": "preserve",
                        "proficiency": "preserve",
                        "notes": "anonymize"
                    }
                )
            }


class EnhancedTalentProfileAnonymizer:
    """
    Enhanced anonymizer that automatically handles nested structures.
    """
    
    def __init__(self, config: Optional[TalentProfileConfig] = None):
        """Initialize the enhanced anonymizer."""
        self.config = config or TalentProfileConfig()
        
        # Initialize base anonymizer
        base_config = AnonymizerConfig(
            detect_bias=True,
            detect_pii=True,
            confidence_threshold=0.7
        )
        self.anonymizer = JSONAnonymizer(config=base_config)
        
        # Cache for processed paths
        self._processed_paths = set()
    
    def anonymize_talent_profile(self, 
                                 profile: Dict[str, Any],
                                 custom_rules: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Anonymize a talent profile with automatic nested structure handling.
        
        Args:
            profile: The talent profile JSON
            custom_rules: Optional custom rules for specific fields
            
        Returns:
            Anonymized talent profile
        """
        import copy
        anonymized = copy.deepcopy(profile)
        
        # Reset processed paths cache
        self._processed_paths = set()
        
        # Process the entire structure
        self._process_structure(anonymized, "", custom_rules or {})
        
        # Clean empty structures
        self._clean_empty_structures(anonymized)
        
        return anonymized
    
    def _process_structure(self, 
                          data: Any, 
                          path: str,
                          custom_rules: Dict[str, str],
                          parent_rule: Optional[FieldRule] = None):
        """
        Recursively process any structure, automatically detecting nested objects and arrays.
        
        Args:
            data: Current data node
            path: Current path in dot notation
            custom_rules: Custom rules for specific fields
            parent_rule: Rule inherited from parent structure
        """
        if isinstance(data, dict):
            self._process_dict(data, path, custom_rules, parent_rule)
        elif isinstance(data, list):
            self._process_list(data, path, custom_rules, parent_rule)
    
    def _process_dict(self, 
                     data: Dict, 
                     path: str,
                     custom_rules: Dict[str, str],
                     parent_rule: Optional[FieldRule]):
        """Process a dictionary structure."""
        keys_to_remove = []
        
        for key, value in list(data.items()):
            current_path = f"{path}.{key}" if path else key
            
            # Skip if already processed
            if current_path in self._processed_paths:
                continue
            self._processed_paths.add(current_path)
            
            # Determine action for this field
            action = self._determine_action(key, current_path, value, custom_rules, parent_rule)
            
            if action == "remove":
                keys_to_remove.append(key)
            elif action == "preserve":
                # Keep as is, but still process nested structures
                if isinstance(value, (dict, list)):
                    self._process_structure(value, current_path, custom_rules, parent_rule)
            elif action == "anonymize":
                if isinstance(value, str):
                    data[key] = self._anonymize_value(value, current_path)
                elif isinstance(value, (dict, list)):
                    # Anonymize nested structure
                    self._process_structure(value, current_path, custom_rules, parent_rule)
            elif action == "hash":
                if isinstance(value, str):
                    data[key] = self._hash_value(value)
            elif action == "year_only":
                if isinstance(value, str):
                    data[key] = self._extract_year(value)
            elif action == "categorize":
                data[key] = self._categorize_value(value)
            elif action == "auto":
                # Auto-detect based on content
                if isinstance(value, str):
                    if self._should_anonymize_string(key, value):
                        data[key] = self._anonymize_value(value, current_path)
                elif isinstance(value, (dict, list)):
                    # Check if this is a known structure
                    structure_rule = self.config.structure_rules.get(current_path)
                    self._process_structure(value, current_path, custom_rules, structure_rule)
        
        # Remove marked keys
        for key in keys_to_remove:
            del data[key]
    
    def _process_list(self, 
                     data: List, 
                     path: str,
                     custom_rules: Dict[str, str],
                     parent_rule: Optional[FieldRule]):
        """Process a list structure."""
        for i, item in enumerate(data):
            item_path = f"{path}[{i}]"
            
            if isinstance(item, dict):
                # Process each dictionary in the list
                self._process_dict_in_list(item, path, i, custom_rules, parent_rule)
            elif isinstance(item, list):
                # Nested list
                self._process_list(item, item_path, custom_rules, parent_rule)
            elif isinstance(item, str):
                # String in list - check if it should be anonymized
                if self._should_anonymize_string(path, item):
                    data[i] = self._anonymize_value(item, item_path)
    
    def _process_dict_in_list(self,
                             item: Dict,
                             list_path: str,
                             index: int,
                             custom_rules: Dict[str, str],
                             parent_rule: Optional[FieldRule]):
        """Process a dictionary that's an item in a list."""
        # Check if there's a specific rule for this list structure
        structure_rule = self.config.structure_rules.get(list_path)
        
        if structure_rule and structure_rule.nested_fields:
            # Apply specific field rules
            for field_name, field_action in structure_rule.nested_fields.items():
                if "." in field_name:
                    # Nested field (e.g., "country.description")
                    self._apply_nested_field_rule(item, field_name, field_action)
                elif field_name in item:
                    # Direct field
                    self._apply_field_action(item, field_name, field_action)
            
            # Process remaining fields not in rules
            for key, value in item.items():
                if key not in structure_rule.nested_fields:
                    if isinstance(value, (dict, list)):
                        self._process_structure(value, f"{list_path}[{index}].{key}", 
                                              custom_rules, structure_rule)
                    elif isinstance(value, str) and self._should_anonymize_string(key, value):
                        item[key] = self._anonymize_value(value, f"{list_path}[{index}].{key}")
        else:
            # No specific rules, use automatic detection
            self._process_dict(item, f"{list_path}[{index}]", custom_rules, parent_rule)
    
    def _determine_action(self, 
                         field_name: str, 
                         field_path: str,
                         value: Any,
                         custom_rules: Dict[str, str],
                         parent_rule: Optional[FieldRule]) -> str:
        """
        Determine what action to take for a field.
        
        Returns:
            Action string: "preserve", "anonymize", "remove", "hash", "year_only", "categorize", "auto"
        """
        # Check custom rules first
        if field_path in custom_rules:
            return custom_rules[field_path]
        
        # Check structure-specific rules
        if field_path in self.config.structure_rules:
            return self.config.structure_rules[field_path].action
        
        # Check parent rule
        if parent_rule and parent_rule.nested_fields.get(field_name):
            return parent_rule.nested_fields[field_name]
        
        # Check patterns
        if self._matches_pattern(field_name, self.config.preserve_patterns):
            return "preserve"
        
        if self._matches_pattern(field_name, self.config.anonymize_patterns):
            return "anonymize"
        
        # Check common field names
        if field_name.lower() in {f.lower() for f in self.config.common_safe_fields}:
            return "preserve"
        
        if field_name.lower() in {f.lower() for f in self.config.common_pii_fields}:
            return "anonymize"
        
        # Special handling for certain field types
        if "date" in field_name.lower() or "time" in field_name.lower():
            return "year_only"
        
        if field_name.lower().endswith("by"):  # createdBy, modifiedBy, etc.
            return "anonymize"
        
        if field_name.lower() in ["userid", "user_id", "employeeid", "employee_id"]:
            return "hash"
        
        # Default to auto-detection
        return "auto"
    
    def _matches_pattern(self, field_name: str, patterns: Set[str]) -> bool:
        """Check if a field name matches any pattern."""
        field_lower = field_name.lower()
        
        for pattern in patterns:
            pattern_lower = pattern.lower()
            
            if pattern_lower.startswith("*") and pattern_lower.endswith("*"):
                # Contains pattern
                if pattern_lower[1:-1] in field_lower:
                    return True
            elif pattern_lower.startswith("*"):
                # Ends with pattern
                if field_lower.endswith(pattern_lower[1:]):
                    return True
            elif pattern_lower.endswith("*"):
                # Starts with pattern
                if field_lower.startswith(pattern_lower[:-1]):
                    return True
            else:
                # Exact match
                if field_lower == pattern_lower:
                    return True
        
        return False
    
    def _should_anonymize_string(self, field_name: str, value: str) -> bool:
        """
        Determine if a string value should be anonymized based on content analysis.
        """
        # Don't anonymize empty or very short strings
        if not value or len(value.strip()) < 3:
            return False
        
        # Don't anonymize if it looks like a code or ID (all uppercase, alphanumeric)
        if value.isupper() and (value.replace("_", "").replace("-", "").isalnum()):
            return False
        
        # Don't anonymize pure numbers
        if value.replace(".", "").replace("-", "").isdigit():
            return False
        
        # Don't anonymize boolean-like values
        if value.lower() in ["true", "false", "yes", "no", "y", "n", "active", "inactive"]:
            return False
        
        # Check if the value contains bias or PII
        analysis = self.anonymizer.analyze({"text": value})
        if analysis["total_entities"] > 0:
            return True
        
        # Check field name hints
        field_lower = field_name.lower()
        if any(term in field_lower for term in ["description", "title", "name", "summary", "bio"]):
            return True
        
        return False
    
    def _anonymize_value(self, value: str, context: str) -> str:
        """Anonymize a string value."""
        return self.anonymizer.anonymize_text(value)
    
    def _hash_value(self, value: str) -> str:
        """Hash a value."""
        import hashlib
        hashed = hashlib.sha256(value.encode()).hexdigest()[:16]
        return f"HASH_{hashed}"
    
    def _extract_year(self, value: str) -> str:
        """Extract year from a date string."""
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', value)
        if year_match:
            return year_match.group()
        return "[YEAR]"
    
    def _categorize_value(self, value: Any) -> str:
        """Categorize a numeric value."""
        try:
            num_value = int(value) if isinstance(value, str) else value
            if num_value <= 2:
                return "Direct"
            elif num_value <= 4:
                return "Close"
            elif num_value <= 6:
                return "Mid-level"
            else:
                return "Distant"
        except (ValueError, TypeError):
            return "[LEVEL]"
    
    def _apply_nested_field_rule(self, data: Dict, field_path: str, action: str):
        """Apply a rule to a nested field within a structure."""
        parts = field_path.split(".")
        current = data
        
        for part in parts[:-1]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return  # Path doesn't exist
        
        last_part = parts[-1]
        if isinstance(current, dict) and last_part in current:
            self._apply_field_action(current, last_part, action)
    
    def _apply_field_action(self, data: Dict, field: str, action: str):
        """Apply an action to a specific field."""
        if field not in data:
            return
            
        value = data[field]
        
        if action == "anonymize" and isinstance(value, str):
            data[field] = self._anonymize_value(value, field)
        elif action == "remove":
            del data[field]
        elif action == "hash" and isinstance(value, str):
            data[field] = self._hash_value(value)
        elif action == "year_only" and isinstance(value, str):
            data[field] = self._extract_year(value)
        elif action == "categorize":
            data[field] = self._categorize_value(value)
        # "preserve" means do nothing
    
    def _clean_empty_structures(self, data: Any):
        """Remove empty structures recursively."""
        if isinstance(data, dict):
            keys_to_remove = []
            for key, value in data.items():
                if value in ["", [], {}, None]:
                    keys_to_remove.append(key)
                elif isinstance(value, (dict, list)):
                    self._clean_empty_structures(value)
                    if not value:  # Became empty after cleaning
                        keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del data[key]
                
        elif isinstance(data, list):
            items_to_remove = []
            for i, item in enumerate(data):
                if item in ["", {}, [], None]:
                    items_to_remove.append(i)
                elif isinstance(item, (dict, list)):
                    self._clean_empty_structures(item)
                    if not item:
                        items_to_remove.append(i)
            
            for i in reversed(items_to_remove):
                data.pop(i)


# Example usage showing automatic handling
def demonstrate_auto_handling():
    """Demonstrate automatic handling of unknown nested structures."""
    
    profile_with_complex_nesting = {
        "affiliation": {
            "awards": [
                {
                    "id": "AWD001",
                    "name": "Best Employee Award from white male CEO",
                    "organization": "TechCorp known for discrimination",
                    "description": "Given to senior males only",
                    "date": "2023-05-15",
                    "type": "performance",
                    "customField1": "Some value that might have bias",
                    "nestedStructure": {
                        "detail": "Awarded by Christian leadership team",
                        "score": 95,
                        "code": "PERF_2023"
                    }
                }
            ],
            "boards": [
                {
                    "organizationName": "Elite Country Club - whites only",
                    "position": "Board Member - must be wealthy",
                    "boardType": "advisory",
                    "startDate": "2020-01-01",
                    "customData": {
                        "notes": "Requires Republican affiliation",
                        "memberCode": "BD_123",
                        "subCommittees": [
                            {
                                "name": "Finance Committee for wealthy members",
                                "role": "Chair",
                                "id": "SC_001"
                            }
                        ]
                    }
                }
            ],
            "unknownStructure": {
                "field1": "This contains info about the person being male",
                "field2": "Age 45, white, from upper-class family",
                "nestedArray": [
                    {
                        "description": "Hispanic female colleague",
                        "code": "EMP_002",
                        "metadata": {
                            "notes": "Young millennial, unmarried",
                            "id": "META_123"
                        }
                    }
                ]
            }
        }
    }
    
    print("ORIGINAL PROFILE WITH COMPLEX NESTING:")
    print("=" * 60)
    print(json.dumps(profile_with_complex_nesting, indent=2))
    
    # Initialize enhanced anonymizer
    anonymizer = EnhancedTalentProfileAnonymizer()
    
    # Anonymize - will automatically handle all nested structures
    anonymized = anonymizer.anonymize_talent_profile(profile_with_complex_nesting)
    
    print("\n\nANONYMIZED PROFILE (AUTO-HANDLED):")
    print("=" * 60)
    print(json.dumps(anonymized, indent=2))
    
    print("\n\nKEY OBSERVATIONS:")
    print("=" * 60)
    print("✓ All nested structures were automatically discovered and processed")
    print("✓ IDs and codes were preserved throughout")
    print("✓ Descriptions and bias terms were removed at all levels")
    print("✓ Unknown structures were handled intelligently")
    print("✓ Empty structures were cleaned up")


if __name__ == "__main__":
    demonstrate_auto_handling()
