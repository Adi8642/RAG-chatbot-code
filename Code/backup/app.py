import streamlit as st
import requests
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Project Nova AI Assistant",
    page_icon="🤖",
    layout="centered"
)

# --- API Configuration ---
# IMPORTANT: Replace this with your actual OpenRouter API key
# You can get one for free at https://openrouter.ai/keys
OPENROUTER_API_KEY = "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" 

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "x-ai/grok-4-fast:free" # Or "deepseek/deepseek-chat"

# --- Core API Function ---
def get_deepseek_response(user_prompt):
    """
    Sends a prompt to the DeepSeek model via OpenRouter and returns the response.
    """
    if not OPENROUTER_API_KEY or "sk-or-v1-..." in OPENROUTER_API_KEY:
        return "Error: Please provide a valid OpenRouter API key."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    data = json.dumps({
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
    })

    try:
        response = requests.post(API_URL, headers=headers, data=data, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        response_data = response.json()
        
        if "choices" in response_data and len(response_data["choices"]) > 0:
            return response_data["choices"][0]["message"]["content"]
        else:
            return f"Error: Received an unexpected response format from the API.\n\n{response_data}"

    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to the API. Details: {e}"
    except json.JSONDecodeError:
        return f"Error: Failed to decode the API response. Response text: {response.text}"


# --- Streamlit UI ---

st.title("🤖 Project Nova AI Assistant")
st.caption("A simple chatbot powered by DeepSeek via OpenRouter.ai")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you with Project Nova today?"}
    ]

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input from chat input box
if prompt := st.chat_input("Ask a question about Project Nova..."):
    # Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response and display it
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_deepseek_response(prompt)
            st.markdown(response)
    
    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": response})