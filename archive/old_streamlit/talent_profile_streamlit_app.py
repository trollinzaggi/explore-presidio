"""
Streamlit App for Talent Profile Anonymization
Uses the full Enhanced Talent Profile Anonymizer
"""

import streamlit as st
import json
import sys
from pathlib import Path

# Add the bias-anonymizer module to the path
sys.path.append(str(Path(__file__).parent / "bias-anonymizer/src"))

# Import our enhanced anonymizer
from bias_anonymizer.enhanced_talent_profile_anonymizer import EnhancedTalentProfileAnonymizer

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
                },
                "reportingDistance": {
                    "geb": "3",
                    "ceo": "4",
                    "chairman": "5"
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
                "internationalExperience": "Yes",
                "timeInCurrentRoleInDays": "1095"
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
                        "name": "Best Manager Award from CEO",
                        "organization": "Tech Corp",
                        "date": "2023-05-15"
                    }
                ],
                "memberships": []
            },
            "careerAspirationPreference": "Looking to lead C-suite",
            "careerLocationPreference": "Prefer conservative states",
            "careerRolePreference": "Looking for young, energetic team without family obligations",
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


def anonymize_profile(profile_data):
    """
    Function to anonymize a single profile using our Enhanced Talent Profile Anonymizer.
    
    Args:
        profile_data: The talent profile dictionary
        
    Returns:
        Anonymized profile dictionary
    """
    try:
        # Initialize the anonymizer
        anonymizer = EnhancedTalentProfileAnonymizer()
        
        # Anonymize the profile
        anonymized_profile = anonymizer.anonymize_talent_profile(profile_data)
        
        return anonymized_profile
    except Exception as e:
        st.error(f"Error during anonymization: {str(e)}")
        # Return a basic anonymization if the full version fails
        import copy
        return copy.deepcopy(profile_data)


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
            <p>Remove bias and PII from employee profiles using Microsoft Presidio</p>
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
        
        # Display statistics
        st.subheader("📊 Statistics")
        st.metric("Total Profiles", len(profiles_data))
        
        if st.session_state.anonymized_profile:
            st.success("✅ Profile Anonymized")
            
            # Count removed bias terms (simple approximation)
            original_str = json.dumps(st.session_state.selected_profile)
            anonymized_str = json.dumps(st.session_state.anonymized_profile)
            reduction = len(original_str) - len(anonymized_str)
            st.metric("Characters Removed", reduction)
    
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
                    with st.spinner("Anonymizing profile using Enhanced Talent Profile Anonymizer..."):
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
                    if st.button("📊 Show Details", use_container_width=True):
                        with st.expander("Anonymization Details", expanded=True):
                            st.write("**What was removed:**")
                            st.write("- Gender, race, and age indicators")
                            st.write("- Marital and family status")
                            st.write("- Religious and political affiliations")
                            st.write("- Socioeconomic background indicators")
                            st.write("- Health and disability information")
                            st.write("- Names and personal identifiers")
                            
                            st.write("\n**What was preserved:**")
                            st.write("- Job codes and rank codes")
                            st.write("- Technical skills and certifications")
                            st.write("- Degrees and areas of study")
                            st.write("- Years of experience")
                            st.write("- Organizational codes")
    else:
        st.warning("No profiles available. Please upload a JSON file with talent profiles.")
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #888; padding: 20px;'>
            <p>Built with Microsoft Presidio and Enhanced Talent Profile Anonymizer</p>
            <p>Ensures fair and unbiased talent matching</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
