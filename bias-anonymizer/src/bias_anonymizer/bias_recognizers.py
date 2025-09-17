"""
Unified bias recognizer that efficiently detects all bias categories.
"""

import re
from typing import List, Dict, Set, Tuple
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
from .bias_words import BiasWords


class UnifiedBiasRecognizer(PatternRecognizer):
    """
    A single recognizer that detects all bias categories efficiently.
    Uses a word-to-category mapping for fast lookups and category tracking.
    """
    
    def __init__(self):
        # Create word-to-category mapping
        self.word_to_category = BiasWords.get_word_to_category_mapping()
        
        # Create patterns for all bias words
        patterns = self._create_patterns()
        
        # Initialize with a generic entity type
        # We'll override this in the analyze method to provide specific categories
        super().__init__(
            supported_entity="BIAS",
            patterns=patterns,
            name="Unified Bias Recognizer"
        )
        
        # Store category-specific entity types
        self.category_entity_types = {
            'gender': 'GENDER_BIAS',
            'race_ethnicity': 'RACE_BIAS',
            'age': 'AGE_BIAS',
            'disability': 'DISABILITY_BIAS',
            'marital_status': 'FAMILY_STATUS_BIAS',
            'nationality': 'NATIONALITY_BIAS',
            'sexual_orientation': 'SEXUAL_ORIENTATION_BIAS',
            'religion': 'RELIGION_BIAS',
            'political_affiliation': 'POLITICAL_BIAS',
            'socioeconomic_background': 'SOCIOECONOMIC_BIAS',
            'pregnancy_maternity': 'MATERNITY_BIAS',
            'union_membership': 'UNION_BIAS',
            'health_condition': 'HEALTH_BIAS',
            'criminal_background': 'CRIMINAL_BIAS'
        }
    
    def _create_patterns(self) -> List[Pattern]:
        """Create patterns for all bias words."""
        patterns = []
        
        # Group words by length and type for efficient pattern creation
        single_words = []
        multi_word_phrases = []
        
        for word in BiasWords.get_all_bias_words():
            if ' ' in word:
                multi_word_phrases.append(word)
            else:
                single_words.append(word)
        
        # Sort by length (longest first) to match longer phrases first
        multi_word_phrases.sort(key=len, reverse=True)
        
        # Create patterns for multi-word phrases
        for phrase in multi_word_phrases:
            pattern = Pattern(
                name=f"bias_phrase_{phrase.replace(' ', '_').lower()}",
                regex=r'\b' + re.escape(phrase) + r'\b',
                score=0.9
            )
            patterns.append(pattern)
        
        # Create patterns for single words (with optional plural)
        for word in single_words:
            pattern = Pattern(
                name=f"bias_word_{word.lower()}",
                regex=r'\b' + re.escape(word) + r's?\b',
                score=0.85
            )
            patterns.append(pattern)
        
        return patterns
    
    def analyze(self, text: str, entities: List[str], nlp_artifacts=None) -> List[RecognizerResult]:
        """
        Analyze text for bias words and return results with specific category types.
        """
        # Get base results from parent class
        results = super().analyze(text, entities, nlp_artifacts)
        
        # Enhance results with specific category information
        enhanced_results = []
        for result in results:
            # Extract the matched word from text
            matched_text = text[result.start:result.end].lower()
            
            # Remove plural 's' if present for lookup
            if matched_text.endswith('s') and matched_text[:-1] in self.word_to_category:
                lookup_text = matched_text[:-1]
            else:
                lookup_text = matched_text
            
            # Identify category
            category = self.word_to_category.get(lookup_text, None)
            
            if category:
                # Create new result with specific entity type
                entity_type = self.category_entity_types.get(category, 'BIAS_INDICATOR')
                enhanced_result = RecognizerResult(
                    entity_type=entity_type,
                    start=result.start,
                    end=result.end,
                    score=result.score
                )
                enhanced_results.append(enhanced_result)
            else:
                # Keep original result if category not found
                enhanced_results.append(result)
        
        return enhanced_results


