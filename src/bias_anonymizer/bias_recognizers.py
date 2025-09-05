"""
Custom recognizers for bias detection.
"""

import re
from typing import List, Set
from presidio_analyzer import EntityRecognizer, RecognizerResult, Pattern, PatternRecognizer

from .bias_words import BiasWords


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
