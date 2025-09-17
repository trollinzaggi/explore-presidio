"""
Streamlit App for Talent Profile Anonymizer
Updated to use YAML configuration
"""

import streamlit as st
import json
import sys
from pathlib import Path
import copy
import re

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Try to import the anonymizer wrapper
try:
    from bias_anonymizer.anonymizer_wrapper import BiasAnonymizer
    from bias_anonymizer.config_loader import create_anonymizer_from_config, create_custom_config_yaml
    ANONYMIZER_AVAILABLE = True
except ImportError as e:
    ANONYMIZER_AVAILABLE = False
    st.warning(f"Anonymizer not available, using basic version. Error: {e}")

# Page configuration
st.set_page_config(
    page_title="Talent Profile Anonymizer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for clean white design
st.markdown("""
    <style>
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* White background */
    .stApp {
        background-color: white;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px;
        margin-top: 20px;
        border-radius: 5px;
    }
    
    /* Header */
    .profile-header {
        background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
        color: #333;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        border: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)


# Define bias words for basic anonymization
BIAS_WORDS = [
    # Gender
    "male", "female", "man", "woman", "boy", "girl", "he", "she", "him", "her",
    "his", "hers", "husband", "wife", "son", "daughter", "mother", "father",
    # Race/Ethnicity
    "white", "black", "african", "european", "asian", "hispanic", "latino", "latina",
    "caucasian", "chinese", "japanese", "korean", "indian", "mexican",
    # Age
    "young", "old", "elderly", "millennial", "boomer", "senior", "junior",
    # Family
    "married", "single", "divorced", "children", "childcare", "family",
    # Socioeconomic
    "wealthy", "rich", "poor", "working-class", "upper-class", "elite", "immigrant",
    # Religion
    "christian", "muslim", "jewish", "hindu", "buddhist", "catholic",
    # Sexual orientation
    "gay", "lesbian", "lgbtq", "heterosexual", "straight",
    # Political
    "republican", "democrat", "conservative", "liberal", "feminist",
    # Disability
    "disabled", "disability", "wheelchair", "blind", "deaf",
    # Nationality
    "citizen", "visa", "green card", "foreign", "native"
]


def basic_anonymize(text):
    """Basic anonymization function as fallback."""
    if not text or not isinstance(text, str):
        return text
    
    result = text
    for word in BIAS_WORDS:
        pattern = r'\b' + re.escape(word) + r's?\b'
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    
    # Clean up spaces
    result = re.sub(r'\s+', ' ', result).strip()
    return result if result else "[REDACTED]"


def create_temp_config(strategy="redact"):
    """Create a temporary YAML config file for the selected strategy."""
    import yaml
    import tempfile
    
    # Load default config as base
    try:
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except:
        # If default config not found, create minimal config
        config = {
            'anonymization_strategy': strategy,
            'detect_bias': True,
            'detect_pii': True,
            'confidence_threshold': 0.7,
            'preserve_fields': [
                'core.jobCode',
                'core.rank.code',
                'userId'
            ],
            'always_anonymize_fields': [
                'core.businessTitle',
                'core.rank.description',
                'core.employeeType.description',
                'experience.experiences[*].description',
                'experience.experiences[*].company',
                'qualification.educations[*].institutionName',
                'qualification.educations[*].achievements',
                'affiliation.boards[*].organizationName',
                'affiliation.boards[*].position',
                'affiliation.awards[*].name',
                'affiliation.awards[*].organization',
                'affiliation.memberships[*].organizationName',
                'affiliation.memberships[*].role',
                'workEligibility'
            ]
        }
    
    # Update strategy
    config['anonymization_strategy'] = strategy
    
    # Update operators based on strategy
    if strategy == "redact":
        config['operators'] = {
            'GENDER_BIAS': 'redact',
            'RACE_BIAS': 'redact',
            'AGE_BIAS': 'redact',
            'SOCIOECONOMIC_BIAS': 'redact',
            'DISABILITY_BIAS': 'redact',
            'RELIGION_BIAS': 'redact',
            'NATIONALITY_BIAS': 'redact',
            'MARITAL_STATUS_BIAS': 'redact',
            'DEFAULT': 'redact'
        }
    elif strategy == "replace":
        config['operators'] = {
            'GENDER_BIAS': 'replace',
            'RACE_BIAS': 'replace',
            'AGE_BIAS': 'replace',
            'SOCIOECONOMIC_BIAS': 'replace',
            'DISABILITY_BIAS': 'replace',
            'RELIGION_BIAS': 'replace',
            'NATIONALITY_BIAS': 'replace',
            'MARITAL_STATUS_BIAS': 'replace',
            'DEFAULT': 'replace'
        }
        config['replacement_tokens'] = {
            'GENDER_BIAS': '[GENDER]',
            'RACE_BIAS': '[RACE]',
            'AGE_BIAS': '[AGE]',
            'SOCIOECONOMIC_BIAS': '[BACKGROUND]',
            'DISABILITY_BIAS': '[DISABILITY]',
            'RELIGION_BIAS': '[RELIGION]',
            'NATIONALITY_BIAS': '[NATIONALITY]',
            'MARITAL_STATUS_BIAS': '[MARITAL_STATUS]',
            'DEFAULT': '[REDACTED]'
        }
    
    # Create temp file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    yaml.dump(config, temp_file)
    temp_file.close()
    
    return temp_file.name


def anonymize_profile(profile_data, strategy="redact", use_yaml_config=True):
    """
    Anonymize profile using TalentProfileAnonymizer.
    
    Args:
        profile_data: The profile data to anonymize
        strategy: The strategy to use (redact or replace)
        use_yaml_config: If True, uses YAML configuration (Mode 1/2)
                        If False, uses programmatic strategy (Mode 3)
    """
    anonymized = copy.deepcopy(profile_data)
    
    if ANONYMIZER_AVAILABLE:
        try:
            if use_yaml_config:
                # MODE 1/2: Use YAML configuration
                # Try to use default config first
                try:
                    anonymizer = BiasAnonymizer()  # Mode 1: Uses default_config.yaml
                    # If strategy differs from default, create temp config
                    if strategy != "redact":  # Assuming default is redact
                        temp_config = create_temp_config(strategy)
                        anonymizer = BiasAnonymizer(config_path=temp_config)  # Mode 2
                except:
                    # If default config not available, create temp config
                    temp_config = create_temp_config(strategy)
                    anonymizer = BiasAnonymizer(config_path=temp_config)  # Mode 2
            else:
                # MODE 3: Programmatic (minimal config)
                anonymizer = BiasAnonymizer(strategy=strategy)
            
            return anonymizer.anonymize(profile_data)
            
        except Exception as e:
            st.error(f"Error using anonymizer: {e}")
            st.info("Falling back to basic anonymization")
    
    # Basic anonymization fallback
    sections_to_process = ['experience', 'qualification', 'affiliation', 'education']
    
    def process_value(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                if any(section in new_path.lower() for section in sections_to_process):
                    if isinstance(value, str):
                        obj[key] = basic_anonymize(value)
                    elif isinstance(value, (dict, list)):
                        process_value(value, new_path)
                elif isinstance(value, (dict, list)):
                    process_value(value, new_path)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    process_value(item, path)
                    
    process_value(anonymized)
    return anonymized


def get_sample_profiles():
    """Get sample profiles for demonstration."""
    return {
        "Profile_001_John_Smith": {
            "userId": "USER_12345",
            "externalSourceType": "LinkedIn",
            "core": {
                "rank": {
                    "code": "L7",
                    "description": "Senior Principal Engineer - White male, 45 years old",
                    "id": "RANK_007"
                },
                "employeeType": {
                    "code": "FTE",
                    "description": "Full Time Employee - Married with children"
                },
                "businessTitle": "Senior Engineer from wealthy background",
                "jobCode": "ENG_SR_001"
            },
            "workEligibility": "US Citizen, no visa required",
            "experience": {
                "experiences": [
                    {
                        "company": "Google - Known for young workforce",
                        "jobTitle": "Senior Engineering Manager for white collar workers",
                        "description": "Led team including Asian and Hispanic engineers",
                        "startDate": "2015-03-01",
                        "endDate": "2020-12-31"
                    }
                ]
            },
            "qualification": {
                "educations": [
                    {
                        "institutionName": "Stanford University - Elite private school for wealthy families",
                        "degree": "MS Computer Science",
                        "areaOfStudy": "Machine Learning",
                        "completionYear": 2000,
                        "achievements": "Summa Cum Laude, from wealthy white donor family"
                    }
                ]
            },
            "affiliation": {
                "boards": [
                    {
                        "organizationName": "Country Club - Mostly white males",
                        "position": "Board Member for wealthy Christians"
                    }
                ],
                "awards": [
                    {
                        "name": "Best Manager Award from white male CEO",
                        "organization": "Tech Corp - Conservative company"
                    }
                ]
            }
        },
        "Profile_002_Maria_Garcia": {
            "userId": "USER_67890",
            "externalSourceType": "Internal",
            "core": {
                "rank": {
                    "code": "L5",
                    "description": "Software Engineer - Hispanic female, single mother",
                    "id": "RANK_005"
                },
                "employeeType": {
                    "code": "FTE",
                    "description": "Full Time - Needs childcare flexibility"
                },
                "businessTitle": "Engineer from working-class immigrant family",
                "jobCode": "ENG_MID_002"
            },
            "workEligibility": "Green Card holder from Mexico",
            "experience": {
                "experiences": [
                    {
                        "company": "Microsoft - diverse immigrant workforce",
                        "jobTitle": "Software Developer",
                        "description": "Worked in team of Indian and Chinese immigrants"
                    }
                ]
            },
            "qualification": {
                "educations": [
                    {
                        "institutionName": "State University - Public school for poor students",
                        "degree": "BS Computer Science",
                        "areaOfStudy": "Software Engineering",
                        "completionYear": 2015
                    }
                ]
            },
            "affiliation": {
                "memberships": [
                    {
                        "organizationName": "Women in Tech - Feminist organization",
                        "role": "Active Member for single mothers"
                    }
                ]
            }
        }
    }


def main():
    """Main Streamlit app."""
    
    # Initialize session state
    if 'anonymized_profile' not in st.session_state:
        st.session_state.anonymized_profile = None
    if 'selected_profile' not in st.session_state:
        st.session_state.selected_profile = None
    
    # Header
    st.markdown("""
        <div class="profile-header">
            <h1>Talent Profile Anonymizer</h1>
            <p>Remove bias from Experience, Education, Qualification & Affiliation sections</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get sample profiles
    profiles_data = get_sample_profiles()
    
    # Profile selector
    st.markdown("### Select Profile")
    selected_entry = st.selectbox(
        "Choose a profile to anonymize:",
        list(profiles_data.keys()),
        index=0
    )
    
    if selected_entry:
        st.session_state.selected_profile = profiles_data[selected_entry]
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Add strategy selector and configuration mode
        st.markdown("### Anonymization Settings")
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            strategy = st.selectbox(
                "Strategy:",
                ["redact", "replace"],
                help="Redact: Removes bias words completely | Replace: Replaces with tokens like [GENDER]"
            )
        with col2:
            config_mode = st.selectbox(
                "Configuration Mode:",
                ["YAML Config (Full)", "Programmatic (Minimal)"],
                help="YAML: Uses field lists from config | Programmatic: Only uses strategy"
            )
        
        use_yaml = config_mode == "YAML Config (Full)"
        
        # Show configuration info
        with st.expander("Configuration Details"):
            if use_yaml:
                st.info("""
                **YAML Configuration Mode (Recommended)**
                - Uses field lists from default_config.yaml
                - Knows which fields to preserve (jobCode, rank.code, etc.)
                - Knows which fields to anonymize (businessTitle, descriptions, etc.)
                - Applies special handling (hash userId, year-only for dates)
                """)
            else:
                st.warning("""
                **Programmatic Mode (Minimal)**
                - Only applies the strategy
                - No field-specific configuration
                - May not handle all fields correctly
                - Good for testing but not production
                """)
        
        # Two columns for before/after
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### Original Profile")
            st.json(st.session_state.selected_profile)
        
        with col_right:
            st.markdown("### Anonymized Profile")
            if st.session_state.anonymized_profile:
                st.json(st.session_state.anonymized_profile)
            else:
                st.info("Click 'Anonymize Profile' button below")
        
        # Anonymize button
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Anonymize Profile", type="primary", use_container_width=True):
                try:
                    with st.spinner("Processing..."):
                        # Anonymize the profile with selected strategy and mode
                        anonymized = anonymize_profile(
                            st.session_state.selected_profile, 
                            strategy=strategy,
                            use_yaml_config=use_yaml
                        )
                        st.session_state.anonymized_profile = anonymized
                        
                        mode_text = "YAML configuration" if use_yaml else "programmatic mode"
                        st.success(f"Profile anonymized using '{strategy}' strategy with {mode_text}!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error during anonymization: {str(e)}")
                    st.exception(e)  # This will show the full traceback
        
        # Action buttons
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Reset", use_container_width=True):
                st.session_state.anonymized_profile = None
                st.rerun()
        
        with col2:
            if st.session_state.anonymized_profile:
                anonymized_json = json.dumps(st.session_state.anonymized_profile, indent=2)
                st.download_button(
                    label="Download Anonymized",
                    data=anonymized_json,
                    file_name=f"anonymized_{selected_entry}.json",
                    mime="application/json",
                    use_container_width=True
                )


if __name__ == "__main__":
    main()
