"""
Configuration loader for bias anonymizer
Loads configuration from YAML files and provides it to the anonymizer
"""

import os
from pathlib import Path
from typing import Dict, Optional, Any, Set, List
import yaml

from bias_anonymizer.talent_profile_anonymizer import TalentProfileAnonymizer, TalentProfileConfig
from presidio_anonymizer.entities import OperatorConfig


def load_config_from_yaml(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to YAML config file. 
                    If None, uses default_config.yaml
    
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Use default config
        current_dir = Path(__file__).parent.parent.parent
        config_path = current_dir / "config" / "default_config.yaml"
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def create_anonymizer_from_config(config_path: Optional[str] = None) -> TalentProfileAnonymizer:
    """
    Create a TalentProfileAnonymizer from a YAML configuration file.
    
    Args:
        config_path: Path to YAML config file
    
    Returns:
        Configured TalentProfileAnonymizer instance
    """
    yaml_config = load_config_from_yaml(config_path)
    
    # Extract all configuration from YAML
    strategy = yaml_config.get('anonymization_strategy', 'redact')
    
    # Convert lists to sets for field configurations
    preserve_fields = set(yaml_config.get('preserve_fields', []))
    always_anonymize_fields = set(yaml_config.get('always_anonymize_fields', []))
    
    # Get special handling fields
    special_handling_fields = yaml_config.get('special_handling_fields', {})
    
    # Get replacement tokens
    replacement_tokens = yaml_config.get('replacement_tokens', {})
    
    # Get operators
    operators = yaml_config.get('operators', {})
    
    # Get detection settings
    detect_bias = yaml_config.get('detect_bias', True)
    detect_pii = yaml_config.get('detect_pii', True)
    confidence_threshold = yaml_config.get('confidence_threshold', 0.7)
    
    # Create TalentProfileConfig with ALL settings from YAML
    profile_config = TalentProfileConfig(
        preserve_fields=preserve_fields,
        always_anonymize_fields=always_anonymize_fields,
        special_handling_fields=special_handling_fields,
        anonymization_strategy=strategy,
        replacement_tokens=replacement_tokens,
        operators=operators,
        detect_bias=detect_bias,
        detect_pii=detect_pii,
        confidence_threshold=confidence_threshold
    )
    
    # Create and return anonymizer
    return TalentProfileAnonymizer(profile_config)


def create_custom_config_yaml(
    output_path: str,
    strategy: str = "redact",
    preserve_fields: Optional[List[str]] = None,
    always_anonymize_fields: Optional[List[str]] = None,
    special_handling_fields: Optional[Dict[str, str]] = None,
    replacement_tokens: Optional[Dict[str, str]] = None
) -> None:
    """
    Create a custom YAML configuration file.
    
    Args:
        output_path: Path where to save the YAML file
        strategy: Anonymization strategy
        preserve_fields: Fields to preserve
        always_anonymize_fields: Fields to always anonymize
        special_handling_fields: Special handling rules
        replacement_tokens: Custom replacement tokens
    """
    config = {
        'anonymization_strategy': strategy,
        'detect_bias': True,
        'detect_pii': True,
        'confidence_threshold': 0.7,
        'language': 'en'
    }
    
    if preserve_fields:
        config['preserve_fields'] = preserve_fields
    
    if always_anonymize_fields:
        config['always_anonymize_fields'] = always_anonymize_fields
    
    if special_handling_fields:
        config['special_handling_fields'] = special_handling_fields
    
    if replacement_tokens:
        config['replacement_tokens'] = replacement_tokens
    
    # Set default operators based on strategy
    if strategy == "redact":
        config['operators'] = {
            'GENDER_BIAS': 'redact',
            'RACE_BIAS': 'redact',
            'AGE_BIAS': 'redact',
            'DEFAULT': 'redact'
        }
    elif strategy == "replace":
        config['operators'] = {
            'GENDER_BIAS': 'replace',
            'RACE_BIAS': 'replace',
            'AGE_BIAS': 'replace',
            'DEFAULT': 'replace'
        }
        if not replacement_tokens:
            config['replacement_tokens'] = {
                'GENDER_BIAS': '[GENDER]',
                'RACE_BIAS': '[RACE]',
                'AGE_BIAS': '[AGE]',
                'DEFAULT': '[REDACTED]'
            }
    
    # Save to YAML
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Custom configuration saved to: {output_path}")


def get_config_summary(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a summary of the configuration.
    
    Returns:
        Dictionary with configuration summary
    """
    config = load_config_from_yaml(config_path)
    
    summary = {
        'anonymization_strategy': config.get('anonymization_strategy', 'redact'),
        'detect_bias': config.get('detect_bias', True),
        'detect_pii': config.get('detect_pii', True),
        'confidence_threshold': config.get('confidence_threshold', 0.7),
        'preserve_fields_count': len(config.get('preserve_fields', [])),
        'anonymize_fields_count': len(config.get('always_anonymize_fields', [])),
        'special_handling_count': len(config.get('special_handling_fields', {})),
        'has_replacement_tokens': bool(config.get('replacement_tokens', {})),
        'operators_configured': len(config.get('operators', {}))
    }
    
    return summary


def validate_config(config_path: Optional[str] = None) -> bool:
    """
    Validate a configuration file.
    
    Returns:
        True if valid, raises exception if invalid
    """
    config = load_config_from_yaml(config_path)
    
    # Valid Presidio operators
    valid_operators = {'replace', 'mask', 'hash', 'encrypt', 'redact', 'keep'}
    
    # Valid strategies
    valid_strategies = {'redact', 'replace', 'custom'}
    
    # Check strategy
    strategy = config.get('anonymization_strategy', 'redact')
    if strategy not in valid_strategies:
        raise ValueError(f"Invalid strategy '{strategy}'. Valid strategies: {valid_strategies}")
    
    # Check operators if present
    operators = config.get('operators', {})
    for entity, operator in operators.items():
        if operator not in valid_operators:
            raise ValueError(f"Invalid operator '{operator}' for entity '{entity}'. "
                           f"Valid operators are: {valid_operators}")
    
    # Check special handling actions
    valid_actions = {'hash', 'year_only', 'categorize', 'remove'}
    special_handling = config.get('special_handling_fields', {})
    for field, action in special_handling.items():
        if action not in valid_actions:
            raise ValueError(f"Invalid action '{action}' for field '{field}'. "
                           f"Valid actions are: {valid_actions}")
    
    # Check confidence threshold
    threshold = config.get('confidence_threshold', 0.7)
    if not 0 <= threshold <= 1:
        raise ValueError(f"Confidence threshold must be between 0 and 1, got {threshold}")
    
    return True


def merge_configs(base_config_path: str, override_config_path: str) -> Dict[str, Any]:
    """
    Merge two configuration files, with override taking precedence.
    
    Args:
        base_config_path: Path to base configuration
        override_config_path: Path to override configuration
    
    Returns:
        Merged configuration dictionary
    """
    base_config = load_config_from_yaml(base_config_path)
    override_config = load_config_from_yaml(override_config_path)
    
    # Deep merge - override takes precedence
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            # Merge dictionaries
            merged[key] = {**merged[key], **value}
        elif isinstance(value, list) and key in merged and isinstance(merged[key], list):
            # For lists, replace entirely (don't merge)
            merged[key] = value
        else:
            # Simple override
            merged[key] = value
    
    return merged


# Example usage
if __name__ == "__main__":
    # Load default config
    try:
        print("Loading default configuration...")
        anonymizer = create_anonymizer_from_config()
        
        print("\nConfiguration Summary:")
        summary = get_config_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        print("\nValidating configuration...")
        if validate_config():
            print("✓ Configuration is valid")
        
        # Test with sample data
        test_profile = {
            "core": {
                "businessTitle": "Senior white male engineer",
                "jobCode": "ENG_001"
            }
        }
        
        result = anonymizer.anonymize_talent_profile(test_profile)
        print(f"\nTest anonymization:")
        print(f"  Original: {test_profile['core']['businessTitle']}")
        print(f"  Anonymized: {result['core']['businessTitle']}")
        
        # Create a custom config
        print("\n\nCreating custom configuration...")
        create_custom_config_yaml(
            "custom_example.yaml",
            strategy="replace",
            preserve_fields=["core.jobCode", "core.rank.code"],
            always_anonymize_fields=["core.businessTitle", "core.description"],
            replacement_tokens={
                "GENDER_BIAS": "person",
                "RACE_BIAS": "individual"
            }
        )
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
