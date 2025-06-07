# dashboard.py

import streamlit as st
from mood_visualizations import create_dashboard_mood_summary

# Enhanced CSS for professional and attractive design
def add_hover_styles():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom Dashboard Styles */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .dashboard-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .dashboard-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Enhanced Tile Styles */
    .feature-tile {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
        padding: 2rem;
        border-radius: 20px;
        border: none;
        text-align: center;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
        backdrop-filter: blur(4px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        margin-bottom: 1.5rem;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .feature-tile::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 20px 20px 0 0;
    }
    
    .feature-tile:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(31, 38, 135, 0.25);
    }
    
    .tile-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .tile-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.4rem;
        color: #1a1a1a;
        margin-bottom: 0.8rem;
    }
    
    .tile-description {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 0.95rem;
        color: #666;
        line-height: 1.5;
        margin-bottom: 1.5rem;
    }
    
    /* Mood Tracker Special Styling */
    .mood-tile {
        background: linear-gradient(145deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        color: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(255, 154, 158, 0.3);
        transition: all 0.3s ease;
        margin-bottom: 1.5rem;
    }
    
    .mood-tile:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(255, 154, 158, 0.4);
    }
    
    .mood-tile h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Analytics Button Special Style */
    .analytics-button button {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        box-shadow: 0 4px 15px rgba(255, 154, 158, 0.3);
    }
    
    .analytics-button button:hover {
        background: linear-gradient(135deg, #ff8a95 0%, #fdbde5 100%);
        box-shadow: 0 8px 25px rgba(255, 154, 158, 0.4);
    }
    
    /* Footer Styling */
    .footer-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-top: 3rem;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
    }
    
    .footer-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 1rem;
    }
    
    .footer-text {
        font-family: 'Inter', sans-serif;
        color: #555;
        line-height: 1.6;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .dashboard-header h1 {
            font-size: 2rem;
        }
        
        .feature-tile {
            min-height: 180px;
            padding: 1.5rem;
        }
        
        .tile-icon {
            font-size: 2.5rem;
        }
    }
    
    /* Animation for tiles */
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
    
    .feature-tile {
        animation: fadeInUp 0.6s ease-out forwards;
    }
    
    .feature-tile:nth-child(1) { animation-delay: 0.1s; }
    .feature-tile:nth-child(2) { animation-delay: 0.2s; }
    .feature-tile:nth-child(3) { animation-delay: 0.3s; }
    .feature-tile:nth-child(4) { animation-delay: 0.4s; }
    </style>
    """, unsafe_allow_html=True)


def display_dashboard():
    """Display the enhanced main dashboard with tiles for different features"""
    st.title(f"Welcome, {st.session_state['user_name']}!")
    add_hover_styles()
    
    # Enhanced Header with your logo
   

    # Create dashboard layout
    left_col, right_col = st.columns([2, 1])

    with left_col:
        # First row of tiles
        col1, col2 = st.columns(2)

        # Chatbot tile
        with col1:
            st.markdown("""
            <div class="feature-tile">
                <div class="tile-icon">🤖</div>
                <div class="tile-title">Chatbot And OCR</div>
                <div class="tile-description">Get personalized health advice with our AI assistant</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Open Chatbot", key="open_chatbot", use_container_width=True):
                st.session_state['current_page'] = 'chatbot'
                st.rerun()

        # Emotional Diary tile
        with col2:
            st.markdown("""
            <div class="feature-tile">
                <div class="tile-icon">📝</div>
                <div class="tile-title">Emotional Diary</div>
                <div class="tile-description">Express your feelings and receive supportive responses</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Open Diary", key="open_diary", use_container_width=True):
                st.session_state['current_page'] = 'emotional_diary'
                st.rerun()

        # Second row of tiles
        col3, col4 = st.columns(2)

        # Medical Profile tile
        with col3:
            st.markdown("""
            <div class="feature-tile">
                <div class="tile-icon">👤</div>
                <div class="tile-title">My Medical Profile</div>
                <div class="tile-description">Update and view your medical information</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("View Profile", key="view_profile", use_container_width=True):
                st.session_state['current_page'] = 'profile'
                st.rerun()

       

    with right_col:
        # Enhanced Mood tracking summary
        st.markdown("""
        <div class="mood-tile">
            <h3>Mood Tracker</h3>
            <p style="opacity: 0.9; margin-bottom: 1rem;">Track your emotional patterns and gain insights</p>
        </div>
        """, unsafe_allow_html=True)

        create_dashboard_mood_summary(st.session_state['user_id'])

        # Analytics button with special styling
        st.markdown('<div class="analytics-button">', unsafe_allow_html=True)
        if st.button("View Detailed Analytics", key="view_analytics", use_container_width=True):
            st.session_state['current_page'] = 'emotional_diary'
            st.session_state['diary_view_mode'] = 'Mood Analytics'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer-section">
        <h3 class="footer-title" style="color:black">About Swasthya AI</h3>
        <div class="footer-text">
            <p>Swasthya AI is your personal health assistant, providing health advice tailored to your medical conditions. 
            Our AI-powered chatbot offers personalized guidance while respecting your privacy.</p>
    </div>
    """, unsafe_allow_html=True)