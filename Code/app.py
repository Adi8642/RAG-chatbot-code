# app.py

import streamlit as st
from rag_engine import RAG_Engine

# --- Page Configuration ---
st.set_page_config(
    page_title="Project Nova AI Assistant",
    page_icon="🤖",
    layout="centered"
)

# --- State Management and Engine Initialization ---

# This is the core of the new setup. 
# @st.cache_resource ensures the RAG_Engine is loaded only ONCE.
# This prevents re-loading the PDF and re-building the vector store every time the user asks a question.
@st.cache_resource
def load_rag_engine():
    """Loads the RAG Engine and caches it."""
    try:
        engine = RAG_Engine("project_nova_brief.pdf")
        return engine
    except FileNotFoundError:
        return None

# Load the engine
engine = load_rag_engine()

# --- Streamlit UI ---

st.title("🤖 Project Nova AI Assistant")
st.caption("This chatbot uses RAG to answer questions from the project brief.")

if engine is None:
    st.error("The knowledge base file 'project_nova_brief.pdf' was not found. Please add it to the same folder as this script and restart.")
else:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I have studied the Project Nova brief. How can I help you?"}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get user input
    if prompt := st.chat_input("Ask about the project timeline, team, or tech stack..."):
        # Add user message to history and display
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response using the RAG engine
        with st.chat_message("assistant"):
            with st.spinner("Searching the document and thinking..."):
                response = engine.query(prompt)
                st.markdown(response)
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})