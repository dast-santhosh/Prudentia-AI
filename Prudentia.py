import streamlit as st
import requests
import json
import os
import folium
from streamlit_folium import st_folium

# --- 1. API Configuration & Environment Variables ---
try:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    GUIDANCE_MODEL = "openai/gpt-oss-20b:free" #KERNEL USED AND BASE FOR THE DEVELOPMENT (AFTER DATA TRAINING)
    PETITION_MODEL = "google/gemma-3n-e4b-it:free" #KERNEL (MULTI LANGUAGE MODEL) USED AND BASE FOR THE DEVELOPMENT (AFTER DATA TRAINING)

except KeyError:
    st.error("API key not found. Please add your OPENROUTER_API_KEY to the secrets.toml file.")
    st.stop()
except Exception as e:
    st.error(f"Error during API configuration: {str(e)}")
    st.stop()


# --- 2. API Calls & Business Logic ---
@st.cache_data(show_spinner="Generating legal guidance...")
def generate_legal_guidance(case_type, name, phone, email, address, state, form_data, description, documents, witnesses, additional_info):
    """Generates legal guidance using the OpenRouter API based on user input."""
    prompt = f"""
    As Prudentia, an expert Indian legal advisor, provide self-representation (party-in-person) guidance for a user in {state} with the following legal issue:

    **Case Type:** {case_type}
    **Description:** {description}
    **User Info:** Name: {name}, Address: {address}, State: {state}
    **Evidence:** Docs: {documents}, Witnesses: {witnesses}, Other: {additional_info}

    Provide a comprehensive, practical response in five markdown sections:
    1.  **Legal Analysis & Guidance:** Analyze the case, cite relevant Indian laws/precedents, and provide immediate, actionable steps.
    2.  **Required Documents:** List all necessary documents/evidence, noting any format requirements (e.g., stamp paper).
    3.  **Court Procedure:** Outline the step-by-step filing process for a party-in-person and suggest the correct court jurisdiction.
    4.  **Your Rights & Remedies:** Explain the user's rights and potential remedies.
    5.  **A Quick Summary:** Provide a 3-4 sentence summary of the key takeaways.

    Use simple Hinglish where appropriate and include a clear disclaimer at the end.
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GUIDANCE_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        full_response = response.json()['choices'][0]['message']['content']
        
        sections = {
            'analysis': '',
            'documents': '',
            'procedure': '',
            'rights': '',
            'summary': ''
        }
        
        parts = full_response.split("## ")
        for part in parts:
            if "Legal Analysis" in part:
                sections['analysis'] = "## " + part
            elif "Required Documents" in part:
                sections['documents'] = "## " + part
            elif "Court Procedure" in part:
                sections['procedure'] = "## " + part
            elif "Your Rights" in part:
                sections['rights'] = "## " + part
            elif "A Quick Summary" in part:
                sections['summary'] = "## " + part
        
        return sections
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling OpenRouter API: {e}")
        return None
    except KeyError:
        st.error("Error parsing API response. The response format may have changed.")
        return None

@st.cache_data(show_spinner="Drafting your petition...")
def generate_petition_text(case_type, name, phone, email, address, state, description, documents, witnesses, language):
    """
    Generates a draft petition text using the OpenRouter API.
    Uses the "google/gemma-3n-e4b-it:free" model for generation.
    """
    prompt = f"""
    Draft a formal petition for a 'party-in-person' in {state}. The petition should be addressed to the concerned authority or court.

    **Case Type:** {case_type}
    **Petitioner Details:** Name: {name}, Address: {address}, Phone: {phone}
    **Subject:** Petition regarding {case_type} in {state}.
    **Case Description:** {description}
    **Supporting Documents:** {documents}
    **Witnesses:** {witnesses}

    The petition should have the following sections:
    1.  **To:** [Name of the Concerned Authority/Court], [Address of the Authority/Court]
    2.  **Subject:** [A concise, formal subject line]
    3.  **Respected Sir/Madam,**
    4.  **Introduction:** Start with a formal statement introducing the petitioner and the matter.
    5.  **Body:** Detail the facts of the case and the legal issue, referencing the case description provided. Explain why you are petitioning.
    6.  **Prayer:** Clearly state what the petitioner is seeking (e.g., relief, compensation, an order from the court).
    7.  **Sincerely,**
        [Your Name]
        [Your Address]
        [Your Phone Number]

    Write the petition in {language}. Use formal, respectful legal language suitable for an Indian context. Do not include any placeholder text like `[Your Name]` in the final response. Use the provided user data directly. The response should be a complete, ready-to-use petition draft.
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": PETITION_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error generating petition draft: {e}")
        return None
    except KeyError:
        st.error("Error parsing API response for petition draft.")
        return None


