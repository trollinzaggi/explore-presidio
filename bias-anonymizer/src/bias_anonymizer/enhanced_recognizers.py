"""
Enhanced recognizers for better PII detection
"""

from presidio_analyzer import Pattern, PatternRecognizer


class EnhancedSSNRecognizer(PatternRecognizer):
    """
    Enhanced SSN recognizer that catches more patterns.
    """
    
    PATTERNS = [
        Pattern(
            "SSN_WITH_DASHES",
            r"\b\d{3}-\d{2}-\d{4}\b",
            0.9
        ),
        Pattern(
            "SSN_WITH_SPACES",
            r"\b\d{3}\s\d{2}\s\d{4}\b",
            0.9
        ),
        Pattern(
            "SSN_NO_SEPARATOR",
            r"\b\d{9}\b",
            0.7  # Lower confidence for 9 consecutive digits
        ),
        Pattern(
            "SSN_WITH_PREFIX",
            r"(?i)(?:ssn|social\s*security|ss#|ss\s*#|social)\s*:?\s*\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
            0.95  # Higher confidence when explicitly labeled - (?i) makes it case insensitive
        ),
    ]
    
    def __init__(self):
        super().__init__(
            supported_entity="US_SSN",
            patterns=self.PATTERNS,
            name="Enhanced SSN Recognizer"
        )


class EnhancedPhoneRecognizer(PatternRecognizer):
    """
    Enhanced phone recognizer that catches more US phone patterns.
    """
    
    PATTERNS = [
        # Standard formats
        Pattern(
            "PHONE_WITH_DASHES",
            r"\b\d{3}-\d{3}-\d{4}\b",
            0.85
        ),
        Pattern(
            "PHONE_WITH_PARENTHESES",
            r"\b\(\d{3}\)\s*\d{3}-\d{4}\b",
            0.9
        ),
        Pattern(
            "PHONE_WITH_DOTS",
            r"\b\d{3}\.\d{3}\.\d{4}\b",
            0.85
        ),
        Pattern(
            "PHONE_WITH_SPACES",
            r"\b\d{3}\s\d{3}\s\d{4}\b",
            0.8
        ),
        # Short formats (local numbers)
        Pattern(
            "PHONE_SHORT",
            r"\b\d{3}-\d{4}\b",
            0.7  # Lower confidence for short format
        ),
        # Custom format with letters (various formats)
        Pattern(
            "PHONE_WITH_LETTERS",
            r"(?i)\b\d{3}-[A-Z]{2}-[A-Z]{4}\b",
            0.6  # Lower confidence for letter format
        ),
        # Specific vanity numbers
        Pattern(
            "PHONE_VANITY",
            r"(?i)\b555-[A-Z]{2}-[A-Z]{4}\b",
            0.8  # Higher confidence for 555 vanity numbers
        ),
        # International format
        Pattern(
            "PHONE_INTERNATIONAL",
            r"\+1\s?\(?\d{3}\)?\s?\d{3}-?\d{4}\b",
            0.95
        ),
        # With extension
        Pattern(
            "PHONE_WITH_EXT",
            r"\b\d{3}-\d{3}-\d{4}\s*(?:ext|x|extension)\s*\d{1,5}\b",
            0.95
        ),
        # Toll-free numbers
        Pattern(
            "PHONE_TOLL_FREE",
            r"\b(?:800|888|877|866|855|844|833)\-\d{3}-\d{4}\b",
            0.9
        ),
    ]
    
    def __init__(self):
        super().__init__(
            supported_entity="PHONE_NUMBER",
            patterns=self.PATTERNS,
            name="Enhanced Phone Recognizer"
        )


class EnhancedAddressRecognizer(PatternRecognizer):
    """
    Enhanced address recognizer for US addresses.
    """
    
    PATTERNS = [
        # Street addresses with street suffix
        Pattern(
            "STREET_ADDRESS",
            r"\b\d{1,5}\s+[\w\s]{1,30}\s+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Lane|Ln|Drive|Dr|Court|Ct|Way|Parkway|Pkwy|Circle|Cir|Plaza|Place|Pl)\b",
            0.85
        ),
        # PO Box
        Pattern(
            "PO_BOX",
            r"(?i)\bP\.?O\.?\s*Box\s*\d+\b",
            0.95
        ),
        # Full address with city, state, zip
        Pattern(
            "FULL_ADDRESS",
            r"\b\d{1,5}\s+[\w\s]{1,30},\s*[\w\s]{2,30},\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?\b",
            0.95
        ),
        # Just zip code
        Pattern(
            "ZIP_CODE",
            r"\b\d{5}(?:-\d{4})?\b",
            0.6  # Lower confidence for standalone zip
        ),
        # Apartment/Suite numbers
        Pattern(
            "APT_SUITE",
            r"(?i)\b(?:apt|apartment|suite|ste|unit|#)\s*\w{1,10}\b",
            0.7
        ),
    ]
    
    def __init__(self):
        super().__init__(
            supported_entity="LOCATION", 
            patterns=self.PATTERNS,
            name="Enhanced Address Recognizer"
        )
