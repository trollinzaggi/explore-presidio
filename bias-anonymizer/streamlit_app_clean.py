"""
Streamlit App for Talent Profile Anonymization
Clean UI version using the FULL Enhanced Talent Profile Anonymizer
"""

import streamlit as st
import json
import sys
from pathlib import Path

# Add the bias-anonymizer module to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the full Enhanced Talent Profile Anonymizer
from bias_anonymizer.enhanced_talent_profile_anonymizer import EnhancedTalentProfileAnonymizer, TalentProfileConfig

# Page configuration - no sidebar
st.set_page_config(
    page_title="Talent Profile Anonymizer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for white background and clean design
st.markdown("""
    <style>
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* White background for entire app */
    .stApp {
        background-color: white;
    }
    
    /* Clean button styling */
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px;
        margin-top: 20px;
        border-radius: 5px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    
    /* Clean header with subtle gradient */
    .profile-header {
        background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
        color: #333;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        border: 1px solid #ddd;
    }
    
    /* JSON viewer with light background */
    .json-viewer {
        background-color: #f9f9f9;
        padding: 10px;
        border-radius: 5px;
        max-height: 600px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
    }
    
    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Style for expander */
    .streamlit-expanderHeader {
        background-color: #f5f5f5;
        border-radius: 5px;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: #f0f8ff;
        border: 1px solid #b3d9ff;
    }
    </style>
    """, unsafe_allow_html=True)


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
                "jobCode": "ENG_SR_001",
                "enterpriseSeniorityDate": "1995-06-15",
                "workLocation": {
                    "code": "SF_HQ_01",
                    "description": "San Francisco Headquarters - Liberal area",
                    "city": "San Francisco",
                    "state": "California",
                    "country": "United States"
                }
            },
            "workEligibility": "US Citizen, no visa required",
            "experience": {
                "experiences": [
                    {
                        "company": "Google - Known for young workforce",
                        "jobTitle": "Senior Engineering Manager for white collar workers",
                        "description": "Led diverse team including Asian and Hispanic engineers from wealthy backgrounds",
                        "startDate": "2015-03-01",
                        "endDate": "2020-12-31",
                        "id": "EXP_001"
                    }
                ]
            },
            "qualification": {
                "educations": [
                    {
                        "institutionName": "Stanford University - Elite private school for wealthy white families",
                        "degree": "MS Computer Science",
                        "areaOfStudy": "Machine Learning",
                        "completionYear": 2000,
                        "achievements": "Summa Cum Laude, from wealthy white donor family, Christian values scholarship"
                    }
                ]
            },
            "affiliation": {
                "boards": [
                    {
                        "organizationName": "Country Club - Mostly white males",
                        "position": "Board Member for wealthy Christians",
                        "boardType": "advisory"
                    }
                ],
                "awards": [
                    {
                        "name": "Best Manager Award from white male CEO",
                        "organization": "Tech Corp - Conservative company",
                        "description": "Given to white male leaders only"
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
                        "description": "Worked in team of mostly Indian and Chinese immigrants"
                    }
                ]
            },
            "qualification": {
                "educations": [
                    {
                        "institutionName": "State University - Public school for poor Hispanic students",
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


def anonymize_profile_with_config(profile_data):
    """
    Anonymize a profile using the Enhanced Talent Profile Anonymizer.
    """
    # Initialize the anonymizer
    anonymizer = EnhancedTalentProfileAnonymizer()
    
    # Custom rules to focus on specific sections
    custom_rules = {
        # Keep core section fields unchanged
        "core.rank.description": "preserve",
        "core.employeeType.description": "preserve", 
        "core.businessTitle": "preserve",
        "workEligibility": "preserve"
    }
    
    # Anonymize the profile
    anonymized = anonymizer.anonymize_talent_profile(profile_data, custom_rules)
    
    return anonymized


def main():
    """Main Streamlit app function."""
    
    # Initialize session state
    if 'profiles_data' not in st.session_state:
        st.session_state.profiles_data = {}
    if 'anonymized_profile' not in st.session_state:
        st.session_state.anonymized_profile = None
    if 'selected_profile' not in st.session_state:
        st.session_state.selected_profile = None
    
    # Header
    st.markdown("""
        <div class="profile-header">
            <h1>Talent Profile Anonymizer</h1>
            <p>Advanced bias removal using Microsoft Presidio and custom bias detection</p>
        </div>
    """, unsafe_allow_html=True)
    
    # File upload section
    st.markdown("### Upload Profile Data")
    uploaded_file = st.file_uploader(
        "Choose a JSON file containing talent profiles",
        type=['json'],
        help="Upload a JSON file with one or more talent profiles"
    )
    
    # Load profiles
    if uploaded_file is not None:
        try:
            profiles_data = json.load(uploaded_file)
            st.session_state.profiles_data = profiles_data
            st.success(f"Successfully loaded {len(profiles_data)} profiles")
        except Exception as e:
            st.error(f"Error loading file: {e}")
            profiles_data = get_sample_profiles()
    else:
        profiles_data = get_sample_profiles()
        if not st.session_state.profiles_data:
            st.session_state.profiles_data = profiles_data
        else:
            profiles_data = st.session_state.profiles_data
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main content
    if profiles_data:
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
            
            # Two columns for side-by-side display
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
                    with st.spinner("Processing..."):
                        try:
                            anonymized = anonymize_profile_with_config(st.session_state.selected_profile)
                            st.session_state.anonymized_profile = anonymized
                            st.success("Profile successfully anonymized!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
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
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 10px;'>
            <p>Powered by Enhanced Talent Profile Anonymizer</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