# --- 3. Streamlit App Components ---

def _render_header():
    """Renders the main title, sub-header, and the new Contribute button."""
    col1, col2 = st.columns([4, 1])
    with col1:
        st.image("logo.png", width=250)
        st.title("⚖️ Prudentia: Your Legal Companion")
        st.markdown("### Get legal guidance for common issues in India - *Party-in-Person* support")
    with col2:
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True) # Spacer
        if st.button("🤝 Contribute"):
            st.session_state.show_contribute = True

    st.markdown("---")

def _render_sidebar():
    """Renders the entire sidebar content."""
    with st.sidebar:
        st.image("logo.png", width=150)
        st.header("Prudentia")
        st.markdown("---")

        with st.expander("📋 Select Legal Issue", expanded=True):
            case_types = [
                "Consumer Complaint", "Property Dispute", "Family Matter (Divorce/Maintenance)",
                "Employment Issue", "Landlord-Tenant Dispute", "Police Complaint (FIR)",
                "Motor Accident Claim", "Bank/Financial Issue", "Public Interest Litigation", "Other"
            ]
            st.session_state.selected_case = st.selectbox("Choose your case type:", case_types)

        with st.expander("🔍 Quick Help"):
            st.markdown("**🚨 Emergency Legal Contacts:**")
            st.markdown("- **NALSA Legal Aid Helpline:** 15100")
            st.markdown("- **Women's Helpline:** 181")
            st.markdown("- **National Consumer Helpline:** 1915")
            st.markdown("---")
            st.markdown("**💡 Pro Tips:**")
            st.markdown("- Keep all documents organized in a folder.")
            st.markdown("- Take photos or videos of evidence.")
            st.markdown("- Maintain a written record of all communications.")
            st.markdown("- Be aware of filing deadlines (limitation periods).")

        _render_map()

        with st.expander("🤖 About Prudentia"):
            st.info("""
                Prudentia is an AI-powered legal assistant designed to help individuals understand their rights and the legal process for self-representation.
            """)
        
        with st.expander("👨‍💻 About the Founder"):
            st.markdown("""
                <style>
                .founder-image {
                    border: 5px solid #4CAF50;
                    border-radius: 20px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    transition: transform 0.3s ease-in-out;
                }
                .founder-image:hover {
                    transform: scale(1.05);
                }
                </style>
            """, unsafe_allow_html=True)
            st.image("img.png", use_container_width=True, output_format="auto")
            st.markdown("""
            **I'm Santhosh, a student, innovator, and entrepreneur** passionate about AI, robotics, and business technology. I’ve founded initiatives like Codesphere to teach robotics and AI, and I’m building products such as Chela.AI (AI assistant for teachers) and Zocal (business automation app). My interests also extend to aerospace research and new digital file formats. I believe in using technology to solve real-world problems and create meaningful impact.
            """)

