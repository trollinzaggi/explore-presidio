"""
Comprehensive bias words definitions with all categories.
Exact word list as specified by the user.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class BiasWords:
    """Container for all bias-related words organized by category."""
    
    # Gender-related words
    male_words = [
        "he", "him", "his", "man", "male", "boy", "father", "son", "brother",
        "husband", "boyfriend", "gentleman", "guy", "mr", "masculine", "paternal", "dad", "father"
    ]
    
    female_words = [
        "she", "her", "hers", "woman", "female", "girl", "mother", "daughter",
        "sister", "wife", "girlfriend", "lady", "ms", "mrs", "feminine", "maternal", "mom", "mother"
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
        """Get all bias categories and their associated words as per ALL_BIAS_CATEGORIES."""
        return {
            'gender': cls.male_words + cls.female_words + cls.gender_neutral_words,
            'race_ethnicity': (cls.european_words + cls.african_words + cls.asian_words +
                              cls.hispanic_words + cls.middle_eastern_words),
            'age': cls.young_age_words + cls.middle_age_words + cls.older_age_words,
            'disability': cls.disabled_words + cls.able_bodied_words,
            'marital_status': cls.single_status_words + cls.married_status_words + cls.parent_status_words,
            'nationality': cls.domestic_nationality_words + cls.foreign_nationality_words,
            'sexual_orientation': cls.heterosexual_words + cls.lgbtq_words,
            'religion': (cls.christian_words + cls.muslim_words + cls.jewish_words +
                        cls.eastern_religion_words + cls.secular_words),
            'political_affiliation': cls.conservative_words + cls.liberal_words,
            'socioeconomic_background': cls.wealthy_words + cls.working_class_words,
            'pregnancy_maternity': cls.pregnancy_maternity_words,
            'union_membership': cls.union_words + cls.non_union_words,
            'health_condition': cls.health_condition_words,
            'criminal_background': cls.criminal_background_words + cls.clean_background_words
        }
    
    @classmethod
    def get_category_words(cls, category: str) -> List[str]:
        """Get words for a specific category."""
        all_categories = cls.get_all_categories()
        return all_categories.get(category, [])
    
    @classmethod
    def get_word_to_category_mapping(cls) -> Dict[str, str]:
        """Create a reverse mapping from word to its category."""
        word_to_category = {}
        for category, words in cls.get_all_categories().items():
            for word in words:
                word_lower = word.lower()
                # Store the category for this word (keeps last occurrence if duplicate)
                word_to_category[word_lower] = category
        return word_to_category
    
    @classmethod
    def identify_bias_category(cls, word: str) -> str:
        """Identify which bias category a word belongs to."""
        mapping = cls.get_word_to_category_mapping()
        return mapping.get(word.lower(), "unknown")
    
    @classmethod
    def get_all_bias_words(cls) -> List[str]:
        """Get all bias words across all categories (unique)."""
        all_words = []
        for words_list in cls.get_all_categories().values():
            all_words.extend(words_list)
        # Return with duplicates included as they appear in the lists
        return all_words
    
    @classmethod
    def get_statistics(cls) -> Dict[str, int]:
        """Get statistics about the bias word database."""
        stats = {}
        categories = cls.get_all_categories()
        
        stats['total_categories'] = len(categories)
        # Count unique words across all categories
        unique_words = set()
        for words_list in categories.values():
            unique_words.update([w.lower() for w in words_list])
        stats['total_unique_words'] = len(unique_words)
        
        for category, words in categories.items():
            stats[f'{category}_count'] = len(words)
        
        return stats
