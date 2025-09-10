"""
Streamlit App for Talent Profile Anonymization
Displays original and anonymized profiles side by side
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Add the bias-anonymizer to path
sys.path.append(str(Path(__file__).parent.parent / "bias-anonymizer/src"))

from bias_anonymizer.enhanced_talent_profile_anonymizer import EnhancedTalentProfileAnonymizer
from bias_anonymizer import JSONAnonymizer, AnonymizerConfig

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
    .json-container {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #ddd;
        max-height: 600px;
        overflow-y: auto;
    }
    .profile-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stats-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin-bottom: 15px;
    }
    pre {
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    </style>
    """, unsafe_allow_html=True)


class TalentProfileApp:
    """Streamlit app for talent profile anonymization."""
    
    def __init__(self):
        """Initialize the app."""
        self.initialize_session_state()
        self.anonymizer = EnhancedTalentProfileAnonymizer()
    
    def initialize_session_state(self):
        """Initialize session state variables."""
        if 'profiles_data' not in st.session_state:
            st.session_state.profiles_data = {}
        if 'anonymized_profile' not in st.session_state:
            st.session_state.anonymized_profile = None
        if 'selected_profile' not in st.session_state:
            st.session_state.selected_profile = None
        if 'analysis_report' not in st.session_state:
            st.session_state.analysis_report = None
    
    def load_profiles(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load profiles from JSON file.
        
        Args:
            file_path: Path to JSON file containing profiles
            
        Returns:
            Dictionary of profiles
        """
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            # Return sample profiles if no file provided
            return self.get_sample_profiles()
    
    def get_sample_profiles(self) -> Dict[str, Any]:
        """Get sample talent profiles for demonstration."""
        return {
            "John_Smith_001": {
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
                        "description": "San Francisco - Liberal area",
                        "city": "San Francisco",
                        "state": "California",
                        "country": "United States"
                    }
                },
                "workEligibility": "US Citizen, no visa required",
                "experience": {
                    "experiences": [
                        {
                            "company": "Google - Young workforce culture",
                            "jobTitle": "Senior Engineering Manager",
                            "description": "Led team of mostly Asian engineers",
                            "startDate": "2015-03-01",
                            "endDate": "2020-12-31"
                        }
                    ]
                },
                "qualification": {
                    "educations": [
                        {
                            "institutionName": "Stanford University - Elite school",
                            "degree": "MS Computer Science",
                            "areaOfStudy": "Machine Learning",
                            "completionYear": 2000
                        }
                    ],
                    "certifications": ["AWS Solutions Architect", "Google Cloud Professional"]
                },
                "careerPreference": "Looking for young, energetic team"
            },
            "Maria_Garcia_002": {
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
                        "description": "Full Time - Requires childcare flexibility"
                    },
                    "businessTitle": "Engineer from working-class background",
                    "jobCode": "ENG_MID_002",
                    "workLocation": {
                        "code": "NY_01",
                        "city": "New York",
                        "state": "New York",
                        "country": "United States"
                    }
                },
                "workEligibility": "Green Card holder",
                "affiliation": {
                    "awards": [
                        {
                            "id": "AWD_001",
                            "name": "Diversity Award from LGBTQ group",
                            "organization": "Pride Tech Network",
                            "date": "2023-06-15"
                        }
                    ],
                    "memberships": [
                        {
                            "organizationName": "Women in Tech - Feminist group",
                            "role": "Active Member",
                            "since": "2018"
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
                }
            },
            "David_Chen_003": {
                "userId": "USER_11111",
                "core": {
                    "rank": {
                        "code": "L6",
                        "description": "Senior Engineer - Asian male, Buddhist",
                        "id": "RANK_006"
                    },
                    "businessTitle": "Engineer - Gay, partnered",
                    "jobCode": "ENG_SR_003",
                    "workLocation": {
                        "code": "SEA_01",
                        "city": "Seattle",
                        "state": "Washington"
                    }
                },
                "experience": {
                    "experiences": [
                        {
                            "company": "Microsoft",
                            "jobTitle": "Software Engineer",
                            "description": "Worked with predominantly Indian team",
                            "startDate": "2018-01-15"
                        }
                    ]
                },
                "careerPreference": "Prefer inclusive, LGBTQ-friendly environment"
            }
        }
    
    def analyze_profile(self, profile: Dict) -> Dict:
        """
        Analyze a profile for bias and PII.
        
        Args:
            profile: Profile to analyze
            
        Returns:
            Analysis report
        """
        # Create a simple analysis
        bias_terms_found = []
        pii_found = []
        
        def scan_dict(d, path=""):
            results = {"bias": [], "pii": []}
            for key, value in d.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, str):
                    # Check for bias terms
                    bias_keywords = ["male", "female", "white", "asian", "hispanic", "christian", 
                                   "muslim", "jewish", "gay", "lesbian", "wealthy", "poor",
                                   "young", "old", "married", "single", "disabled"]
                    for term in bias_keywords:
                        if term.lower() in value.lower():
                            results["bias"].append((current_path, term))
                    
                    # Check for PII
                    if any(x in value.lower() for x in ["@", "citizen", "visa", "green card"]):
                        results["pii"].append(current_path)
                        
                elif isinstance(value, dict):
                    nested = scan_dict(value, current_path)
                    results["bias"].extend(nested["bias"])
                    results["pii"].extend(nested["pii"])
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            nested = scan_dict(item, f"{current_path}[{i}]")
                            results["bias"].extend(nested["bias"])
                            results["pii"].extend(nested["pii"])
            return results
        
        results = scan_dict(profile)
        
        return {
            "total_bias_terms": len(results["bias"]),
            "total_pii_fields": len(results["pii"]),
            "bias_categories": list(set([term for _, term in results["bias"]])),
            "risk_score": min(100, len(results["bias"]) * 5 + len(results["pii"]) * 10)
        }
    
    def run(self):
        """Run the Streamlit app."""
        
        # Header
        st.markdown("""
            <div class="profile-header">
                <h1>🔒 Talent Profile Anonymizer</h1>
                <p>Remove bias and PII from employee profiles for fair candidate matching</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Sidebar for file upload and settings
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
                    profiles_data = self.get_sample_profiles()
            else:
                profiles_data = self.get_sample_profiles()
                if not st.session_state.profiles_data:
                    st.session_state.profiles_data = profiles_data
                else:
                    profiles_data = st.session_state.profiles_data
            
            st.divider()
            
            # Anonymization options
            st.subheader("Anonymization Options")
            
            detect_bias = st.checkbox("Detect Bias Terms", value=True)
            detect_pii = st.checkbox("Detect PII", value=True)
            confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.7, 0.05)
            
            # Display statistics
            st.divider()
            st.subheader("📊 Statistics")
            st.metric("Total Profiles", len(profiles_data))
            
            if st.session_state.anonymized_profile:
                st.success("✅ Profile Anonymized")
            
            if st.session_state.analysis_report:
                st.metric("Risk Score", 
                         f"{st.session_state.analysis_report['risk_score']}/100",
                         help="Based on bias and PII detected")
        
        # Main content area
        # Profile selector
        profile_names = list(profiles_data.keys())
        
        if profile_names:
            selected_entry = st.selectbox(
                "📋 Select a Profile to Anonymize:",
                profile_names,
                index=0,
                help="Choose a talent profile from the dropdown"
            )
            
            # Store selected profile
            if selected_entry:
                st.session_state.selected_profile = profiles_data[selected_entry]
                
                # Analysis section
                if st.session_state.selected_profile:
                    with st.expander("📈 Profile Analysis", expanded=False):
                        analysis = self.analyze_profile(st.session_state.selected_profile)
                        st.session_state.analysis_report = analysis
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Bias Terms", analysis['total_bias_terms'])
                        with col2:
                            st.metric("PII Fields", analysis['total_pii_fields'])
                        with col3:
                            st.metric("Risk Score", f"{analysis['risk_score']}/100")
                        with col4:
                            st.metric("Categories", len(analysis['bias_categories']))
                        
                        if analysis['bias_categories']:
                            st.write("**Bias Categories Found:**", ", ".join(analysis['bias_categories']))
                
                # Create two columns for side-by-side display
                col_left, col_right = st.columns(2)
                
                # Left column - Original Profile
                with col_left:
                    st.subheader("📄 Original Profile")
                    if st.session_state.selected_profile:
                        # Display JSON with syntax highlighting
                        st.json(st.session_state.selected_profile)
                    else:
                        st.info("Select a profile from the dropdown above")
                
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
                        if st.session_state.selected_profile:
                            with st.spinner("Anonymizing profile..."):
                                try:
                                    # Perform anonymization
                                    anonymized = self.anonymizer.anonymize_talent_profile(
                                        st.session_state.selected_profile
                                    )
                                    st.session_state.anonymized_profile = anonymized
                                    st.success("✅ Profile successfully anonymized!")
                                    st.balloons()
                                    
                                    # Rerun to update the display
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"Error during anonymization: {e}")
                        else:
                            st.warning("Please select a profile first")
                
                # Additional actions
                st.divider()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🔄 Reset", use_container_width=True):
                        st.session_state.anonymized_profile = None
                        st.session_state.analysis_report = None
                        st.rerun()
                
                with col2:
                    if st.session_state.anonymized_profile:
                        # Download anonymized profile
                        anonymized_json = json.dumps(st.session_state.anonymized_profile, indent=2)
                        st.download_button(
                            label="📥 Download Anonymized",
                            data=anonymized_json,
                            file_name=f"anonymized_{selected_entry}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                
                with col3:
                    if st.session_state.selected_profile and st.session_state.anonymized_profile:
                        # Compare button
                        if st.button("📊 Compare Details", use_container_width=True):
                            with st.expander("Detailed Comparison", expanded=True):
                                st.write("**Fields Modified:**")
                                
                                # Simple comparison
                                original_str = json.dumps(st.session_state.selected_profile, sort_keys=True)
                                anonymized_str = json.dumps(st.session_state.anonymized_profile, sort_keys=True)
                                
                                if len(original_str) != len(anonymized_str):
                                    st.write(f"- Original length: {len(original_str)} characters")
                                    st.write(f"- Anonymized length: {len(anonymized_str)} characters")
                                    st.write(f"- Reduction: {len(original_str) - len(anonymized_str)} characters")
        else:
            st.warning("No profiles available. Please upload a JSON file with talent profiles.")
        
        # Footer
        st.divider()
        st.markdown("""
            <div style='text-align: center; color: #888; padding: 20px;'>
                <p>Built with Microsoft Presidio | Ensures fair and unbiased talent matching</p>
            </div>
        """, unsafe_allow_html=True)


# Run the app
if __name__ == "__main__":
    app = TalentProfileApp()
    app.run()
