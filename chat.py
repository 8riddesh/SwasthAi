#chat.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import streamlit as st
from database import SupabaseClient
import time


def initialize_llm():
    """Initialize the language model"""
    return Ollama(model="tinyllama")


def get_prompt_template():
    """Get the chat prompt template"""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "Provide a detailed answer to the question, mention the steps in points. "
                       "Consider the user's medical conditions when relevant."),
            ("user", "User has the following medical conditions: {medical_conditions}. "
                     "Previous conversation context: {conversation_context}. Question: {question}")
        ]
    )


def format_medical_conditions(user_id):
    """Get user's medical conditions as a formatted string"""
    db = SupabaseClient()
    medical_info = db.get_user_medical_info(user_id)

    if not medical_info:
        return "None specified"

    conditions = [info['condition_name'] for info in medical_info]
    return ", ".join(conditions)


def get_conversation_context(conversation_history, max_context=5):
    """Format the recent conversation history as context"""
    if not conversation_history:
        return "No previous context"

    # Get last few interactions to use as context
    recent_history = conversation_history[-max_context:]
    context_text = ""

    for entry in recent_history:
        context_text += f"User: {entry['question']}\nAssistant: {entry['answer']}\n\n"

    return context_text


def process_query(question, user_id):
    """Process the user query and get a response from the language model"""
    # Initialize chat history in session state if not present
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Get user's medical conditions
    medical_conditions = format_medical_conditions(user_id)

    # Get conversation context from session state
    db = SupabaseClient()
    conversation_history = db.get_chat_history(user_id)
    conversation_context = get_conversation_context(conversation_history)

    # Setup the language model chain
    llm = initialize_llm()
    prompt = get_prompt_template()
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    # Get response
    response = chain.invoke({
        "question": question,
        "medical_conditions": medical_conditions,
        "conversation_context": conversation_context
    })

    # Save the chat to the database
    db.save_chat(user_id, question, response)

    # Add to session state for immediate display
    st.session_state.chat_messages.append({"role": "user", "content": question})
    st.session_state.chat_messages.append({"role": "assistant", "content": response})

    return response


def display_chat_interface():
    """Display an interactive chat interface"""
    # Initialize chat history in session state if not present
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Display chat messages
    for message in st.session_state.chat_messages:
        if message["role"] == "user":
            st.chat_message("user", avatar="👤").write(message["content"])
        else:
            st.chat_message("assistant", avatar="🤖").write(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your health-related question here"):
        # Add user message to chat
        st.chat_message("user", avatar="👤").write(prompt)

        # Show thinking animation
        with st.chat_message("assistant", avatar="🤖"):
            thinking_placeholder = st.empty()
            for i in range(3):
                thinking_placeholder.write("Thinking" + "." * (i + 1))
                time.sleep(0.3)

            # Process the query
            with st.spinner(""):
                response = process_query(prompt, st.session_state['user_id'])

            # Replace thinking animation with response
            thinking_placeholder.write(response)


def load_chat_history(user_id):
    """Load chat history from database into session state"""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

        # Get chat history from database
        db = SupabaseClient()
        chat_history = db.get_chat_history(user_id)

        if chat_history:
            for chat in chat_history:
                st.session_state.chat_messages.append({"role": "user", "content": chat['question']})
                st.session_state.chat_messages.append({"role": "assistant", "content": chat['answer']})


def display_chat_history(user_id):
    """Display the user's chat history as expandable sections"""
    db = SupabaseClient()
    chat_history = db.get_chat_history(user_id)

    if not chat_history:
        st.info("No previous chats found.")
        return
    st.subheader("Chat History")

    for chat in chat_history:
        with st.expander(f"Q: {chat['question'][:50]}...", expanded=False):
            st.write("*Question:*")
            st.write(chat['question'])
            st.write("*Answer:*")
            st.write(chat['answer'])