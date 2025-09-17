"""
Streamlit App for Talent Profile Anonymization
Clean UI version using the FULL Enhanced Talent Profile Anonymizer
"""

import streamlit as st
import json
import sys
import os
from pathlib import Path

# Add the bias-anonymizer module to the path
sys.path.insert(0, str(Path(__file__).parent / "bias-anonymizer/src"))

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
                        "position": "Board Member for wealthy Christians",
                        "boardType": "advisory",
                        "description": "Exclusive club for Republican donors",
                        "startDate": "2020-01-01"
                    }
                ],
                "awards": [
                    {
                        "name": "Best Manager Award from white male CEO John Anderson",
                        "organization": "Tech Corp - Conservative company",
                        "description": "Given to white male leaders only",
                        "date": "2023-05-15"
                    }
                ],
                "mandates": [
                    {
                        "title": "Diversity Committee Chair - Token white male",
                        "organization": "Industry Group for wealthy executives",
                        "description": "Leading initiative for hiring more young white males"
                    }
                ],
                "memberships": [
                    {
                        "organizationName": "Golf Club - White males only",
                        "role": "Premium Member",
                        "description": "Networking with other wealthy white executives"
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
                        "role": "Active Member for single mothers",
                        "since": "2018",
                        "description": "Supporting other Hispanic women and LGBTQ members"
                    }
                ],
                "awards": [
                    {
                        "name": "Diversity Champion Award from lesbian director Sarah Johnson",
                        "organization": "LGBTQ Tech Alliance",
                        "description": "For supporting gay and lesbian colleagues from minority backgrounds"
                    }
                ],
                "boards": [
                    {
                        "organizationName": "Hispanic Women Engineers Association",
                        "position": "Board Member",
                        "description": "Advocating for immigrant women in tech"
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
            "affiliation": {
                "memberships": [
                    {
                        "organizationName": "Asian LGBTQ Engineers Network",
                        "role": "Founding Member",
                        "description": "Supporting gay Asian immigrants in tech"
                    }
                ],
                "awards": [
                    {
                        "name": "Pride Award from gay CEO",
                        "organization": "Rainbow Tech Coalition",
                        "description": "For advancing LGBTQ Asian representation"
                    }
                ],
                "mandates": [
                    {
                        "title": "LGBTQ Inclusion Lead for Chinese immigrants",
                        "organization": "Tech Diversity Council",
                        "description": "Promoting gay and lesbian Asian visibility"
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


def anonymize_profile_with_config(profile_data):
    """
    Anonymize a profile using the Enhanced Talent Profile Anonymizer.
    Configured to focus on experience, education, qualification, and affiliation sections.
    
    Args:
        profile_data: The talent profile dictionary
        
    Returns:
        Anonymized profile dictionary
    """
    # Configure the anonymizer to focus on specific sections
    config = TalentProfileConfig()
    
    # Add custom rules for sections to process
    custom_rules = {
        # Preserve core section fields (don't anonymize)
        "core.rank.description": "preserve",
        "core.employeeType.description": "preserve",
        "core.businessTitle": "preserve",
        "core.gcrs.businessDivisionDescription": "preserve",
        "core.workLocation.description": "preserve",
        "workEligibility": "preserve",
        "careerAspirationPreference": "preserve",
        "careerLocationPreference": "preserve",
        "careerRolePreference": "preserve",
        
        # Anonymize experience, qualification, education, affiliation
        "experience": "anonymize",
        "qualification": "anonymize",
        "affiliation": "anonymize",
        
        # Remove email and phone fields
        "personalEmail": "remove",
        "personalPhone": "remove",
        "managerEmail": "remove",
        "managerPhone": "remove",
        "contactEmail": "remove",
        
        # Remove social media
        "socialMedia": "remove"
    }
    
    # Initialize the anonymizer with config
    anonymizer = EnhancedTalentProfileAnonymizer(config)
    
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
    
    # File upload section at the top
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
        # Use sample profiles if no file uploaded
        profiles_data = get_sample_profiles()
        if not st.session_state.profiles_data:
            st.session_state.profiles_data = profiles_data
        else:
            profiles_data = st.session_state.profiles_data
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Info section about what gets anonymized
    with st.expander("View Anonymization Details"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Sections Processed:**
            - Experience (all bias removed)
            - Education (all bias removed)
            - Qualification (all bias removed)
            - Affiliation (Boards, Mandates, Awards, Memberships)
            
            **What Gets Removed:**
            - All bias words from our comprehensive list
            - Email addresses
            - Phone numbers
            - Social media links
            - Organization/Institution names
            """)
        
        with col2:
            st.markdown("""
            **Advanced Features:**
            - Uses Microsoft Presidio for PII detection
            - Custom bias recognizers for all categories
            - Automatic nested structure detection
            - Intelligent field processing
            - Preserves data integrity
            
            **Unchanged Sections:**
            - Core section details
            - User IDs and codes
            - Dates and timestamps
            """)
    
    # Add spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main content area
    if profiles_data:
        # Profile selector
        st.markdown("### Select Profile")
        selected_entry = st.selectbox(
            "Choose a profile to anonymize:",
            list(profiles_data.keys()),
            index=0,
            help="Select a talent profile from the dropdown"
        )
        
        # Store the selected profile
        if selected_entry:
            st.session_state.selected_profile = profiles_data[selected_entry]
            
            # Add spacing
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Create two columns for side-by-side display
            col_left, col_right = st.columns(2)
            
            # Left column - Original Profile
            with col_left:
                st.markdown("### Original Profile")
                with st.container():
                    st.json(st.session_state.selected_profile)
            
            # Right column - Anonymized Profile
            with col_right:
                st.markdown("### Anonymized Profile")
                if st.session_state.anonymized_profile:
                    with st.container():
                        st.json(st.session_state.anonymized_profile)
                else:
                    st.info("Click 'Anonymize Profile' button below to see the anonymized version")
            
            # Anonymize button - centered at the bottom
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Anonymize Profile", type="primary", use_container_width=True):
                    with st.spinner("Processing with Enhanced Talent Profile Anonymizer..."):
                        try:
                            # Call the anonymize function with the selected profile
                            anonymized = anonymize_profile_with_config(st.session_state.selected_profile)
                            
                            # Store the result
                            st.session_state.anonymized_profile = anonymized
                            
                            # Show success message
                            st.success("Profile successfully anonymized using advanced bias detection!")
                            
                            # Rerun to update the display
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error during anonymization: {str(e)}")
                            st.info("Make sure all required packages are installed: presidio-analyzer, presidio-anonymizer, spacy")
            
            # Additional action buttons
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Reset", use_container_width=True):
                    st.session_state.anonymized_profile = None
                    st.rerun()
            
            with col2:
                if st.session_state.anonymized_profile:
                    # Download button for anonymized profile
                    anonymized_json = json.dumps(st.session_state.anonymized_profile, indent=2)
                    st.download_button(
                        label="Download Anonymized Profile",
                        data=anonymized_json,
                        file_name=f"anonymized_{selected_entry}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            
            with col3:
                if st.session_state.selected_profile and st.session_state.anonymized_profile:
                    # Show analysis
                    if st.button("Show Analysis", use_container_width=True):
                        with st.expander("Anonymization Analysis", expanded=True):
                            # Calculate statistics
                            original_str = json.dumps(st.session_state.selected_profile)
                            anonymized_str = json.dumps(st.session_state.anonymized_profile)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Original Size", f"{len(original_str)} chars")
                            with col2:
                                st.metric("Anonymized Size", f"{len(anonymized_str)} chars")
                            with col3:
                                reduction = len(original_str) - len(anonymized_str)
                                st.metric("Reduction", f"{reduction} chars ({reduction/len(original_str)*100:.1f}%)")
                            
                            st.markdown("---")
                            st.markdown("""
                            **Processing Summary:**
                            - Bias words removed from all configured sections
                            - PII detection using Microsoft Presidio
                            - Organization names replaced with generic placeholders
                            - Nested structures automatically processed
                            - Data integrity maintained throughout
                            """)
    else:
        st.warning("No profiles available. Please upload a JSON file with talent profiles.")
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 10px;'>
            <p>Powered by Microsoft Presidio and Enhanced Talent Profile Anonymizer</p>
            <p>Ensuring fair and unbiased talent matching through advanced bias detection</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