def _render_map():
    """Renders the interactive map with court locations."""
    with st.expander("🏛️ Find Courts"):
        st.markdown("**🗺️ Find a Court Near You:**")
        
        pin_code_map = {
            "110001": {"name": "New Delhi", "coords": [28.6139, 77.2090]},
            "400001": {"name": "Mumbai", "coords": [18.9750, 72.8258]},
            "700001": {"name": "Kolkata", "coords": [22.5726, 88.3639]},
            "600001": {"name": "Chennai", "coords": [13.0827, 80.2707]},
            "560001": {"name": "Bengaluru", "coords": [12.9716, 77.5946]},
            "500001": {"name": "Hyderabad", "coords": [17.3850, 78.4867]},
        }
        
        initial_center = [20.5937, 78.9629]
        initial_zoom = 4
        
        pin_code = st.text_input("Enter your Pin Code to zoom into your district:")
        current_center = initial_center
        current_zoom = initial_zoom
        
        if pin_code in pin_code_map:
            coords = pin_code_map[pin_code]["coords"]
            current_center = coords
            current_zoom = 12
            st.success(f"Zooming to {pin_code_map[pin_code]['name']}!")
        elif pin_code:
            st.warning("Pin code not found in our demonstration data. Showing a map of India instead.")

        m = folium.Map(location=current_center, zoom_start=current_zoom)
        
        courts_data = [
            {"name": "Supreme Court of India", "coords": [28.6151, 77.2390], "color": "red"},
            {"name": "Allahabad High Court", "coords": [25.4542, 81.8267], "color": "blue"},
            {"name": "Bombay High Court", "coords": [18.9221, 72.8335], "color": "blue"},
            {"name": "Madras High Court", "coords": [13.0886, 80.2858], "color": "blue"},
            {"name": "Delhi High Court", "coords": [28.6120, 77.2285], "color": "blue"},
            {"name": "Bandra Kurla Complex Court, Mumbai", "coords": [19.0664, 72.8687], "color": "green"},
            {"name": "Tis Hazari Courts, Delhi", "coords": [28.6657, 77.2104], "color": "green"},
            {"name": "Egmore Court, Chennai", "coords": [13.0768, 80.2586], "color": "green"},
        ]
        
        for court in courts_data:
            folium.Marker(
                location=court["coords"],
                popup=court["name"],
                icon=folium.Icon(color=court["color"], icon="briefcase", prefix='fa'),
            ).add_to(m)

        st_folium(m, width=300, height=300)

def _render_case_form():
    """Renders the dynamic case details form based on selected case type."""
    selected_case = st.session_state.selected_case
    
    with st.expander("⚖️ Case Details", expanded=True):
        description = ""
        form_data = {}

        if selected_case == "Consumer Complaint":
            form_data["company_name"] = st.text_input("Company/Service Provider Name *")
            form_data["complaint_nature"] = st.selectbox("Nature of Complaint", ["Defective Product", "Poor Service", "Unfair Trade Practice", "Overcharging", "Insurance Claim Rejection", "Other"])
            form_data["purchase_date"] = st.date_input("Purchase/Service Date")
            form_data["amount_involved"] = st.number_input("Amount Involved (₹)", min_value=0)
            description = st.text_area("Describe your complaint in detail *", height=100)
        
        elif selected_case == "Property Dispute":
            form_data["property_type"] = st.selectbox("Property Type", ["Residential", "Commercial", "Agricultural", "Plot/Land"])
            form_data["dispute_type"] = st.selectbox("Dispute Type", ["Ownership Dispute", "Partition", "Boundary Dispute", "Illegal Possession", "Document Issues", "Other"])
            form_data["property_value"] = st.number_input("Approximate Property Value (₹)", min_value=0)
            description = st.text_area("Describe the property dispute *", height=100)
        
        elif selected_case == "Family Matter (Divorce/Maintenance)":
            form_data["matter_type"] = st.selectbox("Type of Family Matter", ["Divorce (Mutual Consent)", "Divorce (Contested)", "Child Custody", "Maintenance/Alimony", "Domestic Violence", "Property Rights"])
            form_data["marriage_date"] = st.date_input("Date of Marriage")
            form_data["children"] = st.selectbox("Children involved?", ["No", "Yes"])
            description = st.text_area("Describe your situation *", height=100)
        
        elif selected_case == "Landlord-Tenant Dispute":
            form_data["user_type"] = st.selectbox("You are:", ["Tenant", "Landlord"])
            form_data["dispute_type"] = st.selectbox("Dispute Type", ["Rent Issues", "Eviction Notice", "Deposit Return", "Property Damage", "Lease Violation", "Other"])
            form_data["monthly_rent"] = st.number_input("Monthly Rent (₹)", min_value=0)
            description = st.text_area("Describe the dispute *", height=100)

        elif selected_case == "Employment Issue":
            form_data["role"] = st.text_input("Your Role/Designation")
            form_data["issue_type"] = st.selectbox("Issue Type", ["Unfair Termination", "Salary/Wage Dispute", "Harassment", "Workplace Safety", "Leave/Benefits Issues", "Other"])
            description = st.text_area("Describe your employment issue *", height=100)

        elif selected_case == "Police Complaint (FIR)":
            form_data["crime_type"] = st.text_input("Type of Offense (e.g., Theft, Cheating, Assault)")
            form_data["date_of_incident"] = st.date_input("Date of Incident")
            form_data["location_of_incident"] = st.text_input("Location of Incident")
            description = st.text_area("Describe the incident in detail *", height=100)
        
        else:
            description = st.text_area("Describe your legal issue in detail *", height=150)
            form_data["amount_involved"] = st.number_input("Amount Involved (if any) (₹)", min_value=0)

        st.session_state.description = description
        st.session_state.form_data = form_data

