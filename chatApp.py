import streamlit as st
import ollama

# Configure page settings
st.set_page_config(page_title="Public AI Chatbot", page_icon="💬", layout="centered")
st.title("💬 Public Ollama Chat Application")

# 1. Configuration Sidebar for Public/Remote Server Use
# st.sidebar.header("Connection Settings")
ollama_host = st.sidebar.text_input(
    "Ollama Server URL", 
    value="http://localhost:11434",
    help="Point this to your public or local Ollama instance."
)

# Initialize the Ollama Client with the custom host
client = ollama.Client(host=ollama_host)

# Fetch available models dynamically
try:
    models_info = client.list()
    available_models = [model['model'] for model in models_info.get('models', [])]
except Exception:
    available_models = ["llama3", "mistral", "phi3"] # Fallbacks if server isn't reached yet

selected_model = st.sidebar.selectbox("Choose a Model", available_models)

# 2. Maintain Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Handle User Input
if user_input := st.chat_input("Type your message here..."):
    # Append and render user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate and stream response from Ollama
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Request streaming chat response from the client
            stream = client.chat(
                model=selected_model,
                messages=st.session_state.messages,
                stream=True
            )
            
            for chunk in stream:
                full_response += chunk['message']['content']
                response_placeholder.markdown(full_response + "▌")
                
            response_placeholder.markdown(full_response)
            
            # Save assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Failed to connect to Ollama: {str(e)}")
