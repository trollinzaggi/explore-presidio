"""
Custom recognizers for bias detection.
"""

import re
from typing import List, Set
from presidio_analyzer import EntityRecognizer, RecognizerResult, Pattern, PatternRecognizer

from .bias_words import BiasWords


# Specific recognizer classes for each bias category
class GenderBiasRecognizer(PatternRecognizer):
    """Recognizer for gender-related bias."""
    def __init__(self):
        patterns = []
        for word in BiasWords.male_words + BiasWords.female_words + BiasWords.gender_neutral_words:
            patterns.append(
                Pattern(name="GENDER", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="GENDER_BIAS", patterns=patterns)


class RaceBiasRecognizer(PatternRecognizer):
    """Recognizer for race/ethnicity-related bias."""
    def __init__(self):
        patterns = []
        # Combine all race/ethnicity word lists
        race_words = (BiasWords.european_words + BiasWords.african_words + 
                      BiasWords.asian_words + BiasWords.hispanic_words + 
                      BiasWords.middle_eastern_words)
        for word in race_words:
            patterns.append(
                Pattern(name="RACE", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="RACE_BIAS", patterns=patterns)


class AgeBiasRecognizer(PatternRecognizer):
    """Recognizer for age-related bias."""
    def __init__(self):
        patterns = []
        # Combine all age word lists
        age_words = (BiasWords.young_age_words + BiasWords.middle_age_words + 
                     BiasWords.older_age_words)
        for word in age_words:
            patterns.append(
                Pattern(name="AGE", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="AGE_BIAS", patterns=patterns)


class SocioeconomicBiasRecognizer(PatternRecognizer):
    """Recognizer for socioeconomic-related bias."""
    def __init__(self):
        patterns = []
        # Combine wealthy and working class words
        socioeconomic_words = BiasWords.wealthy_words + BiasWords.working_class_words
        for word in socioeconomic_words:
            patterns.append(
                Pattern(name="SOCIOECONOMIC", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="SOCIOECONOMIC_BIAS", patterns=patterns)


class ReligionBiasRecognizer(PatternRecognizer):
    """Recognizer for religion-related bias."""
    def __init__(self):
        patterns = []
        # Combine all religion words
        religion_words = (BiasWords.christian_words + BiasWords.muslim_words + 
                          BiasWords.jewish_words + BiasWords.eastern_religion_words + 
                          BiasWords.secular_words)
        for word in religion_words:
            patterns.append(
                Pattern(name="RELIGION", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="RELIGION_BIAS", patterns=patterns)


class NationalityBiasRecognizer(PatternRecognizer):
    """Recognizer for nationality-related bias."""
    def __init__(self):
        patterns = []
        # Combine domestic and foreign nationality words
        nationality_words = BiasWords.domestic_nationality_words + BiasWords.foreign_nationality_words
        for word in nationality_words:
            patterns.append(
                Pattern(name="NATIONALITY", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="NATIONALITY_BIAS", patterns=patterns)


class DisabilityBiasRecognizer(PatternRecognizer):
    """Recognizer for disability-related bias."""
    def __init__(self):
        patterns = []
        # Combine disabled and able-bodied words
        disability_words = BiasWords.disabled_words + BiasWords.able_bodied_words
        for word in disability_words:
            patterns.append(
                Pattern(name="DISABILITY", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="DISABILITY_BIAS", patterns=patterns)


class PoliticalBiasRecognizer(PatternRecognizer):
    """Recognizer for political-related bias."""
    def __init__(self):
        patterns = []
        # Combine conservative and liberal words
        political_words = BiasWords.conservative_words + BiasWords.liberal_words
        for word in political_words:
            patterns.append(
                Pattern(name="POLITICAL", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="POLITICAL_BIAS", patterns=patterns)


class FamilyStatusBiasRecognizer(PatternRecognizer):
    """Recognizer for family status-related bias."""
    def __init__(self):
        patterns = []
        # Combine all family status words
        family_words = (BiasWords.single_status_words + BiasWords.married_status_words + 
                        BiasWords.parent_status_words)
        for word in family_words:
            patterns.append(
                Pattern(name="FAMILY", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="FAMILY_STATUS_BIAS", patterns=patterns)


class EducationBiasRecognizer(PatternRecognizer):
    """Recognizer for education-related bias."""
    def __init__(self):
        patterns = []
        # Education level words from socioeconomic background
        education_words = ['private school', 'public school', 'ivy league', 'elite', 
                          'prestigious', 'first-generation college', 'scholarship']
        # Institution-related words
        institution_keywords = [
            "university", "college", "institute", "school", "academy",
            "stanford", "harvard", "mit", "yale", "princeton",
            "community college", "state university",
            "top-tier"
        ]
        for word in education_words + institution_keywords:
            # For institution names, match broader patterns
            if word in institution_keywords:
                patterns.append(
                    Pattern(name="INSTITUTION", regex=r'\b\w*\s*' + re.escape(word) + r'\s*\w*', score=0.85)
                )
            else:
                patterns.append(
                    Pattern(name="EDUCATION", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
                )
        super().__init__(supported_entity="EDUCATION_BIAS", patterns=patterns)


class BiasWordRecognizer(EntityRecognizer):
    """Custom recognizer for bias-related words in text."""
    
    def __init__(self, category: str, words: List[str]):
        """
        Initialize bias word recognizer for a specific category.
        
        Args:
            category: The bias category (e.g., 'gender', 'race_ethnicity')
            words: List of words to detect
        """
        self.category = f"{category.upper()}_BIAS"
        self.words = set(word.lower() for word in words)
        self.word_patterns = self._create_word_patterns(words)
        
        super().__init__(
            supported_entities=[self.category],
            supported_language="en",
            name=f"{category}_bias_recognizer"
        )
    
    def _create_word_patterns(self, words: List[str]) -> List[re.Pattern]:
        """Create regex patterns for word matching."""
        patterns = []
        for word in words:
            # Create pattern that matches whole words (case-insensitive)
            if ' ' in word:
                # For phrases, match the exact phrase
                pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            else:
                # For single words, match word boundaries (with optional plural)
                pattern = re.compile(r'\b' + re.escape(word) + r's?\b', re.IGNORECASE)
            patterns.append(pattern)
        return patterns
    
    def analyze(self, text: str, entities: List[str], nlp_artifacts=None) -> List[RecognizerResult]:
        """
        Analyze text for bias words.
        
        Args:
            text: Text to analyze
            entities: List of entities to look for
            nlp_artifacts: NLP artifacts (not used in this recognizer)
            
        Returns:
            List of RecognizerResult with detected bias words
        """
        results = []
        
        # Only process if this recognizer's entity is requested
        if self.category not in entities and "ALL" not in entities:
            return results
        
        # Check each pattern
        for pattern in self.word_patterns:
            for match in pattern.finditer(text):
                result = RecognizerResult(
                    entity_type=self.category,
                    start=match.start(),
                    end=match.end(),
                    score=0.85  # High confidence for exact matches
                )
                results.append(result)
        
        return results


class ComprehensiveBiasRecognizer(PatternRecognizer):
    """
    A comprehensive bias recognizer that detects all bias categories at once.
    Optimized for performance with pattern matching.
    """
    
    def __init__(self):
        """Initialize the comprehensive bias recognizer."""
        # Get all bias words
        all_bias_words = []
        for category_words in BiasWords.get_all_categories().values():
            all_bias_words.extend(category_words)
        
        # Remove duplicates and sort by length (longer phrases first)
        unique_words = list(set(all_bias_words))
        unique_words.sort(key=len, reverse=True)
        
        # Create patterns
        patterns = []
        for word in unique_words:
            if ' ' in word:
                # Multi-word phrase
                pattern_str = r'\b' + re.escape(word) + r'\b'
            else:
                # Single word (with optional plural)
                pattern_str = r'\b' + re.escape(word) + r's?\b'
            
            patterns.append(Pattern(
                name=f"bias_{word.replace(' ', '_').lower()}",
                regex=pattern_str,
                score=0.85
            ))
        
        super().__init__(
            supported_entity="BIAS_INDICATOR",
            patterns=patterns,
            context=[]
        )


class BiasRecognizerFactory:
    """Factory class for creating bias recognizers."""
    
    @staticmethod
    def create_recognizer(category: str) -> BiasWordRecognizer:
        """
        Create a recognizer for a specific bias category.
        
        Args:
            category: Bias category name
            
        Returns:
            BiasWordRecognizer instance
        """
        words = BiasWords.get_category_words(category)
        if not words:
            raise ValueError(f"Unknown bias category: {category}")
        return BiasWordRecognizer(category, words)
    
    @staticmethod
    def create_comprehensive_recognizer() -> ComprehensiveBiasRecognizer:
        """
        Create a comprehensive recognizer for all bias categories.
        
        Returns:
            ComprehensiveBiasRecognizer instance
        """
        return ComprehensiveBiasRecognizer()
    
    @staticmethod
    def create_all_recognizers() -> List[BiasWordRecognizer]:
        """
        Create recognizers for all bias categories.
        
        Returns:
            List of BiasWordRecognizer instances
        """
        recognizers = []
        for category in BiasWords.get_all_categories().keys():
            recognizers.append(BiasRecognizerFactory.create_recognizer(category))
        return recognizers
