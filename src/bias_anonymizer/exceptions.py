"""
Custom exceptions for the bias anonymizer.
"""


class AnonymizerException(Exception):
    """Base exception for anonymizer errors."""
    pass


class ConfigurationError(AnonymizerException):
    """Exception raised for configuration errors."""
    pass


class ValidationError(AnonymizerException):
    """Exception raised for validation errors."""
    pass


class RecognizerError(AnonymizerException):
    """Exception raised for recognizer errors."""
    pass


class ProcessingError(AnonymizerException):
    """Exception raised during processing."""
    pass
