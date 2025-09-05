# Custom Bias Word Detection and Anonymization with Microsoft Presidio
# For Employee Talent Profiles

import json
import re
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from presidio_analyzer import (
    AnalyzerEngine, 
    RecognizerRegistry,
    EntityRecognizer,
    RecognizerResult,
    Pattern,
    PatternRecognizer
)
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_structured import StructuredEngine, JsonAnalysisBuilder

# ============================================================================
# BIAS WORD DEFINITIONS
# ============================================================================

class BiasCategory(Enum):
    """Enumeration of bias categories"""
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

@dataclass
class BiasWords:
    """Container for all bias-related words"""
    
    # Gender-related words
    male_words = [
        "he", "him", "his", "man", "male", "boy", "father", "son", "brother",
        "husband", "boyfriend", "gentleman", "guy", "mr", "masculine", "paternal",
        "dad", "father"
    ]
    
    female_words = [
        "she", "her", "hers", "woman", "female", "girl", "mother", "daughter",
        "sister", "wife", "girlfriend", "lady", "ms", "mrs", "feminine", "maternal",
        "mom", "mother"
    ]
    
    gender_neutral_words = [
        "they", "them", "their", "non-binary", "genderfluid", "transgender",
        "agender", "genderqueer", "enby", "gender-neutral", "fluid", "queer"
    ]
    
    # Race and ethnicity demographics
    european_words = [
        "European", "Caucasian", "white", "Anglo", "Nordic", "Germanic",
        "British", "French", "German", "Italian", "Spanish", "Scandinavian"
    ]
    
    african_words = [
        "African", "Black", "Afro-Caribbean", "Sub-Saharan", "Nigerian", "Kenyan",
        "Ethiopian", "Ghanaian", "Somali", "African-American", "Afro", "Caribbean"
    ]
    
    asian_words = [
        "Asian", "Chinese", "Japanese", "Korean", "Vietnamese", "Thai",
        "Indian", "Pakistani", "Filipino", "Indonesian", "Cambodian", "Laotian"
    ]
    
    hispanic_words = [
        "Hispanic", "Latino", "Mexican", "Colombian", "Puerto Rican", "Guatemalan",
        "Cuban", "Peruvian", "Venezuelan", "Argentinian", "Chilean", "Salvadoran"
    ]
    
    middle_eastern_words = [
        "Middle Eastern", "Arab", "Persian", "Lebanese", "Turkish", "Iranian",
        "Iraqi", "Syrian", "Jordanian", "Palestinian", "Egyptian", "Moroccan"
    ]
    
    # Age-related terms
    young_age_words = [
        "young", "millennial", "Gen-Z", "recent graduate", "entry-level", "twenties",
        "early career", "junior", "new", "fresh", "emerging", "rising"
    ]
    
    middle_age_words = [
        "middle-aged", "experienced", "mid-career", "forties", "fifties", "established",
        "seasoned", "mature", "veteran", "accomplished", "proven", "senior-level"
    ]
    
    older_age_words = [
        "senior", "elder", "older worker", "baby boomer", "retirement-age",
        "elderly", "aged", "geriatric", "golden years", "late career", "legacy"
    ]
    
    # Disability status
    disabled_words = [
        "disabled", "wheelchair user", "blind", "deaf", "mobility impaired",
        "visually impaired", "hearing impaired", "handicapped", "special needs",
        "accessibility", "accommodation", "impairment", "disability"
    ]
    
    able_bodied_words = [
        "able-bodied", "non-disabled", "fully capable", "physically fit", "healthy",
        "normal", "typical", "standard", "regular", "conventional", "mainstream"
    ]
    
    # Marital and family status
    single_status_words = [
        "single", "unmarried", "bachelor", "bachelorette", "unattached", "independent",
        "solo", "alone", "unwed", "celibate", "divorced", "separated"
    ]
    
    married_status_words = [
        "married", "spouse", "husband", "wife", "partnership", "committed",
        "wedded", "coupled", "union", "matrimony", "engaged", "relationship"
    ]
    
    parent_status_words = [
        "parent", "mother", "father", "children", "childcare", "family responsibilities",
        "kids", "offspring", "parental", "maternal", "paternal", "guardian"
    ]
    
    # Nationality and citizenship
    domestic_nationality_words = [
        "American", "US citizen", "native-born", "domestic", "local",
        "citizen", "national", "homeland", "indigenous", "native", "patriotic"
    ]
    
    foreign_nationality_words = [
        "foreign", "international", "immigrant", "visa holder", "non-citizen", "overseas",
        "alien", "expatriate", "refugee", "asylum seeker", "migrant", "outsider"
    ]
    
    # Sexual orientation
    heterosexual_words = [
        "heterosexual", "straight", "traditional", "conventional", "normal",
        "typical", "standard", "mainstream", "orthodox", "classical", "regular"
    ]
    
    lgbtq_words = [
        "gay", "lesbian", "homosexual", "LGBTQ", "same-sex", "queer",
        "bisexual", "pansexual", "rainbow", "pride", "alternative", "diverse"
    ]
    
    # Religious affiliations
    christian_words = [
        "Christian", "Catholic", "Protestant", "biblical", "church-going", "faith-based",
        "Baptist", "Methodist", "Presbyterian", "evangelical", "Orthodox", "religious"
    ]
    
    muslim_words = [
        "Muslim", "Islamic", "mosque", "halal", "imam", "Quran",
        "Sunni", "Shia", "hajj", "Ramadan", "prayer", "faithful"
    ]
    
    jewish_words = [
        "Jewish", "Hebrew", "synagogue", "Torah", "Sabbath", "kosher",
        "rabbi", "Passover", "Yom Kippur", "Orthodox", "Conservative", "Reform"
    ]
    
    eastern_religion_words = [
        "Hindu", "Buddhist", "Sikh", "meditation", "karma", "dharma",
        "temple", "monastery", "enlightenment", "spiritual", "Eastern", "philosophy"
    ]
    
    secular_words = [
        "atheist", "secular", "non-religious", "agnostic", "humanist", "rationalist",
        "skeptic", "freethinker", "irreligious", "godless", "scientific", "logical"
    ]
    
    # Political affiliations
    conservative_words = [
        "conservative", "Republican", "right-wing", "traditional values", "patriotic",
        "GOP", "libertarian", "nationalist", "pro-business", "capitalist", "traditional"
    ]
    
    liberal_words = [
        "liberal", "Democratic", "progressive", "left-wing", "social justice",
        "Democrat", "socialist", "activist", "reform", "inclusive", "diverse"
    ]
    
    # Socioeconomic background
    wealthy_words = [
        "wealthy", "privileged", "elite", "upper-class", "private school", "trust fund",
        "affluent", "rich", "luxury", "exclusive", "prestigious", "high-society"
    ]
    
    working_class_words = [
        "working-class", "blue-collar", "public school", "first-generation college", "scholarship",
        "low-income", "disadvantaged", "struggling", "poor", "underprivileged", "modest"
    ]
    
    # Pregnancy and maternity
    pregnancy_maternity_words = [
        "pregnant", "maternity", "expecting", "prenatal", "childbirth", "newborn",
        "breastfeeding", "maternity leave", "baby", "infant", "delivery", "labor"
    ]
    
    # Union membership
    union_words = [
        "union", "unionized", "collective bargaining", "labor union", "organized labor",
        "solidarity", "strike", "picket", "workers rights", "trade union", "guild"
    ]
    
    non_union_words = [
        "non-union", "independent", "individual", "freelance", "contractor",
        "at-will", "right-to-work", "open shop", "merit-based", "competitive", "flexible"
    ]
    
    # Health and medical conditions
    health_condition_words = [
        "diabetes", "depression", "anxiety", "cancer", "HIV", "mental health",
        "chronic illness", "medical condition", "therapy", "medication", "treatment", "recovery"
    ]
    
    # Criminal background
    criminal_background_words = [
        "criminal record", "conviction", "felony", "misdemeanor", "arrest", "charges",
        "prison", "jail", "parole", "probation", "offense", "rehabilitation"
    ]
    
    clean_background_words = [
        "clean record", "no convictions", "law-abiding", "upstanding", "exemplary",
        "trustworthy", "honest", "reliable", "reputable", "respectable", "credible"
    ]
    
    @classmethod
    def get_all_categories(cls) -> Dict[str, List[str]]:
        """Get all bias categories and their associated words"""
        return {
            BiasCategory.GENDER.value: cls.male_words + cls.female_words + cls.gender_neutral_words,
            BiasCategory.RACE_ETHNICITY.value: (cls.european_words + cls.african_words + 
                                                cls.asian_words + cls.hispanic_words + 
                                                cls.middle_eastern_words),
            BiasCategory.AGE.value: cls.young_age_words + cls.middle_age_words + cls.older_age_words,
            BiasCategory.DISABILITY.value: cls.disabled_words + cls.able_bodied_words,
            BiasCategory.MARITAL_STATUS.value: (cls.single_status_words + cls.married_status_words + 
                                                cls.parent_status_words),
            BiasCategory.NATIONALITY.value: cls.domestic_nationality_words + cls.foreign_nationality_words,
            BiasCategory.SEXUAL_ORIENTATION.value: cls.heterosexual_words + cls.lgbtq_words,
            BiasCategory.RELIGION.value: (cls.christian_words + cls.muslim_words + 
                                          cls.jewish_words + cls.eastern_religion_words + 
                                          cls.secular_words),
            BiasCategory.POLITICAL_AFFILIATION.value: cls.conservative_words + cls.liberal_words,
            BiasCategory.SOCIOECONOMIC_BACKGROUND.value: cls.wealthy_words + cls.working_class_words,
            BiasCategory.PREGNANCY_MATERNITY.value: cls.pregnancy_maternity_words,
            BiasCategory.UNION_MEMBERSHIP.value: cls.union_words + cls.non_union_words,
            BiasCategory.HEALTH_CONDITION.value: cls.health_condition_words,
            BiasCategory.CRIMINAL_BACKGROUND.value: (cls.criminal_background_words + 
                                                     cls.clean_background_words)
        }

