"""
Streamlit app for Bias Anonymizer - Professional Version
Clean, professional interface without icons or unnecessary elements
"""

import streamlit as st
import json
import sys
import os
from pathlib import Path
import warnings

# Suppress SSL warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bias_anonymizer.config_loader import create_anonymizer_from_config, load_config_from_yaml
from bias_anonymizer.talent_profile_anonymizer import TalentProfileAnonymizer

# Page configuration - clean and professional
st.set_page_config(
    page_title="Bias Anonymizer",
    layout="wide"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    .stApp {
        background-color: white;
    }
    .stButton>button {
        background-color: #0066CC;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #0052A3;
    }
    .stTextArea textarea {
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 12px;
    }
    h1 {
        color: #333333;
        font-weight: 500;
    }
    h2 {
        color: #444444;
        font-weight: 500;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
    h3 {
        color: #555555;
        font-weight: 500;
    }
    .success-text {
        color: #008000;
        font-weight: 500;
    }
    .error-text {
        color: #CC0000;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Load configuration once at startup
@st.cache_resource
def load_anonymizer():
    """Load the anonymizer with configuration."""
    try:
        config = load_config_from_yaml()
        anonymizer = create_anonymizer_from_config()
        strategy = config.get('anonymization_strategy', 'custom')
        return anonymizer, config, strategy
    except Exception as e:
        st.error(f"Configuration Error: {str(e)}")
        return None, None, None

# Sample profiles for testing
SAMPLE_PROFILES = {
    "Software Engineer": {
        "userId": "EMP123456",
        "core": {
            "businessTitle": "Senior white male software engineer from Harvard",
            "jobCode": "ENG_SR_001",
            "rank": {
                "code": "L7",
                "id": "RANK_007",
                "description": "Principal Engineer level - mostly older white males in this rank"
            },
            "employeeType": {
                "code": "FTE",
                "description": "Full-time employee, married with children"
            },
            "gcrs": {
                "businessDivisionCode": "TECH",
                "businessDivisionDescription": "Technology Division - predominantly male workforce",
                "businessUnitCode": "CLOUD",
                "businessUnitDescription": "Cloud Engineering - young millennial team",
                "businessAreaDescription": "Backend Services - Asian and Indian engineers"
            },
            "workLocation": {
                "code": "SF_HQ_01",
                "description": "San Francisco HQ near Castro district",
                "city": "San Francisco",
                "state": "California - liberal state",
                "country": "United States"
            }
        },
        "language": {
            "languages": ["English - native speaker", "Spanish - from Mexican heritage"],
            "createdBy": "John Smith (john.smith@company.com)",
            "lastModifiedBy": "Mary Johnson (555-123-4567)"
        },
        "workEligibility": "US Citizen, no visa required (SSN: 123-45-6789)"
    },
    
    "Product Manager": {
        "userId": "EMP789012",
        "core": {
            "businessTitle": "Black female product manager, single mother",
            "jobCode": "PM_SR_002",
            "rank": {
                "code": "L6",
                "id": "RANK_006",
                "description": "Senior PM level - diverse but mostly young professionals"
            },
            "employeeType": {
                "code": "FTE",
                "description": "Full-time, pregnant, on maternity leave soon"
            }
        },
        "experience": {
            "experiences": [{
                "company": "Previous Corp (contact: hr@previous.com)",
                "description": "Led team of mostly female designers and gay developers",
                "jobTitle": "Senior Product Lead"
            }]
        },
        "qualification": {
            "educations": [{
                "institutionName": "Stanford University - wealthy elite school",
                "degree": "MBA",
                "achievements": "First-generation college student, scholarship recipient"
            }]
        }
    },
    
    "Data Scientist": {
        "userId": "EMP345678",
        "core": {
            "businessTitle": "Asian male data scientist with disability",
            "jobCode": "DS_MID_003",
            "rank": {
                "code": "L5",
                "description": "Mid-level - requires accommodation for wheelchair access"
            }
        },
        "careerAspirationPreference": "Want to work with diverse, LGBTQ+ friendly team",
        "careerLocationPreference": "Seattle or Portland - progressive cities",
        "affiliation": {
            "memberships": [{
                "organization": "Association of Muslim Professionals",
                "details": "Active member, follows halal dietary requirements"
            }]
        }
    }
}

def main():
    # Load anonymizer and config
    anonymizer, config, strategy = load_anonymizer()
    
    if not anonymizer:
        st.error("Failed to load anonymizer. Please check configuration.")
        return
    
    # Header
    st.title("Bias Anonymizer")
    st.markdown(f"Configuration: `default_config.yaml` | Strategy: **{strategy}**")
    st.markdown("---")
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Input Profile")
        
        # Profile selection or input
        input_method = st.radio(
            "Input Method",
            ["Select Sample Profile", "Paste JSON"],
            label_visibility="collapsed"
        )
        
        if input_method == "Select Sample Profile":
            selected_profile = st.selectbox(
                "Profile Selection",
                list(SAMPLE_PROFILES.keys()),
                label_visibility="collapsed"
            )
            profile_data = SAMPLE_PROFILES[selected_profile]
            
            # Show the profile in an editable text area
            profile_json = json.dumps(profile_data, indent=2)
            edited_json = st.text_area(
                "Profile JSON",
                value=profile_json,
                height=400,
                label_visibility="collapsed"
            )
            
            try:
                profile_data = json.loads(edited_json)
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {str(e)}")
                return
        
        else:  # Paste JSON
            profile_json = st.text_area(
                "Profile JSON",
                value="{}",
                height=400,
                placeholder="Paste JSON here...",
                label_visibility="collapsed"
            )
            
            try:
                profile_data = json.loads(profile_json)
            except json.JSONDecodeError as e:
                if profile_json != "{}":
                    st.error(f"Invalid JSON: {str(e)}")
                return
    
    # Anonymize button
    st.markdown("")
    if st.button("Anonymize Profile"):
        with st.spinner("Processing..."):
            try:
                # Analyze profile first
                analysis = anonymizer.analyze_profile(profile_data)
                
                # Anonymize profile
                anonymized_data = anonymizer.anonymize_talent_profile(profile_data)
                
                # Store in session state
                st.session_state['anonymized'] = anonymized_data
                st.session_state['original'] = profile_data
                st.session_state['analysis'] = analysis
                
                st.markdown('<p class="success-text">Profile anonymized successfully</p>', unsafe_allow_html=True)
                
            except Exception as e:
                st.markdown(f'<p class="error-text">Error: {str(e)}</p>', unsafe_allow_html=True)
    
    # Show results in second column
    with col2:
        st.header("Anonymized Result")
        
        if 'anonymized' in st.session_state:
            # Show anonymized JSON
            anonymized_json = json.dumps(st.session_state['anonymized'], indent=2)
            st.text_area(
                "Result JSON",
                value=anonymized_json,
                height=400,
                label_visibility="collapsed"
            )
            
            # Download button
            st.download_button(
                label="Download JSON",
                data=anonymized_json,
                file_name="anonymized_profile.json",
                mime="application/json"
            )
        else:
            st.text_area(
                "Result JSON",
                value="",
                height=400,
                placeholder="Results will appear here...",
                disabled=True,
                label_visibility="collapsed"
            )
    
    # Analysis section
    if 'analysis' in st.session_state:
        st.markdown("---")
        with st.expander("Analysis Details"):
            analysis = st.session_state['analysis']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Risk Score", f"{analysis['risk_score']}/100")
            with col2:
                st.metric("Fields Checked", analysis['total_fields_checked'])
            with col3:
                st.metric("Fields with Bias", len(analysis['fields_with_bias']))
            with col4:
                st.metric("Fields with PII", len(analysis['fields_with_pii']))
            
            st.markdown("")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Bias Categories Found**")
                for category in sorted(analysis['bias_categories_found']):
                    st.text(f"• {category}")
            
            with col2:
                st.markdown("**PII Types Found**")
                for pii_type in sorted(analysis['pii_types_found']):
                    st.text(f"• {pii_type}")
    
    # Configuration details
    st.markdown("---")
    with st.expander("Configuration Details"):
        st.markdown(f"""
        **Current Configuration**
        
        - Strategy: `{strategy}`
        - Configuration File: `config/default_config.yaml`
        - Preserve Fields: {len(config.get('preserve_fields', []))} fields
        - Always Anonymize: {len(config.get('always_anonymize_fields', []))} fields
        - Operators Configured: {len(config.get('operators', {}))} types
        
        **Anonymization Coverage**
        
        Bias Categories (14):
        - Gender, Race/Ethnicity, Age, Disability
        - Marital/Family Status, Nationality
        - Sexual Orientation, Religion
        - Political Affiliation, Socioeconomic Background
        - Pregnancy/Maternity, Union Membership
        - Health Conditions, Criminal Background
        
        PII Types:
        - Names → [NAME]
        - Emails → Masked
        - Phones → Hashed
        - SSN → Masked
        - Locations → [LOCATION]
        - Dates → [DATE]
        """)

if __name__ == "__main__":
    main()
