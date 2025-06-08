# app.py
import streamlit as st
import os
import requests
from dotenv import load_dotenv
from auth import initialize_session_state, login_page, register_page, show_user_info, logout
from chat import display_chat_interface, load_chat_history, display_chat_history
from dashboard import display_dashboard
from my_profile import display_profile_update
from emotional_diary_page import display_emotional_diary
from database import SupabaseClient
from groq import Groq
from pathlib import Path
import time
import tempfile
import gtts
from gtts import gTTS
import base64

# Load environment variables
load_dotenv()

# Setup LangChain tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

client = Groq(api_key="apiKey")
speech_file_path = Path(__file__).parent / "speech.mp3"

# N8N configuration
N8N_CHATBOT_URL = os.getenv("N8N_CHATBOT_URL", "webhook-endpoint")
N8N_FILE_UPLOAD_URL = os.getenv("N8N_FILE_UPLOAD_URL", "webhook-endpoint")
user_id = None
web_url = "webhook-endpoint"

def generate_audio(text, key_suffix=""):
    """Generate audio from text using gTTS and return the file path"""
    try:
        if not text or len(text.strip()) == 0:
            st.error("❌ No text available for audio generation")
            return None
            
        # Limit text length for audio generation (gTTS has limitations)
        max_length = 5000
        if len(text) > max_length:
            text = text[:max_length] + "... (text truncated for audio)"
            st.info(f"📝 Text truncated to {max_length} characters for audio generation")
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(tmp_file.name)
            return tmp_file.name
            
    except Exception as e:
        st.error(f"❌ Audio generation failed: {str(e)}")
        return None

def display_audio_player(text, key_suffix=""):
    """Display audio player with generation button"""
    audio_key = f"audio_file_{key_suffix}"
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("🔊 Generate Audio", key=f"gen_audio_{key_suffix}"):
            with st.spinner("Generating audio..."):
                audio_file = generate_audio(text, key_suffix)
                if audio_file:
                    st.session_state[audio_key] = audio_file
                    st.success("✅ Audio generated successfully!")
                    st.rerun()
    
    # Display audio player if audio file exists
    if audio_key in st.session_state and st.session_state[audio_key]:
        try:
            with col2:
                # Read the audio file and display it
                with open(st.session_state[audio_key], 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/mp3")
                    
                # Cleanup button
                if st.button("🗑️ Clear Audio", key=f"clear_audio_{key_suffix}"):
                    try:
                        if os.path.exists(st.session_state[audio_key]):
                            os.unlink(st.session_state[audio_key])
                    except:
                        pass
                    del st.session_state[audio_key]
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Error playing audio: {str(e)}")
            # Clean up corrupted audio file reference
            if audio_key in st.session_state:
                del st.session_state[audio_key]

def cleanup_temp_files():
    """Clean up temporary audio files on session end"""
    for key in list(st.session_state.keys()):
        if key.startswith('audio_file_'):
            try:
                if os.path.exists(st.session_state[key]):
                    os.unlink(st.session_state[key])
            except:
                pass

def display_chatbot():
    """Display the chatbot page with interface and history options"""
    st.title('Swasthya AI Chatbot 🏥')

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "message_counter" not in st.session_state:
        st.session_state.message_counter = 0

    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("Back to Dashboard", use_container_width=True):
            cleanup_temp_files()
            st.session_state['current_page'] = 'dashboard'
            st.rerun()

    with st.sidebar:
        st.markdown("---")
        st.subheader("Chatbot Options")
        view_mode = st.radio("View Mode:", ["Chat Interface", "Chat History"], key="view_mode")

        if view_mode == "Chat Interface" and st.button("Clear Current Chat", use_container_width=True):
            cleanup_temp_files()
            st.session_state.chat_messages = []
            st.session_state.response_history = []
            st.session_state.message_counter = 0
            st.rerun()

        if st.session_state.get("response_history"):
            st.markdown("### 💬 Recent Conversations")
            for idx, response in enumerate(st.session_state.response_history[::-1][:5]):
                if response.get("type") == "text":
                    with st.expander(f"🗨️ {response.get('prompt', '')[:20]}..."):
                        st.markdown(f"**You:** {response.get('prompt')[:50]}...")
                elif response.get("type") == "file":
                    with st.expander(f"📄 {response.get('filename', 'unknown')}"):
                        st.markdown(f"**Uploaded file:** {response.get('filename', 'unknown')}")

    if view_mode == "Chat Interface":
        # Display chat messages
        for idx, message in enumerate(st.session_state.chat_messages):
            with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
                st.write(message["content"])
                
                # Add audio player for assistant messages
                if message["role"] == "assistant" and len(message["content"]) > 50:
                    display_audio_player(message["content"], f"msg_{idx}")

        # File upload section
        uploaded_file = st.file_uploader(
            "Upload a medical document (optional)", 
            type=["jpg", "jpeg", "png", "pdf"], 
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            if st.button("📤 Process this file", use_container_width=True):
                st.session_state.message_counter += 1
                file_message = f"📄 Uploaded file: {uploaded_file.name}"
                st.session_state.chat_messages.append({"role": "user", "content": file_message})
                
                with st.chat_message("user", avatar="👤"):
                    st.write(file_message)

                with st.chat_message("assistant", avatar="🤖"):
                    thinking_placeholder = st.empty()
                    for i in range(3):
                        thinking_placeholder.write("Processing" + "." * (i + 1))
                        time.sleep(0.5)

                    with st.spinner("Processing your file..."):
                        try:
                            from database import SupabaseClient
                            base = SupabaseClient()
                            client_db = base.client
                            res = client_db.table('medical_info').select('id').eq('user_id', st.session_state['user_id']).execute()
                            ids = [item['id'] for item in res.data]

                            response = requests.post(
                                web_url,
                                files={'data': (uploaded_file.name, uploaded_file, uploaded_file.type)},
                                data={'name': uploaded_file.name, "id": ids, "userId": st.session_state['user_id']},
                            )

                            if response.status_code == 200:
                                extracted_text = response.text
                                
                                if not extracted_text or len(extracted_text.strip()) == 0:
                                    extracted_text = "File processed successfully, but no text content was extracted."

                                st.session_state.response_history.append({
                                    "type": "file",
                                    "filename": uploaded_file.name,
                                    "response": extracted_text
                                })

                                message = f"I've processed your file '{uploaded_file.name}'. Here's what I extracted:\n\n{extracted_text}\n\n(Use the chat input below to ask me questions about this document)"
                                st.session_state.chat_messages.append({"role": "assistant", "content": message})

                                try:
                                    client_db.table('medicalinfo').insert({
                                        'user_id': st.session_state['user_id'],
                                        'content': extracted_text
                                    }).execute()
                                except Exception as e:
                                    st.error(f"❌ Database error: {str(e)}")

                                thinking_placeholder.write(message)
                                
                                # Add audio player for the response
                                display_audio_player(message, f"file_{st.session_state.message_counter}")
                                
                            else:
                                error_msg = f"Error processing file (Status: {response.status_code}). Please try again."
                                thinking_placeholder.write(error_msg)
                                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})

                        except requests.exceptions.Timeout:
                            error_msg = "❌ Request timed out. Please try again with a smaller file."
                            thinking_placeholder.write(error_msg)
                            st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                        except Exception as e:
                            error_msg = f"❌ An error occurred: {str(e)}"
                            thinking_placeholder.write(error_msg)
                            st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})

                st.rerun()

        # Chat input
        if prompt := st.chat_input("Ask your health question here..."):
            st.session_state.message_counter += 1
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user", avatar="👤"):
                st.write(prompt)

            with st.chat_message("assistant", avatar="🤖"):
                thinking_placeholder = st.empty()
                for i in range(3):
                    thinking_placeholder.write("Thinking" + "." * (i + 1))
                    time.sleep(0.3)

                with st.spinner("Getting your answer..."):
                    try:
                        response = requests.post(
                            web_url,
                            json={'chatInput': prompt, "userId": st.session_state['user_id']},
                            timeout=30
                        )

                        if response.status_code == 200:
                            response_text = response.text
                            if not response_text or len(response_text.strip()) == 0:
                                response_text = "I apologize, but I couldn't generate a response. Please try rephrasing your question."

                            st.session_state.response_history.append({
                                "type": "text",
                                "prompt": prompt,
                                "response": response_text
                            })

                            st.session_state.chat_messages.append({"role": "assistant", "content": response_text})
                            thinking_placeholder.write(response_text)
                            
                            # Add audio player for the response
                            display_audio_player(response_text, f"chat_{st.session_state.message_counter}")
                            
                        else:
                            error_msg = f"❌ Server error (Status: {response.status_code}). Please try again."
                            thinking_placeholder.write(error_msg)
                            st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})

                    except requests.exceptions.Timeout:
                        error_msg = "❌ Request timed out. Please try again."
                        thinking_placeholder.write(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                    except Exception as e:
                        error_msg = f"❌ An error occurred: {str(e)}"
                        thinking_placeholder.write(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})

            st.rerun()
    else:
        display_chat_history(st.session_state['user_id'])

