"""
Bias Anonymizer Package

A comprehensive tool for detecting and anonymizing bias-inducing information 
and PII in structured JSON data using Microsoft Presidio.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .anonymizer import JSONAnonymizer
from .config import AnonymizerConfig, BiasCategories, OperatorTypes
from .bias_words import BiasWords
from .exceptions import AnonymizerException, ConfigurationError, ValidationError

__all__ = [
    "JSONAnonymizer",
    "AnonymizerConfig",
    "BiasCategories",
    "OperatorTypes",
    "BiasWords",
    "AnonymizerException",
    "ConfigurationError",
    "ValidationError",
]
