"""
Configuration module for the bias anonymizer.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import yaml
from pathlib import Path


class BiasCategories(Enum):
    """Enumeration of supported bias categories."""
    GENDER = "gender"
    RACE_ETHNICITY = "race_ethnicity"
    AGE = "age"
    DISABILITY = "disability"
    MARITAL_STATUS = "marital_status"
    NATIONALITY = "nationality"
    SEXUAL_ORIENTATION = "sexual_orientation"
    RELIGION = "religion"
    POLITICAL_AFFILIATION = "political_affiliation"
    SOCIOECONOMIC_BACKGROUND = "socioeconomic_background"
    PREGNANCY_MATERNITY = "pregnancy_maternity"
    UNION_MEMBERSHIP = "union_membership"
    HEALTH_CONDITION = "health_condition"
    CRIMINAL_BACKGROUND = "criminal_background"


class OperatorTypes(Enum):
    """Enumeration of anonymization operators."""
    REPLACE = "replace"
    MASK = "mask"
    HASH = "hash"
    ENCRYPT = "encrypt"
    REDACT = "redact"
    KEEP = "keep"
    REMOVE = "remove"


@dataclass
class AnonymizerConfig:
    """
    Configuration class for the anonymizer.
    
    Attributes:
        detect_bias: Whether to detect bias indicators
        detect_pii: Whether to detect PII
        bias_categories: List of bias categories to detect (None = all)
        confidence_threshold: Minimum confidence score for detection
        language: Language for analysis
        operators: Anonymization operators per entity type
        replacements: Replacement values per entity type
        custom_recognizers: List of custom recognizers
        encryption_key: Key for encryption operator
        preserve_structure: Whether to preserve JSON structure
        batch_size: Batch size for processing
        parallel_processing: Whether to use parallel processing
    """
    
    # Detection settings
    detect_bias: bool = True
    detect_pii: bool = True
    bias_categories: Optional[List[str]] = None
    confidence_threshold: float = 0.7
    language: str = "en"
    
    # Anonymization settings
    operators: Dict[str, str] = field(default_factory=lambda: {
        "PERSON": "replace",
        "EMAIL_ADDRESS": "mask",
        "PHONE_NUMBER": "hash",
        "LOCATION": "replace",
        "DATE_TIME": "replace",
        "CREDIT_CARD": "mask",
        "IP_ADDRESS": "mask",
        "BIAS_INDICATOR": "remove",
        "DEFAULT": "replace"
    })
    
    replacements: Dict[str, str] = field(default_factory=lambda: {
        "PERSON": "[PERSON]",
        "EMAIL_ADDRESS": "[EMAIL]",
        "PHONE_NUMBER": "[PHONE]",
        "LOCATION": "[LOCATION]",
        "DATE_TIME": "[DATE]",
        "DEFAULT": ""
    })
    
    # Advanced settings
    custom_recognizers: List[Any] = field(default_factory=list)
    encryption_key: Optional[str] = None
    preserve_structure: bool = True
    batch_size: int = 100
    parallel_processing: bool = False
    
    @classmethod
    def from_yaml(cls, file_path: str) -> 'AnonymizerConfig':
        """
        Load configuration from YAML file.
        
        Args:
            file_path: Path to YAML configuration file
            
        Returns:
            AnonymizerConfig instance
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Convert bias categories from strings if present
        if 'bias_categories' in data and data['bias_categories']:
            data['bias_categories'] = [
                cat if isinstance(cat, str) else cat.value
                for cat in data['bias_categories']
            ]
        
        return cls(**data)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AnonymizerConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            AnonymizerConfig instance
        """
        return cls(**config_dict)
    
    def to_yaml(self, file_path: str):
        """
        Save configuration to YAML file.
        
        Args:
            file_path: Path to save YAML file
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'detect_bias': self.detect_bias,
            'detect_pii': self.detect_pii,
            'bias_categories': self.bias_categories,
            'confidence_threshold': self.confidence_threshold,
            'language': self.language,
            'operators': self.operators,
            'replacements': self.replacements,
            'preserve_structure': self.preserve_structure,
            'batch_size': self.batch_size,
            'parallel_processing': self.parallel_processing
        }
        
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def validate(self):
        """
        Validate configuration settings.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if self.confidence_threshold < 0 or self.confidence_threshold > 1:
            raise ValueError("Confidence threshold must be between 0 and 1")
        
        if self.batch_size < 1:
            raise ValueError("Batch size must be positive")
        
        if self.bias_categories:
            valid_categories = [cat.value for cat in BiasCategories]
            for cat in self.bias_categories:
                if cat not in valid_categories:
                    raise ValueError(f"Invalid bias category: {cat}")
        
        valid_operators = [op.value for op in OperatorTypes]
        for entity, operator in self.operators.items():
            if operator not in valid_operators:
                raise ValueError(f"Invalid operator '{operator}' for entity '{entity}'")
