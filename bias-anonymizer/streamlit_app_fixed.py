"""
Streamlit App for Talent Profile Anonymizer
Fixed version - no file uploader, with proper error handling
"""

import streamlit as st
import json
import sys
from pathlib import Path
import copy
import re

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Try to import the enhanced anonymizer, fall back to basic if needed
try:
    from bias_anonymizer.enhanced_talent_profile_anonymizer import EnhancedTalentProfileAnonymizer
    ENHANCED_AVAILABLE = True
except ImportError as e:
    ENHANCED_AVAILABLE = False
    st.warning(f"Enhanced anonymizer not available, using basic version. Error: {e}")

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


def anonymize_profile(profile_data):
    """Anonymize profile using enhanced or basic method."""
    anonymized = copy.deepcopy(profile_data)
    
    if ENHANCED_AVAILABLE:
        try:
            anonymizer = EnhancedTalentProfileAnonymizer()
            return anonymizer.anonymize_talent_profile(profile_data)
        except Exception as e:
            st.error(f"Error using enhanced anonymizer: {e}")
            st.info("Falling back to basic anonymization")
    
    # Basic anonymization for specific sections
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
        
        # Two columns
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
                        # Anonymize the profile
                        anonymized = anonymize_profile(st.session_state.selected_profile)
                        st.session_state.anonymized_profile = anonymized
                        st.success("Profile successfully anonymized!")
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