class CategoryTrackingBiasRecognizer:
    """
    A wrapper class that tracks which bias categories were detected and removed.
    Useful for reporting and analytics.
    """
    
    def __init__(self):
        self.recognizer = UnifiedBiasRecognizer()
        self.detected_categories = {}
        
    def analyze_and_track(self, text: str) -> Tuple[List[RecognizerResult], Dict[str, List[str]]]:
        """
        Analyze text and track which categories and specific words were found.
        
        Returns:
            Tuple of (results, category_tracking_dict)
        """
        results = self.recognizer.analyze(text, entities=[], nlp_artifacts=None)
        
        # Track categories and specific words
        tracking = {}
        for result in results:
            category = result.entity_type.replace('_BIAS', '').lower()
            matched_word = text[result.start:result.end]
            
            if category not in tracking:
                tracking[category] = []
            if matched_word not in tracking[category]:
                tracking[category].append(matched_word)
        
        return results, tracking
    
    def get_statistics(self, text: str) -> Dict:
        """
        Get detailed statistics about bias detection in text.
        """
        results, tracking = self.analyze_and_track(text)
        
        stats = {
            'total_bias_words_found': len(results),
            'categories_found': list(tracking.keys()),
            'category_counts': {cat: len(words) for cat, words in tracking.items()},
            'specific_words': tracking
        }
        
        return stats


