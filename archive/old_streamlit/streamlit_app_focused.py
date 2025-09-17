"""
Streamlit App for Talent Profile Anonymization
Focuses on removing bias from experience, education, and qualification sections
"""

import streamlit as st
import json
import sys
import os
import re
import copy
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Talent Profile Anonymizer",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better display
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px;
        margin-top: 20px;
        border-radius: 5px;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .profile-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .json-viewer {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        max-height: 600px;
        overflow-y: auto;
    }
    </style>
    """, unsafe_allow_html=True)


# Define all bias words
BIAS_WORDS = {
    'gender': [
        "male", "female", "man", "woman", "boy", "girl", "he", "she", "him", "her", 
        "his", "hers", "husband", "wife", "son", "daughter", "mother", "father",
        "mom", "dad", "brother", "sister", "boyfriend", "girlfriend", "gentleman",
        "lady", "mr", "ms", "mrs", "masculine", "feminine", "maternal", "paternal"
    ],
    'race_ethnicity': [
        "white", "black", "african", "european", "asian", "hispanic", "latino", "latina",
        "caucasian", "african-american", "afro", "caribbean", "chinese", "japanese",
        "korean", "vietnamese", "thai", "indian", "pakistani", "filipino", "indonesian",
        "mexican", "colombian", "puerto rican", "cuban", "arab", "persian", "middle eastern",
        "lebanese", "turkish", "iranian", "iraqi", "syrian", "palestinian", "egyptian"
    ],
    'age': [
        "young", "old", "elderly", "millennial", "gen-z", "boomer", "baby boomer",
        "senior", "junior", "veteran", "experienced", "fresh", "recent graduate",
        "entry-level", "twenties", "thirties", "forties", "fifties", "sixties",
        "middle-aged", "elder", "older worker", "retirement-age", "aged", "geriatric"
    ],
    'family_status': [
        "married", "single", "divorced", "widowed", "separated", "bachelor", "bachelorette",
        "spouse", "partner", "children", "kids", "childcare", "family", "parent",
        "unmarried", "unwed", "celibate", "engaged", "coupled"
    ],
    'socioeconomic': [
        "wealthy", "rich", "poor", "working-class", "upper-class", "middle-class",
        "privileged", "elite", "disadvantaged", "low-income", "high-income",
        "blue-collar", "white-collar", "immigrant", "refugee", "first-generation",
        "trust fund", "scholarship", "public school", "private school", "ivy league",
        "elite", "prestigious", "exclusive", "donor"
    ],
    'religion': [
        "christian", "muslim", "jewish", "hindu", "buddhist", "catholic", "protestant",
        "baptist", "methodist", "presbyterian", "evangelical", "orthodox", "islamic",
        "mosque", "church", "synagogue", "temple", "atheist", "agnostic", "secular",
        "religious", "faith-based", "spiritual"
    ],
    'sexual_orientation': [
        "gay", "lesbian", "homosexual", "heterosexual", "straight", "lgbtq", "lgbt",
        "bisexual", "pansexual", "queer", "transgender", "non-binary", "cis", "cisgender"
    ],
    'political': [
        "republican", "democrat", "conservative", "liberal", "progressive", "left-wing",
        "right-wing", "socialist", "libertarian", "communist", "fascist", "activist",
        "feminist", "feminism"
    ],
    'disability': [
        "disabled", "disability", "wheelchair", "blind", "deaf", "impaired", "handicapped",
        "special needs", "able-bodied", "non-disabled", "physically fit", "healthy"
    ],
    'nationality': [
        "american", "mexican", "canadian", "british", "french", "german", "italian",
        "spanish", "russian", "chinese", "japanese", "indian", "brazilian", "australian",
        "green card", "visa", "citizen", "immigrant", "foreign", "native", "indigenous",
        "nationality", "citizenship"
    ]
}

# Flatten all bias words into a single list
ALL_BIAS_WORDS = []
for category_words in BIAS_WORDS.values():
    ALL_BIAS_WORDS.extend(category_words)


def remove_bias_from_text(text):
    """
    Remove bias words from text.
    
    Args:
        text: Input text
        
    Returns:
        Text with bias words removed
    """
    if not text or not isinstance(text, str):
        return text
    
    result = text
    
    # Remove each bias word (case-insensitive)
    for word in ALL_BIAS_WORDS:
        # Use word boundaries for accurate matching
        pattern = r'\b' + re.escape(word) + r's?\b'
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    result = re.sub(r'\s+', ' ', result).strip()
    result = re.sub(r'\s*-\s*-\s*', ' - ', result)
    result = re.sub(r'\s*,\s*,\s*', ', ', result)
    result = re.sub(r'\s*:\s*$', '', result)
    result = re.sub(r'^\s*-\s*', '', result)
    
    # Return placeholder if string became empty
    if not result and len(text) > 5:
        return "[REDACTED]"
    
    return result


def remove_pii_patterns(text):
    """
    Remove only email, phone, and social media links.
    
    Args:
        text: Input text
        
    Returns:
        Text with PII removed
    """
    if not text or not isinstance(text, str):
        return text
    
    result = text
    
    # Remove email addresses
    result = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'removed', result)
    
    # Remove phone numbers
    result = re.sub(r'(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', 'removed', result)
    
    # Remove social media links
    social_patterns = [
        r'(?:https?://)?(?:www\.)?linkedin\.com/[^\s]*',
        r'(?:https?://)?(?:www\.)?twitter\.com/[^\s]*',
        r'(?:https?://)?(?:www\.)?facebook\.com/[^\s]*',
        r'(?:https?://)?(?:www\.)?github\.com/[^\s]*',
        r'@[A-Za-z0-9_]+',  # Twitter handles
    ]
    for pattern in social_patterns:
        result = re.sub(pattern, 'removed', result, flags=re.IGNORECASE)
    
    return result


def anonymize_profile(profile_data):
    """
    Function to anonymize a profile focusing on experience, education, and qualification sections.
    
    Args:
        profile_data: The talent profile dictionary
        
    Returns:
        Anonymized profile dictionary
    """
    # Create a deep copy
    anonymized = copy.deepcopy(profile_data)
    
    # Define which sections to process for bias removal
    bias_removal_sections = ['experience', 'qualification', 'education']
    
    # Fields where we should remove organization/institution names
    org_name_fields = ['institutionName', 'company', 'organizationName', 'organization']
    
    def process_value(value, field_name="", parent_path=""):
        """Recursively process values in the profile."""
        
        # Check if we're in a section that needs bias removal
        in_bias_section = any(section in parent_path.lower() for section in bias_removal_sections)
        
        if isinstance(value, dict):
            # Process dictionary
            result = {}
            for k, v in value.items():
                new_path = f"{parent_path}.{k}" if parent_path else k
                result[k] = process_value(v, k, new_path)
            return result
            
        elif isinstance(value, list):
            # Process list
            return [process_value(item, field_name, parent_path) for item in value]
            
        elif isinstance(value, str):
            # Process string
            
            # First, always remove email, phone, and social media
            value = remove_pii_patterns(value)
            
            # Remove organization/institution names if in those fields
            if field_name in org_name_fields:
                # Remove bias words and then replace with "removed"
                cleaned = remove_bias_from_text(value)
                if cleaned != value:  # If bias was found and removed
                    return "removed"
                # If no bias, keep original but still check for names
                if any(name in value.lower() for name in ['university', 'college', 'institute', 'school', 'company', 'corp', 'inc', 'ltd']):
                    return "removed"
            
            # If we're in experience/qualification/education section, remove bias
            if in_bias_section:
                value = remove_bias_from_text(value)
            
            return value
            
        else:
            # Return other types as-is (numbers, booleans, None, dates)
            return value
    
    # Process the entire profile
    anonymized = process_value(anonymized)
    
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
                "jobCode": "ENG_SR_001",
                "enterpriseSeniorityDate": "1995-06-15",
                "gcrs": {
                    "businessDivisionCode": "TECH",
                    "businessDivisionDescription": "Technology Division - Predominantly white males",
                    "businessUnitCode": "CLOUD",
                    "businessUnitDescription": "Cloud Computing Unit"
                },
                "workLocation": {
                    "code": "SF_HQ_01",
                    "description": "San Francisco Headquarters - Liberal area",
                    "city": "San Francisco",
                    "state": "California",
                    "country": "United States"
                }
            },
            "workEligibility": "US Citizen, no visa required",
            "language": {
                "languages": ["English - Native", "Spanish - Basic"],
                "createdBy": "Admin John",
                "lastModifiedBy": "Manager Sarah Williams"
            },
            "experience": {
                "experiences": [
                    {
                        "company": "Google - Known for young workforce",
                        "jobTitle": "Senior Engineering Manager for white collar workers",
                        "description": "Led diverse team including Asian and Hispanic engineers from wealthy backgrounds",
                        "startDate": "2015-03-01",
                        "endDate": "2020-12-31",
                        "id": "EXP_001",
                        "managerEmail": "john.manager@google.com"
                    }
                ],
                "crossDivisionalExperience": "Yes",
                "internationalExperience": "Yes",
                "timeInCurrentRoleInDays": "1095"
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
                ],
                "certifications": ["AWS Solutions Architect", "Google Cloud Professional"]
            },
            "affiliation": {
                "boards": [
                    {
                        "organizationName": "Country Club - Mostly white males",
                        "position": "Board Member",
                        "boardType": "advisory"
                    }
                ],
                "awards": [
                    {
                        "name": "Best Manager Award from CEO John Anderson",
                        "organization": "Tech Corp",
                        "date": "2023-05-15"
                    }
                ]
            },
            "careerAspirationPreference": "Looking to lead C-suite with other white executives",
            "careerLocationPreference": "Prefer conservative Republican states",
            "careerRolePreference": "Looking for young, energetic team without family obligations",
            "personalEmail": "johnsmith@gmail.com",
            "personalPhone": "650-555-9876",
            "version": "1.0",
            "completionScore": "95"
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
                    "description": "Full Time - Needs childcare flexibility for disabled child"
                },
                "businessTitle": "Engineer from working-class immigrant family",
                "jobCode": "ENG_MID_002",
                "workLocation": {
                    "code": "NY_01",
                    "city": "New York",
                    "state": "New York"
                }
            },
            "workEligibility": "Green Card holder from Mexico, married to US citizen",
            "experience": {
                "experiences": [
                    {
                        "company": "Microsoft - diverse immigrant workforce",
                        "jobTitle": "Software Developer",
                        "description": "Worked in team of mostly Indian and Chinese immigrants, reported to Muslim manager",
                        "startDate": "2018-01-01",
                        "contactEmail": "hr@microsoft.com"
                    }
                ]
            },
            "qualification": {
                "educations": [
                    {
                        "institutionName": "State University - Public school for poor Hispanic students",
                        "degree": "BS Computer Science",
                        "areaOfStudy": "Software Engineering",
                        "completionYear": 2015,
                        "achievements": "First generation college student, immigrant scholarship recipient"
                    }
                ]
            },
            "affiliation": {
                "memberships": [
                    {
                        "organizationName": "Women in Tech - Feminist organization for lesbians",
                        "role": "Active Member",
                        "since": "2018"
                    }
                ],
                "awards": [
                    {
                        "name": "Diversity Champion Award from Sarah Johnson",
                        "organization": "LGBTQ Tech Alliance",
                        "description": "For supporting gay and lesbian colleagues"
                    }
                ]
            },
            "careerPreference": "Seeking inclusive environment, flexible for elderly parent care",
            "createdBy": "HR Manager Bob Smith",
            "lastModifiedBy": "Director Jane Williams"
        },
        "Profile_003_David_Chen": {
            "userId": "USER_11111",
            "core": {
                "rank": {
                    "code": "L6",
                    "description": "Senior Engineer - Asian male, Buddhist, gay married to partner",
                    "id": "RANK_006"
                },
                "businessTitle": "Engineer - Gay partnered, no children due to homosexuality",
                "jobCode": "ENG_SR_003",
                "workLocation": {
                    "code": "SEA_01",
                    "city": "Seattle",
                    "state": "Washington"
                }
            },
            "workEligibility": "H1-B Visa from China, seeking green card through gay marriage",
            "experience": {
                "experiences": [
                    {
                        "company": "Amazon Web Services",
                        "jobTitle": "Senior Software Engineer",
                        "description": "Worked with predominantly Indian and Chinese team of H1-B visa holders",
                        "startDate": "2018-01-15",
                        "managerPhone": "206-555-4321"
                    }
                ]
            },
            "qualification": {
                "educations": [
                    {
                        "institutionName": "Beijing University - Chinese communist party affiliated school",
                        "degree": "BS Computer Science",
                        "areaOfStudy": "Software Engineering",
                        "completionYear": 2012,
                        "achievements": "Communist party scholarship, gay student union president"
                    }
                ]
            },
            "careerPreference": "Prefer LGBTQ-friendly, liberal Democrat environment",
            "socialMedia": {
                "linkedin": "linkedin.com/in/davidchen",
                "twitter": "@davidchen_tech"
            }
        }
    }


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
            <h1>🔒 Talent Profile Anonymizer</h1>
            <p>Remove bias from Experience, Education & Qualification sections</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for settings and file upload
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # File upload option
        uploaded_file = st.file_uploader(
            "Upload JSON file with profiles",
            type=['json'],
            help="Upload a JSON file containing talent profiles"
        )
        
        # Load profiles
        if uploaded_file is not None:
            try:
                profiles_data = json.load(uploaded_file)
                st.session_state.profiles_data = profiles_data
                st.success(f"✅ Loaded {len(profiles_data)} profiles")
            except Exception as e:
                st.error(f"Error loading file: {e}")
                profiles_data = get_sample_profiles()
        else:
            # Use sample profiles if no file uploaded
            profiles_data = get_sample_profiles()
            if not st.session_state.profiles_data:
                st.session_state.profiles_data = profiles_data
            else:
                profiles_data = st.session_state.profiles_data
        
        st.divider()
        
        # Display what will be anonymized
        st.subheader("🎯 Anonymization Focus")
        st.info("""
        **Sections Processed:**
        - Experience
        - Education
        - Qualification
        
        **What Gets Removed:**
        - All bias words
        - Email addresses
        - Phone numbers
        - Social media links
        - Organization/Institution names
        
        **What Stays:**
        - User IDs
        - Dates
        - Created/Modified by
        - Other sections unchanged
        """)
        
        st.divider()
        
        # Display statistics
        st.subheader("📊 Statistics")
        st.metric("Total Profiles", len(profiles_data))
        
        if st.session_state.anonymized_profile:
            st.success("✅ Profile Anonymized")
    
    # Main content area
    if profiles_data:
        # Profile selector dropdown
        selected_entry = st.selectbox(
            "📋 Select a Profile to Anonymize:",
            list(profiles_data.keys()),
            index=0,
            help="Choose a talent profile from the dropdown"
        )
        
        # Store the selected profile
        if selected_entry:
            st.session_state.selected_profile = profiles_data[selected_entry]
            
            # Create two columns for side-by-side display
            col_left, col_right = st.columns(2)
            
            # Left column - Original Profile
            with col_left:
                st.subheader("📄 Original Profile")
                with st.container():
                    st.json(st.session_state.selected_profile)
            
            # Right column - Anonymized Profile
            with col_right:
                st.subheader("🔐 Anonymized Profile")
                if st.session_state.anonymized_profile:
                    with st.container():
                        st.json(st.session_state.anonymized_profile)
                else:
                    st.info("Click 'Anonymize Profile' button below to see the anonymized version")
            
            # Anonymize button - centered at the bottom
            st.divider()
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔒 Anonymize Profile", type="primary", use_container_width=True):
                    with st.spinner("Removing bias from Experience, Education & Qualification sections..."):
                        # Call the anonymize function with the selected profile
                        anonymized = anonymize_profile(st.session_state.selected_profile)
                        
                        # Store the result
                        st.session_state.anonymized_profile = anonymized
                        
                        # Show success message
                        st.success("✅ Profile successfully anonymized!")
                        st.balloons()
                        
                        # Rerun to update the display
                        st.rerun()
            
            # Additional action buttons
            st.divider()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Reset", use_container_width=True):
                    st.session_state.anonymized_profile = None
                    st.rerun()
            
            with col2:
                if st.session_state.anonymized_profile:
                    # Download button for anonymized profile
                    anonymized_json = json.dumps(st.session_state.anonymized_profile, indent=2)
                    st.download_button(
                        label="📥 Download Anonymized Profile",
                        data=anonymized_json,
                        file_name=f"anonymized_{selected_entry}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            
            with col3:
                if st.session_state.selected_profile and st.session_state.anonymized_profile:
                    # Show comparison details
                    if st.button("📊 Show Changes", use_container_width=True):
                        with st.expander("What Changed", expanded=True):
                            st.write("**✅ Changes in Experience Section:**")
                            st.write("- Removed bias words from job titles and descriptions")
                            st.write("- Removed company names → 'removed'")
                            st.write("- Removed email/phone contacts")
                            st.write("")
                            st.write("**✅ Changes in Education/Qualification:**")
                            st.write("- Removed institution names → 'removed'")
                            st.write("- Removed bias from achievements")
                            st.write("- Kept degrees and completion years")
                            st.write("")
                            st.write("**❌ Unchanged Sections:**")
                            st.write("- Core (rank, employee type, business title)")
                            st.write("- Work eligibility")
                            st.write("- Affiliations")
                            st.write("- Career preferences")
                            st.write("- User IDs and dates")
                            st.write("- CreatedBy/ModifiedBy fields")
    else:
        st.warning("No profiles available. Please upload a JSON file with talent profiles.")
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #888; padding: 20px;'>
            <p>Focused Anonymization: Experience, Education & Qualification Only</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
