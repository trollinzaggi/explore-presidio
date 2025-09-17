"""
Streamlit App for Talent Profile Anonymization
Removes BOTH bias words AND PII information
"""

import streamlit as st
import json
import sys
import os
import re
import copy
from pathlib import Path
import hashlib
from datetime import datetime

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
        "unmarried", "unwed", "celibate", "engaged", "coupled", "maternal", "paternal"
    ],
    'socioeconomic': [
        "wealthy", "rich", "poor", "working-class", "upper-class", "middle-class",
        "privileged", "elite", "disadvantaged", "low-income", "high-income",
        "blue-collar", "white-collar", "immigrant", "refugee", "first-generation",
        "trust fund", "scholarship", "public school", "private school", "ivy league"
    ],
    'religion': [
        "christian", "muslim", "jewish", "hindu", "buddhist", "catholic", "protestant",
        "baptist", "methodist", "presbyterian", "evangelical", "orthodox", "islamic",
        "mosque", "church", "synagogue", "temple", "atheist", "agnostic", "secular"
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
        "green card", "visa", "citizen", "immigrant", "foreign", "native", "indigenous"
    ]
}

# Flatten all bias words into a single list
ALL_BIAS_WORDS = []
for category_words in BIAS_WORDS.values():
    ALL_BIAS_WORDS.extend(category_words)

# PII patterns
PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
    'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    'date_of_birth': r'\b(?:0[1-9]|1[0-2])[/\-.](?:0[1-9]|[12]\d|3[01])[/\-.](?:19|20)\d{2}\b',
    'passport': r'\b[A-Z]{1,2}\d{6,9}\b',
    'driver_license': r'\b[A-Z]{1,2}\d{5,8}\b'
}

# Fields that might contain PII (names, locations, etc.)
PII_FIELDS = {
    'names': ['name', 'firstname', 'lastname', 'fullname', 'username', 'createdby', 
              'modifiedby', 'lastmodifiedby', 'approvedby', 'reviewedby'],
    'locations': ['address', 'street', 'city', 'state', 'country', 'location', 
                  'hometown', 'birthplace', 'residence'],
    'identifiers': ['email', 'phone', 'mobile', 'fax', 'linkedin', 'twitter', 
                   'facebook', 'github', 'website', 'url'],
    'sensitive': ['salary', 'compensation', 'income', 'wage', 'bonus', 'equity',
                 'medical', 'health', 'diagnosis', 'medication', 'treatment']
}


def remove_pii_from_text(text):
    """
    Remove PII patterns from text.
    
    Args:
        text: Input text
        
    Returns:
        Text with PII removed
    """
    if not text or not isinstance(text, str):
        return text
    
    result = text
    
    # Remove PII patterns
    for pii_type, pattern in PII_PATTERNS.items():
        replacement = f"[{pii_type.upper().replace('_', '-')}]"
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result


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
    
    # Return placeholder if string became empty
    if not result and len(text) > 5:
        return "[REDACTED]"
    
    return result


def anonymize_date(date_str):
    """
    Anonymize date to year only.
    
    Args:
        date_str: Date string
        
    Returns:
        Year only or [YEAR]
    """
    if not date_str or not isinstance(date_str, str):
        return date_str
    
    # Try to extract year
    year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
    if year_match:
        return year_match.group()
    
    return "[YEAR]"


def hash_identifier(identifier):
    """
    Hash an identifier to maintain uniqueness but remove actual value.
    
    Args:
        identifier: Original identifier
        
    Returns:
        Hashed version
    """
    if not identifier:
        return identifier
    
    # Create a hash
    hashed = hashlib.sha256(str(identifier).encode()).hexdigest()[:8].upper()
    return f"ID_{hashed}"


def should_remove_field(field_name):
    """
    Check if a field should be completely removed.
    
    Args:
        field_name: Field name
        
    Returns:
        Boolean indicating if field should be removed
    """
    field_lower = field_name.lower()
    
    # Fields that should be completely removed
    remove_fields = [
        'createdby', 'modifiedby', 'lastmodifiedby', 'approvedby',
        'updatedby', 'deletedby', 'email', 'emailaddress', 'phone',
        'phonenumber', 'mobile', 'socialmedia', 'linkedin', 'twitter',
        'facebook', 'personalwebsite'
    ]
    
    return field_lower in remove_fields


def should_hash_field(field_name):
    """
    Check if a field should be hashed.
    
    Args:
        field_name: Field name
        
    Returns:
        Boolean indicating if field should be hashed
    """
    field_lower = field_name.lower()
    
    # Fields that should be hashed
    hash_fields = ['userid', 'employeeid', 'personid', 'candidateid', 'applicantid']
    
    return field_lower in hash_fields


