import streamlit as st
import requests
import json
import time

# --- Page Config ---
st.set_page_config(page_title="OpenRouter Chatbot", page_icon="💬")

# --- CSS for Chat Bubbles ---
st.markdown("""
        <style>
.chat-container {
    display: flex;
    flex-direction: column;
    border-radius: 8px;
    padding: 1em;
}

.chat-bubble {
    max-width: 80%;
    padding: 0.8em 1.2em;
    margin: 0.5em 0;
    font-size: 1.05em;
    line-height: 1.5;
    color: #141311;
    background-color: #f9f9f9;
    border-radius: 1em;
    word-wrap: break-word;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.user-bubble {
    background-color: #DCF8C6;
    align-self: flex-end;
    margin-left: auto;
}

.assistant-bubble {
    background-color: #F1F0F0;
    color: #0a0801;
    align-self: flex-start;
    margin-right: auto;
}
</style>

""", unsafe_allow_html=True)

# --- Function to validate API key ---
def validate_api_key(api_key):
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistralai/mixtral-8x7b-instruct",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        return response.ok
    except:
        return False

# --- API Key Handling ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = False

# --- Ask for API Key ---
if not st.session_state.api_key_valid:
    with st.form("api_key_form"):
        user_key = st.text_input("🔐 Enter your OpenRouter API Key", type="password")
        submitted = st.form_submit_button("Submit")
        st.write("Get free API key from OpenRouter: https://openrouter.ai")
        if submitted:
            if user_key.strip():
                if validate_api_key(user_key.strip()):
                    st.session_state.api_key = user_key.strip()
                    st.session_state.api_key_valid = True
                    st.success("✅ API Key is valid. You can now start chatting!")
                    st.rerun()
                else:
                    st.error("❌ Invalid API Key. Please try again.")
            else:
                st.error("API Key cannot be empty.")

# --- Stop if no valid API key ---
if not st.session_state.api_key_valid:
    st.warning("Please enter a valid API key to continue.")
    st.stop()

# --- Main Chat UI ---
st.title("💬 Chatbot")

# --- Model Selection ---
model_options = {
    "Mixtral 8x7B Instruct": "mistralai/mixtral-8x7b-instruct",
    "Claude 3 Haiku": "anthropic/claude-3-haiku",
    "LLaMA 3 70B Instruct": "meta-llama/llama-3-70b-instruct",
    "Gemma 7B IT": "google/gemma-7b-it",
    "Command R+": "cohere/command-r-plus"
}
selected_model_name = st.selectbox("Choose a model", list(model_options.keys()))
selected_model = model_options[selected_model_name]

# --- Messages State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Clear & Export Buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Clear Chat"):
        st.session_state.clear()
        st.success("Chat cleared. Refresh to start again.")
        st.stop()
with col2:
    if st.download_button("💾 Export Chat", data=json.dumps(st.session_state.messages, indent=2),
                          file_name="chat_history.json", mime="application/json"):
        st.success("Chat exported!")

# --- Display Chat Bubbles ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    role_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
    st.markdown(f'<div class="chat-bubble {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Chat Input ---
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show user bubble
    st.markdown(f'<div class="chat-bubble user-bubble">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner("Assistant is typing..."):
        headers = {
            "Authorization": f"Bearer {st.session_state.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": selected_model,
            "messages": st.session_state.messages,
        }

        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            assistant_reply = response.json()["choices"][0]["message"]["content"]

            # Typing animation
            bubble_placeholder = st.empty()
            displayed_text = ""
            for char in assistant_reply:
                displayed_text += char
                bubble_placeholder.markdown(
                    f'<div class="chat-bubble assistant-bubble">{displayed_text}</div>', unsafe_allow_html=True
                )
                time.sleep(0.013)

            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            st.error(f"An error occurred: {e}")
