"""
Simple wrapper for Talent Profile Anonymizer
Provides an easy-to-use interface for anonymizing JSON profiles
"""

import json
from typing import Dict, List, Optional, Any, Union
from bias_anonymizer.talent_profile_anonymizer import TalentProfileAnonymizer, TalentProfileConfig
from bias_anonymizer.config_loader import create_anonymizer_from_config, load_config_from_yaml


class BiasAnonymizer:
    """
    Simple wrapper class for bias anonymization.
    
    Usage:
        # Using default strategy
        anonymizer = BiasAnonymizer()
        result = anonymizer.anonymize(profile_json)
        
        # Using YAML config
        anonymizer = BiasAnonymizer(config_path='config/custom.yaml')
        result = anonymizer.anonymize(profile_json)
        
        # Using strategy
        anonymizer = BiasAnonymizer(strategy='replace')
        result = anonymizer.anonymize(profile_json)
    """
    
    def __init__(self, strategy: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the anonymizer.
        
        Args:
            strategy: Anonymization strategy - "redact", "replace", or "custom"
                     If None and no config_path, uses default YAML config
            config_path: Path to YAML configuration file
                        If provided, overrides strategy parameter
        """
        if config_path:
            # Load from YAML configuration
            self.anonymizer = create_anonymizer_from_config(config_path)
            yaml_config = load_config_from_yaml(config_path)
            self.strategy = yaml_config.get('anonymization_strategy', 'redact')
        elif strategy:
            # Use programmatic strategy
            self.strategy = strategy
            self._init_anonymizer(strategy)
        else:
            # Use default YAML configuration
            self.anonymizer = create_anonymizer_from_config()
            yaml_config = load_config_from_yaml()
            self.strategy = yaml_config.get('anonymization_strategy', 'redact')
    
    def _init_anonymizer(self, strategy: str, custom_tokens: Optional[Dict[str, str]] = None):
        """Initialize the underlying anonymizer with the specified strategy."""
        config = TalentProfileConfig(
            anonymization_strategy=strategy,
            replacement_tokens=custom_tokens
        )
        self.anonymizer = TalentProfileAnonymizer(config)
    
    def anonymize(self,
                  profile: Union[Dict, str],
                  fields_to_anonymize: Optional[List[str]] = None,
                  fields_to_preserve: Optional[List[str]] = None,
                  strategy: Optional[str] = None) -> Dict[str, Any]:
        """
        Anonymize a profile JSON.
        
        Args:
            profile: Profile data as dict or JSON string
            fields_to_anonymize: Additional fields to anonymize (dot notation)
                                Example: ['custom.field1', 'experience.customField']
            fields_to_preserve: Additional fields to preserve (dot notation)
                               Example: ['core.customId', 'qualification.customScore']
            strategy: Override default strategy for this call
        
        Returns:
            Anonymized profile as dictionary
        
        Example:
            result = anonymizer.anonymize(
                profile,
                fields_to_anonymize=['core.customDescription'],
                fields_to_preserve=['core.customCode']
            )
        """
        # Handle JSON string input
        if isinstance(profile, str):
            profile = json.loads(profile)
        
        # Reinitialize if strategy changed
        if strategy and strategy != self.strategy:
            self._init_anonymizer(strategy)
            self.strategy = strategy
        
        # Perform anonymization
        return self.anonymizer.anonymize_talent_profile(
            profile,
            custom_fields_to_anonymize=fields_to_anonymize,
            custom_fields_to_preserve=fields_to_preserve
        )
    
    def anonymize_with_replace(self, profile: Union[Dict, str]) -> Dict[str, Any]:
        """Convenience method to anonymize with replace strategy."""
        return self.anonymize(profile, strategy="replace")
    
    def anonymize_with_redact(self, profile: Union[Dict, str]) -> Dict[str, Any]:
        """Convenience method to anonymize with redact strategy."""
        return self.anonymize(profile, strategy="redact")
    
    def anonymize_with_remove(self, profile: Union[Dict, str]) -> Dict[str, Any]:
        """Convenience method to anonymize with remove strategy (alias for redact)."""
        return self.anonymize(profile, strategy="redact")
    
    def anonymize_with_custom(self, 
                             profile: Union[Dict, str],
                             custom_tokens: Dict[str, str]) -> Dict[str, Any]:
        """
        Anonymize with custom replacement tokens.
        
        Args:
            profile: Profile to anonymize
            custom_tokens: Dictionary of entity types to replacement text
                          Example: {
                              "GENDER_BIAS": "person",
                              "RACE_BIAS": "individual"
                          }
        """
        self._init_anonymizer("custom", custom_tokens)
        return self.anonymize(profile, strategy="custom")
    
    def analyze(self, profile: Union[Dict, str]) -> Dict[str, Any]:
        """
        Analyze a profile for bias without anonymizing.
        
        Returns:
            Analysis report with risk score and detected bias categories
        """
        if isinstance(profile, str):
            profile = json.loads(profile)
        
        return self.anonymizer.analyze_profile(profile)


# Convenience functions for direct use
def anonymize_profile(profile: Union[Dict, str],
                     strategy: str = "redact",
                     fields_to_anonymize: Optional[List[str]] = None,
                     fields_to_preserve: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Quick function to anonymize a profile.
    
    Args:
        profile: Profile JSON (dict or string)
        strategy: "remove" (default), "replace", or "custom"
        fields_to_anonymize: Additional fields to anonymize
        fields_to_preserve: Additional fields to preserve
    
    Returns:
        Anonymized profile dictionary
    
    Example:
        result = anonymize_profile(profile_json)
        result = anonymize_profile(profile_json, strategy="replace")
        result = anonymize_profile(
            profile_json,
            fields_to_anonymize=['custom.notes'],
            fields_to_preserve=['custom.id']
        )
    """
    anonymizer = BiasAnonymizer(strategy)
    return anonymizer.anonymize(profile, fields_to_anonymize, fields_to_preserve)


def analyze_profile(profile: Union[Dict, str]) -> Dict[str, Any]:
    """
    Analyze a profile for bias without anonymizing.
    
    Returns:
        Risk report with score and detected bias categories
    """
    anonymizer = BiasAnonymizer()
    return anonymizer.analyze(profile)


# For backward compatibility
def simple_anonymize(json_data: Union[Dict, str], 
                    remove_bias: bool = True) -> Dict[str, Any]:
    """
    Simple anonymization function for backward compatibility.
    
    Args:
        json_data: JSON data to anonymize
        remove_bias: If True, removes bias words. If False, replaces with tokens.
    
    Returns:
        Anonymized JSON
    """
    strategy = "remove" if remove_bias else "replace"
    return anonymize_profile(json_data, strategy=strategy)


if __name__ == "__main__":
    # Test the wrapper
    test_profile = {
        "core": {
            "businessTitle": "Senior white male engineer from wealthy family",
            "jobCode": "ENG_001"
        },
        "experience": {
            "experiences": [{
                "company": "Stanford University",
                "description": "Led team of Asian engineers"
            }]
        }
    }
    
    # Test different usage patterns
    print("Testing BiasAnonymizer Wrapper\n" + "="*50)
    
    # Method 1: Using class
    anonymizer = BiasAnonymizer()
    result1 = anonymizer.anonymize(test_profile)
    print("\n1. Class method (remove):", result1["core"]["businessTitle"])
    
    # Method 2: Direct function
    result2 = anonymize_profile(test_profile, strategy="replace")
    print("\n2. Direct function (replace):", result2["core"]["businessTitle"])
    
    # Method 3: With custom fields
    result3 = anonymize_profile(
        test_profile,
        fields_to_anonymize=["core.jobCode"],  # Normally preserved
        strategy="remove"
    )
    print("\n3. With custom fields:", result3["core"].get("jobCode", "[ANONYMIZED]"))
    
    # Method 4: Analysis
    analysis = analyze_profile(test_profile)
    print("\n4. Analysis - Risk Score:", analysis["risk_score"])
    print("   Bias categories found:", ", ".join(analysis["bias_categories_found"]))
