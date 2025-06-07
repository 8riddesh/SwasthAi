#auth.py

import streamlit as st
import bcrypt
from database import SupabaseClient


def hash_password(password):
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))


def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = None
    if 'user_name' not in st.session_state:
        st.session_state['user_name'] = None
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'dashboard'


def add_auth_styles():
    """Add formal, professional styling for authentication pages matching dashboard theme"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }
    .auth-header {
        background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
        padding: 2.5rem 2rem;
        border-radius: 18px;
        color: #f4f6fa;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 28px rgba(75, 108, 183, 0.18);
    }
    .auth-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.2rem;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.18);
    }
    .auth-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        opacity: 0.92;
        margin-top: 0.7rem;
        font-weight: 400;
    }
    .auth-form-container {
        background: linear-gradient(145deg, #f3f4f7 0%, #e9ecf3 100%);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 6px 24px rgba(31, 38, 135, 0.10);
        border: 1px solid #e3e7ef;
        margin-bottom: 2rem;
    }
    .form-header {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.5rem;
        color: #232946;
        margin-bottom: 1.2rem;
        text-align: center;
    }
    /* Input and Label Styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border: 2px solid #c3c8d6;
        border-radius: 10px;
        padding: 0.7rem 1rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.97rem;
       
        color: white !important;
        transition: all 0.3s ease;
    }

    /* Label colors and styling */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label,
    .stTextArea > label {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: white !important;
        font-size: 0.92rem;
        
        padding: 4px 8px;
        border-radius: 6px;
        margin-bottom: 4px;
    }

    /* Style select dropdown text */
    .stSelectbox > div > div > select option {
        background: #232946;
        color: #f4f6fa;
    }

    /* Style markdown text in forms */
    .stMarkdown {
        color: #f4f6fa;
    }

    /* Style form subheaders */
    .stMarkdown h3 {
        color: #f4f6fa;
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
        color: #f4f6fa;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 3px 12px rgba(75, 108, 183, 0.13);
        margin-top: 1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(75, 108, 183, 0.18);
        background: linear-gradient(135deg, #3a539b 0%, #232946 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Checkbox Styling */
    .stCheckbox {
        font-family: 'Inter', sans-serif;
        color: #374151;
    }
    
    .stCheckbox > label {
        font-size: 0.92rem;
        font-weight: 400;
    }
    
    /* Medical Conditions Section */
    .medical-section {
        background: #f0f2f5;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1.2rem 0;
        border: 1px solid #d1d5db;
    }
    
    .medical-section h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #4b6cb7;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }
    
    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        font-family: 'Inter', sans-serif;
        border-radius: 10px;
        border: none;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.07);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(102, 126, 234, 0.1);
        border-radius: 15px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
        background: transparent;
        border-radius: 10px;
        color: #667eea;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* User Info Sidebar */
    .user-info-card {
        background: linear-gradient(145deg, #f3f4f7 0%, #e9ecf3 100%);
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(31, 38, 135, 0.08);
        margin-bottom: 1rem;
        border: 1px solid #e3e7ef;
    }
    
    .user-avatar {
        width: 54px;
        height: 54px;
        background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        color: #f4f6fa;
        margin: 0 auto 0.8rem auto;
    }
    
    .user-name {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #232946;
        text-align: center;
        margin-bottom: 0.4rem;
    }
    
    .user-email {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        color: #555;
        text-align: center;
        font-size: 0.92rem;
    }
    
    /* Welcome Message */
    .welcome-message {
        background: linear-gradient(145deg, #e9ecf3 0%, #f3f4f7 100%);
        padding: 1.5rem;
        border-radius: 16px;
        color: #232946;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 6px 18px rgba(75, 108, 183, 0.08);
    }
    
    .welcome-message h2, .welcome-message h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #232946;
        text-shadow: none;
    }
    
    /* Animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .auth-form-container {
        animation: fadeInUp 0.6s ease-out forwards;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .auth-header h1 {
            font-size: 1.5rem;
        }
        
        .auth-form-container {
            padding: 1.2rem;
        }
        
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def login_page():
    """Display the professional medical login page and handle login attempts"""
    add_auth_styles()
    
    # Header - moved to top

    
    # Login Form Container
  
    st.markdown('<h2 class="form-header">Patient Portal Access</h2>', unsafe_allow_html=True)
    
    st.markdown("Please enter your credentials to access your medical dashboard.")
    st.markdown("---")
    
    email = st.text_input(
        "Email Address", 
        key="login_email", 
        placeholder="Enter your registered email address",
        help="Use the email address provided during registration"
    )
    password = st.text_input(
        "Password", 
        type="password", 
        key="login_password", 
        placeholder="Enter your secure password",
        help="Password is case-sensitive"
    )

    if st.button("Access Medical Dashboard", use_container_width=True):
        if not email or not password:
            st.error("⚠️ Authentication Error: Both email and password are required for secure access")
            return

        # Attempt to log in the user
        db = SupabaseClient()
        user = db.get_user_by_email(email)

        if user and verify_password(user['password_hash'], password):
            # Set session state
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = user['id']
            st.session_state['user_email'] = user['email']
            st.session_state['user_name'] = user['full_name']
            st.session_state['current_page'] = 'dashboard'
            st.success("✅ Authentication Successful - Redirecting to your medical dashboard...")
            st.rerun()
            return user['id']
        else:
            st.error("❌ Authentication Failed: Invalid credentials. Please verify your email and password.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Security info



def register_page():
    """Display the professional medical registration page and handle registration attempts"""
    add_auth_styles()
    
    # Header - at the top
    

    # Registration Form Container

    st.markdown('<h2 class="form-header">New Patient Registration</h2>', unsafe_allow_html=True)
    
    st.markdown("Please complete all sections accurately. This information will be used to provide personalized medical assistance.")
    st.markdown("---")

    with st.form(key="registration_form"):
        # Personal Information Section
        st.subheader("📋 Personal Information")
        st.markdown("*Required for patient identification and communication*")
        
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input(
                "Full Legal Name", 
                placeholder="Enter your complete legal name",
                help="Enter your name as it appears on official documents"
            )
            email = st.text_input(
                "Email Address", 
                placeholder="Enter a valid email address",
                help="This will be used for secure communication and login"
            )
            password = st.text_input(
                "Create Password", 
                type="password", 
                placeholder="Create a secure password (min. 8 characters)",
                help="Use a combination of letters, numbers, and symbols"
            )

        with col2:
            confirm_password = st.text_input(
                "Confirm Password", 
                type="password", 
                placeholder="Re-enter your password",
                help="Must match the password entered above"
            )
            age = st.number_input(
                "Age", 
                min_value=1, 
                max_value=120, 
                step=1, 
                value=25,
                help="Your current age in years"
            )
            gender = st.selectbox(
                "Gender", 
                ["Male", "Female", "Other", "Prefer not to disclose"],
                help="Select your gender for medical record purposes"
            )
        
        contact_no = st.text_input(
            "Primary Contact Number", 
            placeholder="Enter your primary phone number with country code",
            help="Include country code (e.g., +91 for India)"
        )

        # Medical History Section
        # st.markdown('<div class="medical-section">', unsafe_allow_html=True)
        st.subheader("🏥 Medical History & Conditions")
        st.markdown("*This information helps provide accurate medical assistance and personalized recommendations*")
        
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Pre-existing Medical Conditions:**")
            diabetes = st.checkbox("Diabetes Mellitus (Type 1 or 2)")
            hypertension = st.checkbox("Hypertension (High Blood Pressure)")
            asthma = st.checkbox("Asthma or Respiratory Conditions")
            heart_disease = st.checkbox("Cardiovascular Disease")

        with col2:
            st.markdown("**Additional Medical Information:**")
            custom_conditions = st.text_area(
                "Other medical conditions, allergies, or chronic illnesses", 
                placeholder="Please list any other medical conditions, allergies, medications, or chronic illnesses (one per line)\n\nExample:\n- Allergy to Penicillin\n- Migraine headaches\n- Previous surgery details",
                height=120,
                help="Include allergies, medications, previous surgeries, or any other relevant medical history"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Terms and conditions
        st.markdown("---")
        st.markdown("**Medical Disclaimer & Privacy Policy**")
        terms_accepted = st.checkbox(
            "I acknowledge that this platform provides health information and AI assistance, but does not replace professional medical advice. I understand that all information will be kept confidential and secure.",
            help="Required to proceed with registration"
        )

        submit_button = st.form_submit_button("Complete Registration", use_container_width=True)

        if submit_button:
            # Validate form fields
            if not all([full_name, email, password, confirm_password, age, gender, contact_no]):
                st.error("⚠️ Registration Error: All required fields must be completed.")
                return

            if not terms_accepted:
                st.error("⚠️ Please acknowledge the medical disclaimer and privacy policy to proceed.")
                return

            if password != confirm_password:
                st.error("❌ Password Mismatch: The passwords entered do not match.")
                return

            if len(password) < 8:
                st.error("🔒 Password Security: Password must be at least 8 characters long for security.")
                return

            # Email validation
            if "@" not in email or "." not in email.split("@")[-1]:
                st.error("📧 Invalid Email: Please enter a valid email address.")
                return

            # Hash the password
            password_hash = hash_password(password)

            # Prepare user data
            user_data = {
                'email': email,
                'password_hash': password_hash,
                'full_name': full_name,
                'age': age,
                'gender': gender,
                'contact_no': contact_no
            }

            # Prepare medical conditions
            medical_conditions = {
                'standard': {
                    'diabetes': diabetes,
                    'hypertension': hypertension,
                    'asthma': asthma,
                    'heart_disease': heart_disease
                },
                'custom': [condition.strip() for condition in custom_conditions.strip().split('\n') if condition.strip()] if custom_conditions else []
            }

            # Create user in database
            db = SupabaseClient()
            existing_user = db.get_user_by_email(email)

            if existing_user:
                st.error("📧 Registration Error: This email address is already registered. Please use a different email or proceed to login.")
                return

            user = db.create_user(user_data)

            if user:
                # Add medical info
                db.create_medical_info(user['id'], medical_conditions)

                st.success("✅ Registration Successful: Your medical profile has been created. You may now access the platform using your credentials.")
                
                # Switch to login tab
                st.session_state['show_login'] = True
                st.rerun()
            else:
                st.error("❌ Registration Failed: Unable to create account. Please try again or contact support.")

    st.markdown('</div>', unsafe_allow_html=True)


def logout():
    """Log out the current user"""
    st.session_state['logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['user_email'] = None
    st.session_state['user_name'] = None
    st.session_state['current_page'] = 'login'
    if 'chat_messages' in st.session_state:
        del st.session_state['chat_messages']


def show_user_info():
    """Display professional user information in the sidebar"""
    if st.session_state['logged_in']:
        # User info card
        st.sidebar.markdown("""
        <div class="user-info-card">
            <div class="user-avatar">👤</div>
            <div class="user-name">{}</div>
            <div class="user-email">{}</div>
        </div>
        """.format(st.session_state['user_name'], st.session_state['user_email']), 
        unsafe_allow_html=True)

        # Get user medical info
        db = SupabaseClient()
        medical_info = db.get_user_medical_info(st.session_state['user_id'])

        if medical_info:
            with st.sidebar.expander("📋 Medical Profile", expanded=False):
                st.markdown("**Recorded Medical Conditions:**")
                conditions = [info['condition_name'] for info in medical_info]
                if conditions:
                    for condition in conditions:
                        st.write(f"• {condition}")
                else:
                    st.write("No medical conditions on record")
                st.markdown("---")
                st.markdown("*Last updated: Current session*")
    else:
        st.sidebar.markdown("""
        <div class="welcome-message">
            <h3>Medical Platform Access</h3>
            <p>Secure authentication required to access your medical dashboard and health information.</p>
        </div>
        """, unsafe_allow_html=True)