def _render_evidence_section():
    """Renders the documents and evidence input section."""
    with st.expander("📎 Documents & Evidence"):
        st.markdown("**List documents you have:**")
        st.session_state.documents = st.text_area(
            "List all documents you currently possess",
            placeholder="Example: Aadhaar card, Purchase receipt, Email correspondence, Photos, etc."
        )
        st.markdown("**Upload documents (optional):**")
        st.session_state.uploaded_files = st.file_uploader(
            "Upload files (PDF, JPG, PNG)",
            type=["pdf", "jpg", "jpeg", "png"],
            accept_multiple_files=True
        )

        st.markdown("**Additional Evidence:**")
        st.session_state.witnesses = st.text_area("Witness details (if any)")
        st.session_state.additional_info = st.text_area("Any other relevant information")

def _render_results_tabs(guidance):
    """Displays the AI-generated guidance in a tabbed interface."""
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Summary", "📋 Legal Analysis", "📄 Documents Needed",
        "🏛️ Court Procedure", "⚖️ Your Rights"
    ])
    
    with tab1:
        st.subheader("Quick Summary")
        st.markdown(guidance.get('summary', 'No summary found.'))

    with tab2:
        st.markdown(guidance.get('analysis', 'No analysis found.'))
    
    with tab3:
        st.markdown(guidance.get('documents', 'No documents information found.'))
    
    with tab4:
        st.markdown(guidance.get('procedure', 'No procedure information found.'))
    
    with tab5:
        st.markdown(guidance.get('rights', 'No rights information found.'))

def _render_feedback_section():
    """Renders a simple feedback mechanism."""
    st.markdown("---")
    st.subheader("Was this guidance helpful?")
    col_helpful, col_unhelpful = st.columns(2)
    with col_helpful:
        if st.button("👍 Yes, it was helpful!"):
            st.success("Thank you for your feedback! We're glad we could help.")
    with col_unhelpful:
        if st.button("👎 No, it was not helpful."):
            st.warning("We're sorry this was not helpful. We'll use your feedback to improve.")

def _render_editable_petition():
    """Renders the editable text area for the petition."""
    st.markdown("---")
    st.subheader("📝 Your Editable Petition Draft")
    st.info("The drafted petition is below. You can edit it directly here before copying and pasting it wherever you need.")
    
    petition_language = st.selectbox(
        "Select language for the petition draft:",
        ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam"],
        key="petition_language_select"
    )

    if st.button("Draft Petition", key="draft_petition_button", type="primary", use_container_width=True):
        petition_text = generate_petition_text(
            st.session_state.selected_case,
            st.session_state.name,
            st.session_state.phone,
            st.session_state.email,
            st.session_state.address,
            st.session_state.state,
            st.session_state.description,
            st.session_state.documents,
            st.session_state.witnesses,
            petition_language
        )
        st.session_state.petition_text = petition_text

    if "petition_text" in st.session_state and st.session_state.petition_text:
        st.text_area(
            "Edit and Copy Your Petition Here:",
            value=st.session_state.petition_text,
            height=600,
            key="editable_petition_text_area"
        )
    else:
        st.markdown("Click 'Draft Petition' to generate the text.")
    
