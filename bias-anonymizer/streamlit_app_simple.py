"""
Simplified Streamlit App for Talent Profile Anonymization
This version can run standalone without complex imports
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import re

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
    </style>
    """, unsafe_allow_html=True)


class SimpleAnonymizer:
    """Simple anonymizer for demonstration (without Presidio dependencies)."""
    
    def __init__(self):
        """Initialize with bias terms."""
        self.bias_terms = {
            "gender": ["male", "female", "man", "woman", "boy", "girl", "he", "she", 
                      "his", "her", "husband", "wife", "son", "daughter", "mother", "father"],
            "race": ["white", "black", "asian", "hispanic", "african", "european", 
                    "chinese", "indian", "latino", "caucasian"],
            "age": ["young", "old", "elderly", "millennial", "boomer", "gen-z", 
                   "senior", "junior", "veteran", "experienced"],
            "religion": ["christian", "muslim", "jewish", "hindu", "buddhist", 
                        "catholic", "protestant", "atheist", "church", "mosque"],
            "status": ["married", "single", "divorced", "widowed", "partnered",
                      "wealthy", "poor", "rich", "privileged", "working-class"],
            "orientation": ["gay", "lesbian", "straight", "heterosexual", "homosexual",
                          "bisexual", "lgbtq", "queer"],
            "disability": ["disabled", "wheelchair", "blind", "deaf", "handicapped",
                         "impaired", "disability"],
            "political": ["republican", "democrat", "conservative", "liberal", 
                         "left-wing", "right-wing"]
        }
        
        self.pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "date": r'\b\d{4}-\d{2}-\d{2}\b'
        }
    
    def anonymize_profile(self, profile: Dict) -> Dict:
        """
        Anonymize a profile by removing bias terms and PII.
        
        Args:
            profile: Profile dictionary
            
        Returns:
            Anonymized profile
        """
        import copy
        anonymized = copy.deepcopy(profile)
        self._process_dict(anonymized)
        return anonymized
    
    def _process_dict(self, data: Any, parent_key: str = ""):
        """Recursively process dictionary."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_key = f"{parent_key}.{key}" if parent_key else key
                
                # Skip certain fields
                if key.lower() in ["code", "id", "type", "category", "status", "degree", 
                                  "certifications", "areaOfStudy", "score", "level"]:
                    continue
                
                if isinstance(value, str):
                    # Anonymize string values
                    data[key] = self._anonymize_string(value, current_key)
                elif isinstance(value, (dict, list)):
                    self._process_dict(value, current_key)
                    
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._process_dict(item, parent_key)
                elif isinstance(item, str):
                    # Note: Can't modify list items in place easily
                    pass
    
    def _anonymize_string(self, text: str, field_name: str) -> str:
        """Anonymize a string value."""
        if not text:
            return text
        
        # Special handling for certain fields
        if "date" in field_name.lower() or "year" in field_name.lower():
            # Extract year only
            year_match = re.search(r'\b(19|20)\d{2}\b', text)
            if year_match:
                return year_match.group()
        
        if field_name.lower().endswith("by"):
            return "[REDACTED]"
        
        if "userid" in field_name.lower() or "user_id" in field_name.lower():
            # Hash user IDs
            return f"HASH_{hashlib.md5(text.encode()).hexdigest()[:8]}"
        
        # Remove bias terms
        result = text
        for category, terms in self.bias_terms.items():
            for term in terms:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                result = pattern.sub("", result)
        
        # Remove PII patterns
        for pii_type, pattern in self.pii_patterns.items():
            result = re.sub(pattern, f"[{pii_type.upper()}]", result)
        
        # Clean up multiple spaces
        result = re.sub(r'\s+', ' ', result).strip()
        
        # If string became too short, return a placeholder
        if len(result) < 3 and len(text) > 10:
            if "description" in field_name.lower():
                return "[DESCRIPTION]"
            elif "title" in field_name.lower():
                return "[TITLE]"
            elif "name" in field_name.lower():
                return "[NAME]"
            else:
                return "[REDACTED]"
        
        return result


def get_sample_profiles() -> Dict[str, Any]:
    """Get sample talent profiles for demonstration."""
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
            "language": {
                "languages": ["English - Native", "Spanish - Basic"],
                "createdBy": "Admin John",
                "lastModifiedBy": "Manager Sarah"
            },
            "experience": {
                "experiences": [
                    {
                        "company": "Google - Known for young workforce",
                        "jobTitle": "Senior Engineering Manager",
                        "description": "Led diverse team including Asian and Hispanic engineers",
                        "startDate": "2015-03-01",
                        "endDate": "2020-12-31",
                        "id": "EXP_001"
                    }
                ],
                "crossDivisionalExperience": "Yes",
                "internationalExperience": "Yes"
            },
            "qualification": {
                "educations": [
                    {
                        "institutionName": "Stanford University - Elite private school",
                        "degree": "MS Computer Science",
                        "areaOfStudy": "Machine Learning",
                        "completionYear": 2000,
                        "achievements": "Summa Cum Laude, from wealthy donor family"
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
                        "name": "Best Manager Award",
                        "organization": "Tech Corp",
                        "date": "2023-05-15"
                    }
                ]
            },
            "careerPreference": "Looking for young, energetic team without family obligations"
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
                "jobCode": "ENG_MID_002",
                "workLocation": {
                    "code": "NY_01",
                    "city": "New York",
                    "state": "New York"
                }
            },
            "workEligibility": "Green Card holder from Mexico",
            "affiliation": {
                "memberships": [
                    {
                        "organizationName": "Women in Tech - Feminist organization",
                        "role": "Active Member",
                        "since": "2018"
                    }
                ],
                "awards": [
                    {
                        "name": "Diversity Champion Award",
                        "organization": "LGBTQ Tech Alliance",
                        "description": "For supporting gay and lesbian colleagues"
                    }
                ]
            },
            "qualification": {
                "educations": [
                    {
                        "institutionName": "State University - Public school",
                        "degree": "BS Computer Science",
                        "areaOfStudy": "Software Engineering",
                        "completionYear": 2015
                    }
                ]
            },
            "careerPreference": "Seeking inclusive environment, flexible for elderly parent care"
        },
        "Profile_003_David_Chen": {
            "userId": "USER_11111",
            "core": {
                "rank": {
                    "code": "L6",
                    "description": "Senior Engineer - Asian male, Buddhist, gay",
                    "id": "RANK_006"
                },
                "businessTitle": "Engineer - Partnered, no children",
                "jobCode": "ENG_SR_003",
                "workLocation": {
                    "code": "SEA_01",
                    "city": "Seattle",
                    "state": "Washington"
                }
            },
            "workEligibility": "H1-B Visa from China",
            "experience": {
                "experiences": [
                    {
                        "company": "Microsoft",
                        "jobTitle": "Software Engineer",
                        "description": "Worked with predominantly Indian and Chinese team",
                        "startDate": "2018-01-15"
                    }
                ]
            },
            "careerPreference": "Prefer LGBTQ-friendly, liberal environment"
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
    
    # Initialize anonymizer
    anonymizer = SimpleAnonymizer()
    
    # Header
    st.markdown("""
        <div class="profile-header">
            <h1>🔒 Talent Profile Anonymizer</h1>
            <p>Remove bias and PII from employee profiles for fair candidate matching</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # File upload
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
            profiles_data = get_sample_profiles()
            if not st.session_state.profiles_data:
                st.session_state.profiles_data = profiles_data
            else:
                profiles_data = st.session_state.profiles_data
        
        st.divider()
        st.metric("Total Profiles", len(profiles_data))
        
        if st.session_state.anonymized_profile:
            st.success("✅ Profile Anonymized")
    
    # Main content
    if profiles_data:
        # Profile selector
        selected_entry = st.selectbox(
            "📋 Select a Profile to Anonymize:",
            list(profiles_data.keys()),
            index=0,
            help="Choose a talent profile from the dropdown"
        )
        
        if selected_entry:
            st.session_state.selected_profile = profiles_data[selected_entry]
            
            # Two columns for side-by-side display
            col_left, col_right = st.columns(2)
            
            # Left column - Original Profile
            with col_left:
                st.subheader("📄 Original Profile")
                st.json(st.session_state.selected_profile)
            
            # Right column - Anonymized Profile
            with col_right:
                st.subheader("🔐 Anonymized Profile")
                if st.session_state.anonymized_profile:
                    st.json(st.session_state.anonymized_profile)
                else:
                    st.info("Click 'Anonymize Profile' to see the anonymized version")
            
            # Anonymize button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔒 Anonymize Profile", type="primary", use_container_width=True):
                    with st.spinner("Anonymizing profile..."):
                        try:
                            # Perform anonymization
                            anonymized = anonymizer.anonymize_profile(
                                st.session_state.selected_profile
                            )
                            st.session_state.anonymized_profile = anonymized
                            st.success("✅ Profile successfully anonymized!")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            # Additional actions
            st.divider()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Reset", use_container_width=True):
                    st.session_state.anonymized_profile = None
                    st.rerun()
            
            with col2:
                if st.session_state.anonymized_profile:
                    anonymized_json = json.dumps(st.session_state.anonymized_profile, indent=2)
                    st.download_button(
                        label="📥 Download Anonymized",
                        data=anonymized_json,
                        file_name=f"anonymized_{selected_entry}.json",
                        mime="application/json",
                        use_container_width=True
                    )
    else:
        st.warning("No profiles available. Please upload a JSON file.")


if __name__ == "__main__":
    main()
