# emotional_diary_page.py

import streamlit as st
from emotional_diary import display_diary_interface, load_diary_history, display_diary_history
from mood_visualizations import display_mood_visualizations


def display_emotional_diary():
    """Display the emotional diary page with interface, history and analytics options"""
    st.title('Emotional Diary')
    st.markdown("""
    Welcome to your personal emotional diary. Use this space to express your thoughts and feelings, 
    and receive supportive responses. Regular emotional journaling can help improve mental wellbeing.
    """)
    
    # Button to navigate back to dashboard
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("Back to Dashboard", use_container_width=True):
            st.session_state['current_page'] = 'dashboard'
            st.rerun()
    
    # Add diary sidebar options
    with st.sidebar:
        st.markdown("---")
        st.subheader("Diary Options")
        view_mode = st.radio(
            "View Mode:",
            ["Diary Interface", "Diary History", "Mood Analytics"],
            key="diary_view_mode"
        )

        if view_mode == "Diary Interface" and st.button("Clear Current Session", use_container_width=True):
            st.session_state.diary_messages = []
            st.rerun()
    
    # Load diary history if not already loaded
    load_diary_history(st.session_state['user_id'])
    
    # Display based on selected view mode
    if view_mode == "Diary Interface":
        display_diary_interface()
    elif view_mode == "Diary History":
        display_diary_history(st.session_state['user_id'])
    else:  # Mood Analytics
        display_mood_visualizations(st.session_state['user_id'])