def main():
    # Initialize session state
    initialize_session_state()
    
    # Set up the page
    st.set_page_config(
        page_title="Swasthya AI",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Cleanup temporary files on app start
    if 'app_started' not in st.session_state:
        cleanup_temp_files()
        st.session_state['app_started'] = True
    
    # Display user info in sidebar
    show_user_info()
    
    # Main content
    if not st.session_state['logged_in']:
        # Show tabs for login and registration
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            user_id = login_page()
        with tab2:
           register_page()
    else:
        # Determine which page to show based on session state
        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = 'dashboard'
        
        # Initialize response history if not exists
        if 'response_history' not in st.session_state:
            st.session_state.response_history = []
        
        # Add navigation to sidebar for logged-in users
        with st.sidebar:
            st.markdown("---")
            st.subheader("Navigation")
                    
            if st.button("Dashboard", use_container_width=True):
                cleanup_temp_files()
                st.session_state['current_page'] = 'dashboard'
                st.rerun()
                        
            if st.button("Update Profile", use_container_width=True):
                cleanup_temp_files()
                st.session_state['current_page'] = 'profile'
                st.rerun()
            
            if st.button("Emotional Diary", use_container_width=True):
                cleanup_temp_files()
                st.session_state['current_page'] = 'emotional_diary'
                st.rerun()
            
            if st.button("Chatbot", use_container_width=True):
                st.session_state['current_page'] = 'chatbot'
                st.rerun()
                        
            if st.button("Logout", use_container_width=True):
                cleanup_temp_files()
                logout()
                st.rerun()
        
        # Display the appropriate page based on session state
        if st.session_state['current_page'] == 'dashboard':
            display_dashboard()
        elif st.session_state['current_page'] == 'profile':
            display_profile_update()
        elif st.session_state['current_page'] == 'emotional_diary':
            display_emotional_diary()
        elif st.session_state['current_page'] == 'chatbot':
            display_chatbot()

if __name__ == "__main__":
    main()