# Individual category recognizers using the unified approach
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
        age_words = (BiasWords.young_age_words + BiasWords.middle_age_words + 
                     BiasWords.older_age_words)
        for word in age_words:
            patterns.append(
                Pattern(name="AGE", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="AGE_BIAS", patterns=patterns)


class DisabilityBiasRecognizer(PatternRecognizer):
    """Recognizer for disability-related bias."""
    def __init__(self):
        patterns = []
        disability_words = BiasWords.disabled_words + BiasWords.able_bodied_words
        for word in disability_words:
            patterns.append(
                Pattern(name="DISABILITY", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="DISABILITY_BIAS", patterns=patterns)


class MaritalStatusBiasRecognizer(PatternRecognizer):
    """Recognizer for marital/family status-related bias."""
    def __init__(self):
        patterns = []
        family_words = (BiasWords.single_status_words + BiasWords.married_status_words + 
                        BiasWords.parent_status_words)
        for word in family_words:
            patterns.append(
                Pattern(name="FAMILY", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="FAMILY_STATUS_BIAS", patterns=patterns)


class NationalityBiasRecognizer(PatternRecognizer):
    """Recognizer for nationality-related bias."""
    def __init__(self):
        patterns = []
        nationality_words = BiasWords.domestic_nationality_words + BiasWords.foreign_nationality_words
        for word in nationality_words:
            patterns.append(
                Pattern(name="NATIONALITY", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="NATIONALITY_BIAS", patterns=patterns)


class SexualOrientationBiasRecognizer(PatternRecognizer):
    """Recognizer for sexual orientation-related bias."""
    def __init__(self):
        patterns = []
        orientation_words = BiasWords.heterosexual_words + BiasWords.lgbtq_words
        for word in orientation_words:
            if word.upper() == "LGBTQ":
                patterns.append(
                    Pattern(name="LGBTQ", regex=r'\bLGBTQ\+?\b', score=0.9)
                )
            else:
                patterns.append(
                    Pattern(name="ORIENTATION", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
                )
        super().__init__(supported_entity="SEXUAL_ORIENTATION_BIAS", patterns=patterns)


class ReligionBiasRecognizer(PatternRecognizer):
    """Recognizer for religion-related bias."""
    def __init__(self):
        patterns = []
        religion_words = (BiasWords.christian_words + BiasWords.muslim_words + 
                          BiasWords.jewish_words + BiasWords.eastern_religion_words + 
                          BiasWords.secular_words)
        for word in religion_words:
            patterns.append(
                Pattern(name="RELIGION", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="RELIGION_BIAS", patterns=patterns)


class PoliticalBiasRecognizer(PatternRecognizer):
    """Recognizer for political-related bias."""
    def __init__(self):
        patterns = []
        political_words = BiasWords.conservative_words + BiasWords.liberal_words
        for word in political_words:
            patterns.append(
                Pattern(name="POLITICAL", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="POLITICAL_BIAS", patterns=patterns)


class SocioeconomicBiasRecognizer(PatternRecognizer):
    """Recognizer for socioeconomic-related bias."""
    def __init__(self):
        patterns = []
        socioeconomic_words = BiasWords.wealthy_words + BiasWords.working_class_words
        for word in socioeconomic_words:
            patterns.append(
                Pattern(name="SOCIOECONOMIC", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="SOCIOECONOMIC_BIAS", patterns=patterns)


class PregnancyMaternityBiasRecognizer(PatternRecognizer):
    """Recognizer for pregnancy/maternity-related bias."""
    def __init__(self):
        patterns = []
        for word in BiasWords.pregnancy_maternity_words:
            patterns.append(
                Pattern(name="MATERNITY", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="MATERNITY_BIAS", patterns=patterns)


class UnionMembershipBiasRecognizer(PatternRecognizer):
    """Recognizer for union membership-related bias."""
    def __init__(self):
        patterns = []
        union_words = BiasWords.union_words + BiasWords.non_union_words
        for word in union_words:
            patterns.append(
                Pattern(name="UNION", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="UNION_BIAS", patterns=patterns)


class HealthConditionBiasRecognizer(PatternRecognizer):
    """Recognizer for health condition-related bias."""
    def __init__(self):
        patterns = []
        for word in BiasWords.health_condition_words:
            patterns.append(
                Pattern(name="HEALTH", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="HEALTH_BIAS", patterns=patterns)


class CriminalBackgroundBiasRecognizer(PatternRecognizer):
    """Recognizer for criminal background-related bias."""
    def __init__(self):
        patterns = []
        criminal_words = BiasWords.criminal_background_words + BiasWords.clean_background_words
        for word in criminal_words:
            patterns.append(
                Pattern(name="CRIMINAL", regex=r'\b' + re.escape(word) + r's?\b', score=0.9)
            )
        super().__init__(supported_entity="CRIMINAL_BIAS", patterns=patterns)


# Backward compatibility
FamilyStatusBiasRecognizer = MaritalStatusBiasRecognizer
EducationBiasRecognizer = SocioeconomicBiasRecognizer  # Education is part of socioeconomic


class BiasRecognizerFactory:
    """Factory class for creating bias recognizers."""
    
    @staticmethod
    def create_recognizer(category: str):
        """
        Create a recognizer for a specific bias category.
        
        Args:
            category: Bias category name
            
        Returns:
            PatternRecognizer instance for the category
        """
        recognizer_map = {
            'gender': GenderBiasRecognizer,
            'race_ethnicity': RaceBiasRecognizer,
            'age': AgeBiasRecognizer,
            'disability': DisabilityBiasRecognizer,
            'marital_status': MaritalStatusBiasRecognizer,
            'nationality': NationalityBiasRecognizer,
            'sexual_orientation': SexualOrientationBiasRecognizer,
            'religion': ReligionBiasRecognizer,
            'political_affiliation': PoliticalBiasRecognizer,
            'socioeconomic_background': SocioeconomicBiasRecognizer,
            'pregnancy_maternity': PregnancyMaternityBiasRecognizer,
            'union_membership': UnionMembershipBiasRecognizer,
            'health_condition': HealthConditionBiasRecognizer,
            'criminal_background': CriminalBackgroundBiasRecognizer
        }
        
        recognizer_class = recognizer_map.get(category)
        if not recognizer_class:
            raise ValueError(f"Unknown bias category: {category}")
        return recognizer_class()
    
    @staticmethod
    def create_all_recognizers():
        """
        Create recognizers for all bias categories.
        
        Returns:
            List of PatternRecognizer instances
        """
        return [
            GenderBiasRecognizer(),
            RaceBiasRecognizer(),
            AgeBiasRecognizer(),
            DisabilityBiasRecognizer(),
            MaritalStatusBiasRecognizer(),
            NationalityBiasRecognizer(),
            SexualOrientationBiasRecognizer(),
            ReligionBiasRecognizer(),
            PoliticalBiasRecognizer(),
            SocioeconomicBiasRecognizer(),
            PregnancyMaternityBiasRecognizer(),
            UnionMembershipBiasRecognizer(),
            HealthConditionBiasRecognizer(),
            CriminalBackgroundBiasRecognizer()
        ]
