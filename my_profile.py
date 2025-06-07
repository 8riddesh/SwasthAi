# profile.py

import streamlit as st
from database import SupabaseClient
from auth import hash_password, verify_password


def display_profile_update():
    """Display and handle the profile update form"""
    st.title("Update Your Profile")
    
    if not st.session_state['logged_in']:
        st.warning("Please log in to view and update your profile.")
        return
    
    # Get current user data
    db = SupabaseClient()
    user_id = st.session_state['user_id']
    user = db.get_user_by_id(user_id)
    
    if not user:
        st.error("Could not retrieve user information. Please try again later.")
        return
    
    # Create tabs for personal and medical info
    tab1, tab2 = st.tabs(["Personal Information", "Medical Information"])
    
    # Personal Information Tab
    with tab1:
        st.subheader("Update Personal Information")
        
        with st.form(key="update_personal_info"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name", value=user['full_name'])
                email = st.text_input("Email", value=user['email'], disabled=True)
                new_password = st.text_input("New Password (leave blank to keep current)", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
            
            with col2:
                age = st.number_input("Age", min_value=1, max_value=120, value=user['age'])
                gender = st.selectbox("Gender", 
                                     ["Male", "Female", "Other", "Prefer not to say"],
                                     index=["Male", "Female", "Other", "Prefer not to say"].index(user['gender']))
                contact_no = st.text_input("Contact Number", value=user['contact_no'])
            
            submit_personal = st.form_submit_button("Update Personal Information")
            
            if submit_personal:
                # Validate form
                if not all([full_name, age, gender, contact_no]):
                    st.error("Please fill in all required fields.")
                    return
                
                # Update user data
                update_data = {
                    'full_name': full_name,
                    'age': age,
                    'gender': gender,
                    'contact_no': contact_no
                }
                
                # Handle password update if provided
                if new_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match.")
                        return
                    update_data['password_hash'] = hash_password(new_password)
                
                # Update in database
                success = db.update_user(user_id, update_data)
                
                if success:
                    # Update session state
                    st.session_state['user_name'] = full_name
                    st.success("Personal information updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update information. Please try again.")
    
    # Medical Information Tab
    with tab2:
        st.subheader("Update Medical Information")
        
        # Get current medical conditions
        medical_info = db.get_user_medical_info(user_id)
        current_conditions = {info['condition_name']: info['condition_type'] for info in medical_info}
        
        # Form for updating medical info
        with st.form(key="update_medical_info"):
            col1, col2 = st.columns(2)
            
            # Standard conditions checkboxes
            with col1:
                st.write("Standard conditions:")
                diabetes = st.checkbox("Diabetes", value=("diabetes" in current_conditions))
                hypertension = st.checkbox("Hypertension", value=("hypertension" in current_conditions))
                asthma = st.checkbox("Asthma", value=("asthma" in current_conditions))
                heart_disease = st.checkbox("Heart Disease", value=("heart_disease" in current_conditions))
            
            # Custom conditions
            with col2:
                st.write("Custom conditions:")
                custom_conditions_list = [cond for cond, type_ in current_conditions.items() 
                                         if type_ == 'custom']
                custom_conditions = st.text_area(
                    "Enter any other medical conditions (one per line)",
                    value="\n".join(custom_conditions_list)
                )
            
            submit_medical = st.form_submit_button("Update Medical Information")
            
            if submit_medical:
                # Prepare medical conditions
                new_conditions = {
                    'standard': {
                        'diabetes': diabetes,
                        'hypertension': hypertension,
                        'asthma': asthma,
                        'heart_disease': heart_disease
                    },
                    'custom': custom_conditions.strip().split('\n') if custom_conditions.strip() else []
                }
                
                # Clear existing medical info and add new ones
                success = db.update_medical_info(user_id, new_conditions)
                
                if success:
                    st.success("Medical information updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update medical information. Please try again.")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Back to Dashboard", use_container_width=True):
            st.session_state['current_page'] = 'dashboard'
            st.rerun()