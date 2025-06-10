import streamlit as st
import requests
import json
# Load API key from secrets
api_key = st.secrets["OPENROUTER_API_KEY"]
# Title and description
st.title("💬 Chatbot via OpenRouter")
st.write(
    "This chatbot uses OpenRouter"
    "You can get a free API key from openrouter.ai."
)
# Model selector
model_options = {
    "Mixtral 8x7B Instruct": "mistralai/mixtral-8x7b-instruct",
    "Claude 3 Haiku": "anthropic/claude-3-haiku",
    "LLaMA 3 70B Instruct": "meta-llama/llama-3-70b-instruct",
    "Gemma 7B IT": "google/gemma-7b-it",
    "Command R+": "cohere/command-r-plus"
}
selected_model_name = st.selectbox("Choose a model", list(model_options.keys()))
selected_model = model_options[selected_model_name]
# Temperature slider
temperature = st.slider("Response creativity (temperature)", 0.0, 1.5, 0.7, 0.1)
# System prompt input
system_prompt = st.text_area("System prompt (optional)", placeholder="You are a helpful assistant.")
# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    if system_prompt:
        st.session_state.messages.append({"role": "system", "content": system_prompt})
# Buttons for export and reset
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.experimental_rerun()
with col2:
    if st.download_button("💾 Export Chat", data=json.dumps(st.session_state.messages, indent=2),
                          file_name="chat_history.json", mime="application/json"):
        st.success("Chat exported!")
# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)
# Chat input
if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    try:
        # Prepare the request payload
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": selected_model,
            "messages": st.session_state.messages,
            "temperature": temperature
        }
        # Send request to OpenRouter
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        assistant_reply = response.json()["choices"][0]["message"]["content"]
        with st.chat_message("assistant"):
            st.markdown(assistant_reply, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    except Exception as e:
        st.error(f"An error occurred: {e}")