# ============================================================================
# CUSTOM BIAS RECOGNIZERS FOR PRESIDIO
# ============================================================================

class BiasWordRecognizer(EntityRecognizer):
    """
    Custom recognizer for bias-related words in text.
    Detects words that could introduce bias in employee evaluation.
    """
    
    def __init__(self, category: str, words: List[str]):
        """
        Initialize bias word recognizer for a specific category
        
        Args:
            category: The bias category (e.g., 'GENDER_BIAS', 'RACE_BIAS')
            words: List of words to detect
        """
        self.category = f"{category.upper()}_BIAS"
        self.words = set(word.lower() for word in words)
        self.word_patterns = self._create_word_patterns(words)
        
        # Call parent constructor
        super().__init__(
            supported_entities=[self.category],
            supported_language="en",
            name=f"{category}_bias_recognizer"
        )
    
    def _create_word_patterns(self, words: List[str]) -> List[re.Pattern]:
        """Create regex patterns for word matching"""
        patterns = []
        for word in words:
            # Create pattern that matches whole words (case-insensitive)
            # Handle multi-word phrases
            if ' ' in word:
                # For phrases, match the exact phrase
                pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            else:
                # For single words, match word boundaries
                pattern = re.compile(r'\b' + re.escape(word) + r's?\b', re.IGNORECASE)
            patterns.append(pattern)
        return patterns
    
    def analyze(self, text: str, entities: List[str], nlp_artifacts=None) -> List[RecognizerResult]:
        """
        Analyze text for bias words
        
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
    
    def validate_result(self, pattern_text: str) -> bool:
        """Validate that a detected pattern is actually a bias word"""
        return pattern_text.lower() in self.words


class ComprehensiveBiasRecognizer(PatternRecognizer):
    """
    A comprehensive bias recognizer that detects all bias categories at once
    using pattern matching for better performance.
    """
    
    def __init__(self):
        """Initialize the comprehensive bias recognizer"""
        
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
                name=f"bias_word_{word.replace(' ', '_')}",
                regex=pattern_str,
                score=0.85
            ))
        
        super().__init__(
            supported_entity="BIAS_INDICATOR",
            patterns=patterns,
            context=[]  # No additional context needed
        )


# ============================================================================
# BIAS-AWARE ANONYMIZATION ENGINE
# ============================================================================

class BiasAwareAnonymizer:
    """
    Enhanced anonymization engine that combines Presidio's PII detection
    with custom bias word detection for comprehensive profile anonymization.
    """
    
    def __init__(self, detect_bias: bool = True, bias_categories: List[str] = None):
        """
        Initialize the bias-aware anonymizer
        
        Args:
            detect_bias: Whether to detect and remove bias indicators
            bias_categories: Specific bias categories to detect (None = all)
        """
        self.detect_bias = detect_bias
        self.bias_categories = bias_categories or list(BiasCategory.__members__.values())
        
        # Initialize Presidio components
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # Add custom recognizers
        self._setup_custom_recognizers()
        
    def _setup_custom_recognizers(self):
        """Set up all custom recognizers including bias detection"""
        
        # Add standard employee-specific recognizers
        self._add_employee_recognizers()
        
        # Add bias recognizers if enabled
        if self.detect_bias:
            self._add_bias_recognizers()
    
    def _add_employee_recognizers(self):
        """Add recognizers for employee-specific patterns"""
        
        # Employee ID recognizer
        emp_id_recognizer = PatternRecognizer(
            supported_entity="EMPLOYEE_ID",
            patterns=[
                Pattern(r'\bEMP[0-9]{5}\b', score=0.9),
                Pattern(r'\bE[0-9]{6}\b', score=0.8),
                Pattern(r'\b[A-Z]{2}-[0-9]{6}\b', score=0.8)
            ],
            context=["employee", "id", "identifier", "badge", "number"]
        )
        
        # Performance rating recognizer
        rating_recognizer = PatternRecognizer(
            supported_entity="PERFORMANCE_RATING",
            patterns=[
                Pattern(r'\b[A-E][1-5]\b', score=0.7),
                Pattern(r'\b(exceeds|meets|below)\s+expectations\b', score=0.8),
                Pattern(r'\b[1-5]\s*(star|stars)\b', score=0.7)
            ],
            context=["rating", "performance", "review", "score", "evaluation"]
        )
        
        # Salary recognizer
        salary_recognizer = PatternRecognizer(
            supported_entity="COMPENSATION",
            patterns=[
                Pattern(r'\$[0-9]{1,3},?[0-9]{3,}', score=0.9),
                Pattern(r'\b[0-9]{5,7}\s*(USD|EUR|GBP)\b', score=0.9),
                Pattern(r'\b(salary|compensation|pay):\s*[0-9]+', score=0.8)
            ],
            context=["salary", "compensation", "pay", "wage", "bonus", "earnings"]
        )
        
        # Add recognizers to analyzer
        self.analyzer.registry.add_recognizer(emp_id_recognizer)
        self.analyzer.registry.add_recognizer(rating_recognizer)
        self.analyzer.registry.add_recognizer(salary_recognizer)
    
    def _add_bias_recognizers(self):
        """Add bias word recognizers for each category"""
        
        bias_words_dict = BiasWords.get_all_categories()
        
        # Option 1: Add individual recognizers for each category (more granular)
        for category, words in bias_words_dict.items():
            if category in self.bias_categories:
                recognizer = BiasWordRecognizer(category, words)
                self.analyzer.registry.add_recognizer(recognizer)
        
        # Option 2: Add one comprehensive recognizer (better performance)
        # comprehensive_recognizer = ComprehensiveBiasRecognizer()
        # self.analyzer.registry.add_recognizer(comprehensive_recognizer)
    
    def analyze_text(self, text: str, entities: List[str] = None) -> List[RecognizerResult]:
        """
        Analyze text for PII and bias indicators
        
        Args:
            text: Text to analyze
            entities: Specific entities to detect (None = all)
            
        Returns:
            List of detected entities
        """
        if entities is None:
            entities = ["ALL"]
        
        results = self.analyzer.analyze(
            text=text,
            entities=entities,
            language="en"
        )
        
        return results
    
    def anonymize_text(self, 
                      text: str, 
                      custom_operators: Dict[str, OperatorConfig] = None) -> str:
        """
        Anonymize text by removing PII and bias indicators
        
        Args:
            text: Text to anonymize
            custom_operators: Custom anonymization operators per entity type
            
        Returns:
            Anonymized text
        """
        # Analyze text
        results = self.analyze_text(text)
        
        # Define default operators if not provided
        if custom_operators is None:
            custom_operators = self._get_default_operators()
        
        # Anonymize
        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=custom_operators
        )
        
        return anonymized.text
    
    def _get_default_operators(self) -> Dict[str, OperatorConfig]:
        """Get default anonymization operators"""
        operators = {
            # Standard PII
            "PERSON": OperatorConfig("replace", {"new_value": "[PERSON]"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "[LOCATION]"}),
            
            # Employee-specific
            "EMPLOYEE_ID": OperatorConfig("replace", {"new_value": "[ID]"}),
            "COMPENSATION": OperatorConfig("replace", {"new_value": "[SALARY]"}),
            "PERFORMANCE_RATING": OperatorConfig("keep", {}),  # Keep for matching
            
            # Default for all bias categories
            "DEFAULT": OperatorConfig("replace", {"new_value": ""})
        }
        
        # Add operators for each bias category
        for category in BiasCategory:
            entity_name = f"{category.value.upper()}_BIAS"
            operators[entity_name] = OperatorConfig("replace", {"new_value": ""})
        
        # Single operator for comprehensive bias detection
        operators["BIAS_INDICATOR"] = OperatorConfig("replace", {"new_value": ""})
        
        return operators
    
    def anonymize_json(self, 
                      json_data: Dict[str, Any],
                      fields_to_skip: List[str] = None) -> Dict[str, Any]:
        """
        Anonymize JSON data structure
        
        Args:
            json_data: JSON data to anonymize
            fields_to_skip: Field paths to skip (e.g., ["skills", "education.degree"])
            
        Returns:
            Anonymized JSON maintaining structure
        """
        fields_to_skip = fields_to_skip or []
        
        def should_skip_field(path: str) -> bool:
            """Check if field should be skipped"""
            for skip_pattern in fields_to_skip:
                if path == skip_pattern or path.startswith(skip_pattern + "."):
                    return True
            return False
        
        def anonymize_value(value: Any, path: str) -> Any:
            """Recursively anonymize values"""
            if should_skip_field(path):
                return value
            
            if isinstance(value, str):
                # Anonymize string value
                return self.anonymize_text(value)
            elif isinstance(value, dict):
                # Recursively process dictionary
                return {
                    k: anonymize_value(v, f"{path}.{k}" if path else k)
                    for k, v in value.items()
                }
            elif isinstance(value, list):
                # Process list items
                return [
                    anonymize_value(item, f"{path}[{i}]")
                    for i, item in enumerate(value)
                ]
            else:
                # Return other types as-is (numbers, booleans, None)
                return value
        
        return anonymize_value(json_data, "")
    
    def generate_bias_report(self, text: str) -> Dict[str, Any]:
        """
        Generate a report of detected bias indicators in text
        
        Args:
            text: Text to analyze
            
        Returns:
            Report with bias statistics and details
        """
        results = self.analyze_text(text)
        
        # Categorize results
        bias_categories_found = {}
        pii_found = []
        
        for result in results:
            if "_BIAS" in result.entity_type or result.entity_type == "BIAS_INDICATOR":
                category = result.entity_type.replace("_BIAS", "").lower()
                if category not in bias_categories_found:
                    bias_categories_found[category] = []
                
                detected_text = text[result.start:result.end]
                bias_categories_found[category].append({
                    "text": detected_text,
                    "position": (result.start, result.end),
                    "confidence": result.score
                })
            else:
                pii_found.append({
                    "type": result.entity_type,
                    "text": text[result.start:result.end],
                    "position": (result.start, result.end),
                    "confidence": result.score
                })
        
        return {
            "total_bias_indicators": sum(len(v) for v in bias_categories_found.values()),
            "bias_categories": bias_categories_found,
            "total_pii": len(pii_found),
            "pii_entities": pii_found,
            "bias_free": len(bias_categories_found) == 0,
            "pii_free": len(pii_found) == 0
        }


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_usage():
    """Demonstrate usage of the bias-aware anonymizer"""
    
    # Initialize anonymizer
    anonymizer = BiasAwareAnonymizer(detect_bias=True)
    
    # Sample employee profile with bias indicators
    employee_profile = {
        "id": "EMP12345",
        "personal": {
            "bio": "John is a 55-year-old senior engineer. He's married with two kids and "
                   "attends church regularly. As a Republican voter, he brings traditional "
                   "values to the workplace.",
            "contact": {
                "email": "john.smith@company.com",
                "phone": "555-123-4567"
            }
        },
        "professional": {
            "summary": "Experienced white male engineer from an affluent background. "
                      "Despite his age and recent back surgery, he remains productive.",
            "skills": ["Python", "Java", "Leadership", "Mentoring"],
            "performance": {
                "rating": "A2",
                "comments": "Strong technical skills. As a baby boomer, he sometimes "
                           "struggles with new agile methodologies."
            },
            "salary": "$145,000"
        },
        "preferences": {
            "remote_work": True,
            "relocation": False
        }
    }
    
    print("=== ORIGINAL PROFILE ===")
    print(json.dumps(employee_profile, indent=2))
    
    # Generate bias report
    print("\n=== BIAS ANALYSIS ===")
    bio_text = employee_profile["personal"]["bio"]
    summary_text = employee_profile["professional"]["summary"]
    
    bio_report = anonymizer.generate_bias_report(bio_text)
    print(f"\nBio Analysis:")
    print(f"  - Bias indicators found: {bio_report['total_bias_indicators']}")
    print(f"  - Categories: {list(bio_report['bias_categories'].keys())}")
    
    summary_report = anonymizer.generate_bias_report(summary_text)
    print(f"\nSummary Analysis:")
    print(f"  - Bias indicators found: {summary_report['total_bias_indicators']}")
    print(f"  - Categories: {list(summary_report['bias_categories'].keys())}")
    
    # Anonymize the profile
    print("\n=== ANONYMIZING PROFILE ===")
    anonymized_profile = anonymizer.anonymize_json(
        employee_profile,
        fields_to_skip=["skills", "preferences", "id"]
    )
    
    print("\n=== ANONYMIZED PROFILE ===")
    print(json.dumps(anonymized_profile, indent=2))
    
    # Test specific bias categories
    print("\n=== TESTING SPECIFIC BIAS DETECTION ===")
    test_texts = [
        "She is a young Muslim woman from a working-class background.",
        "The disabled veteran needs wheelchair access.",
        "This conservative Christian employee is expecting a baby.",
        "The candidate is a skilled Python developer with AWS experience."
    ]
    
    for text in test_texts:
        print(f"\nText: {text}")
        anonymized = anonymizer.anonymize_text(text)
        print(f"Anonymized: {anonymized}")


if __name__ == "__main__":
    example_usage()