def _display_main_form():
    """Renders the main content area with the legal guidance form."""
    _render_header()
    st.header("📝 Details Form")

    with st.expander("👤 Personal Information", expanded=True):
        st.session_state.name = st.text_input("Full Name *")
        st.session_state.phone = st.text_input("Phone Number *")
        st.session_state.email = st.text_input("Email (optional)")
        st.session_state.address = st.text_area("Complete Address *")
        states_of_india = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
            "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
            "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
            "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
            "Delhi", "Jammu and Kashmir", "Ladakh"
        ]
        st.session_state.state = st.selectbox("State *", states_of_india)

    _render_case_form()
    _render_evidence_section()
    
    st.markdown("---")
    
def _check_required_fields():
    """Checks if all required form fields are filled."""
    required_fields = [
        st.session_state.name,
        st.session_state.phone,
        st.session_state.address,
        st.session_state.description
    ]
    return all(required_fields)

def _get_guidance():
    """Triggers the guidance generation process and displays results."""
    if not _check_required_fields():
        st.error("⚠️ Please fill in all required fields marked with *")
    else:
        st.session_state.guidance = generate_legal_guidance(
            st.session_state.selected_case,
            st.session_state.name,
            st.session_state.phone,
            st.session_state.email,
            st.session_state.address,
            st.session_state.state,
            st.session_state.form_data,
            st.session_state.description,
            st.session_state.documents,
            st.session_state.witnesses,
            st.session_state.additional_info
        )
        if st.session_state.guidance:
            st.success("✅ Legal guidance generated successfully!")

def _render_contribute_section():
    """Renders the contribution pop-up section."""
    with st.container():
        st.markdown("---")
        st.subheader("Contribute to Prudentia AI 🚀")
        st.markdown("""
            <style>
            .upi-image {
                border: 5px solid #28A745;
                border-radius: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease-in-out;
                margin-bottom: 15px;
            }
            .upi-image:hover {
                transform: scale(1.05);
            }
            </style>
        """, unsafe_allow_html=True)
        st.image("upi.png", use_container_width=True, output_format="auto")
        st.info("""
            **Prudentia AI is built with the vision of making knowledge and technology accessible for everyone.** We’re constantly improving, and your support can help us grow faster. Whether it’s sharing ideas, giving feedback, contributing code, or supporting development, every contribution brings us closer to creating a smarter future together.
            
            **Join us in shaping Prudentia AI** — let’s build something impactful for the world 🌍✨
        """)
        st.button("Close", key="close_contribute_button")
        
# --- 4. Main Application Flow ---

def main():
    """Main function to run the Streamlit app."""
    # Set up initial session state
    if "guidance" not in st.session_state:
        st.session_state.guidance = None
    if "selected_case" not in st.session_state:
        st.session_state.selected_case = "Consumer Complaint"
    if "petition_text" not in st.session_state:
        st.session_state.petition_text = ""
    if "show_contribute" not in st.session_state:
        st.session_state.show_contribute = False
    
    # Check if the close button was clicked to reset the state
    if st.session_state.get("close_contribute_button", False):
        st.session_state.show_contribute = False
        st.session_state.close_contribute_button = False

    st.set_page_config(
        page_title="Prudentia: Your Legal Companion",
        page_icon="⚖️",
        layout="wide"
    )

    # Layout with columns
    col_empty_left, col_center, col_empty_right = st.columns([1, 4, 1])

    with col_center:
        _display_main_form()

        # The 'Get Legal Guidance' button
        st.markdown("---")
        if st.button("🎯 Get Legal Guidance", type="primary", use_container_width=True):
            _get_guidance()

        # Renders the results if guidance has already been generated
        if st.session_state.guidance:
            _render_results_tabs(st.session_state.guidance)
            _render_editable_petition()
            _render_feedback_section()

        # Renders the contribution section if the button is clicked
        if st.session_state.show_contribute:
            _render_contribute_section()

    _render_sidebar()
    
    # Add the copyright notice at the bottom
    st.markdown("---")
    st.markdown("<p style='text-align: center; font-size: 0.8em; color: #888;'>Santhosh | Prudentia | 2025</p>", unsafe_allow_html=True)


# --- 5. Main Execution Block ---
if __name__ == "__main__":
    main()