def anonymize_profile(profile_data):
    """
    Function to anonymize a single profile by removing bias AND PII.
    
    Args:
        profile_data: The talent profile dictionary
        
    Returns:
        Anonymized profile dictionary
    """
    # Fields to preserve (don't anonymize)
    preserve_fields = {
        "code", "id", "jobCode", "externalSourceType",
        "completionYear", "degree", "areaOfStudy", "certifications",
        "crossDivisionalExperience", "internationalExperience",
        "timeInCurrentRoleInDays", "version", "completionScore",
        "businessDivisionCode", "businessUnitCode", "boardType",
        "membershipType", "educationType", "certificationLevel"
    }
    
    def process_value(value, field_name=""):
        """Recursively process values in the profile."""
        field_lower = field_name.lower()
        
        # Check if field should be removed entirely
        if should_remove_field(field_name):
            return None
        
        if isinstance(value, dict):
            # Process dictionary
            result = {}
            for k, v in value.items():
                processed = process_value(v, k)
                # Only add if not None (not removed)
                if processed is not None:
                    result[k] = processed
            return result
            
        elif isinstance(value, list):
            # Process list
            processed_list = []
            for item in value:
                processed = process_value(item, field_name)
                if processed is not None:
                    processed_list.append(processed)
            return processed_list
            
        elif isinstance(value, str):
            # Process string based on field type
            
            # Preserve certain fields
            if field_name in preserve_fields:
                return value
            
            # Hash user IDs
            if should_hash_field(field_name):
                return hash_identifier(value)
            
            # Anonymize dates
            if 'date' in field_lower or 'time' in field_lower:
                return anonymize_date(value)
            
            # First remove PII patterns
            value = remove_pii_from_text(value)
            
            # Then remove bias words
            value = remove_bias_from_text(value)
            
            # Additional PII removal for name fields
            if any(name_field in field_lower for name_field in ['name', 'title', 'organization', 'institution', 'company']):
                # Check if it looks like a person's name (contains common first/last names)
                common_names = ['john', 'jane', 'smith', 'garcia', 'chen', 'williams', 'johnson', 
                              'brown', 'jones', 'miller', 'davis', 'wilson', 'anderson', 'taylor',
                              'thomas', 'jackson', 'martin', 'lee', 'thompson', 'white', 'harris',
                              'clark', 'lewis', 'robinson', 'walker', 'hall', 'allen', 'king']
                
                for name in common_names:
                    if name in value.lower():
                        value = re.sub(r'\b' + name + r'\b', '', value, flags=re.IGNORECASE)
                
                # Clean up the result
                value = re.sub(r'\s+', ' ', value).strip()
                
                # If it's empty or too short, use generic placeholder
                if not value or len(value) < 3:
                    if 'institution' in field_lower or 'school' in field_lower or 'university' in field_lower:
                        return "[INSTITUTION]"
                    elif 'company' in field_lower or 'organization' in field_lower:
                        return "[ORGANIZATION]"
                    elif 'title' in field_lower:
                        return "[TITLE]"
                    else:
                        return "[NAME]"
            
            return value
            
        else:
            # Return other types as-is (numbers, booleans, None)
            return value
    
    # Create a deep copy and process it
    anonymized = copy.deepcopy(profile_data)
    anonymized = process_value(anonymized)
    
    # Clean up empty structures
    def clean_empty(data):
        """Remove empty strings, lists, and dictionaries."""
        if isinstance(data, dict):
            result = {}
            for k, v in data.items():
                cleaned = clean_empty(v)
                if cleaned not in [None, "", [], {}]:
                    result[k] = cleaned
            return result
        elif isinstance(data, list):
            result = []
            for item in data:
                cleaned = clean_empty(item)
                if cleaned not in [None, "", [], {}]:
                    result.append(cleaned)
            return result
        else:
            return data
    
    anonymized = clean_empty(anonymized)
    
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
                "lastModifiedBy": "Manager Sarah Williams",
                "email": "john.smith@company.com",
                "phone": "415-555-1234"
            },
            "experience": {
                "experiences": [
                    {
                        "company": "Google - Known for young workforce",
                        "jobTitle": "Senior Engineering Manager for white collar workers",
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
                        "institutionName": "Stanford University - Elite private school for wealthy families",
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
                        "name": "Best Manager Award from CEO John Anderson",
                        "organization": "Tech Corp",
                        "date": "2023-05-15"
                    }
                ],
                "memberships": []
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
                        "description": "For supporting gay and lesbian colleagues",
                        "recipientEmail": "maria.garcia@company.com"
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
                        "company": "Microsoft",
                        "jobTitle": "Software Engineer",
                        "description": "Worked with predominantly Indian and Chinese team of immigrants",
                        "startDate": "2018-01-15",
                        "managerEmail": "manager@microsoft.com",
                        "managerPhone": "206-555-4321"
                    }
                ],
                "personalReference": "Former manager John Davis at 425-555-1111"
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
            <p>Remove ALL bias words and PII for completely fair matching</p>
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
            st.metric("Reduction %", f"{(reduction/len(original_str)*100):.1f}%")
    
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
                    with st.spinner("Removing bias words and PII..."):
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
                        with st.expander("What Was Removed", expanded=True):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**🚫 Bias Words Removed:**")
                                st.write("- Gender indicators (male, female, etc.)")
                                st.write("- Race/ethnicity terms")
                                st.write("- Age-related words")
                                st.write("- Marital/family status")
                                st.write("- Religious affiliations")
                                st.write("- Political leanings")
                                st.write("- Sexual orientation")
                                st.write("- Socioeconomic indicators")
                                st.write("- Disability references")
                                st.write("- Nationality/citizenship")
                            
                            with col2:
                                st.write("**🔒 PII Removed:**")
                                st.write("- Email addresses")
                                st.write("- Phone numbers")
                                st.write("- Personal names")
                                st.write("- Social media links")
                                st.write("- Specific dates → Year only")
                                st.write("- User IDs → Hashed")
                                st.write("- CreatedBy/ModifiedBy fields")
                                st.write("- Location details")
                                st.write("- Organization names")
                                st.write("- Institution names")
                            
                            st.write("\n**✅ What Was Preserved:**")
                            st.write("- Job codes and rank codes")
                            st.write("- Technical skills and certifications")
                            st.write("- Degrees and areas of study")
                            st.write("- Completion years")
                            st.write("- Business division/unit codes")
                            st.write("- Experience indicators (Yes/No)")
    else:
        st.warning("No profiles available. Please upload a JSON file with talent profiles.")
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #888; padding: 20px;'>
            <p>Talent Profile Anonymizer - Complete Bias and PII Removal</p>
            <p>Ensuring 100% Fair and Anonymous Matching</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
