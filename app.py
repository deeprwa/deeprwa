import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# ============ PAGE CONFIGURATION ============
st.set_page_config(
    page_title="DeepRWA",
    page_icon="av.png",
    layout="wide"
)

# ============ GET API KEY FROM STREAMLIT CLOUD SECRETS ============
DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]

# ============ SESSION STATE ============
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.chats[st.session_state.current_chat_id] = []

# ============ SYSTEM PROMPT ============
SYSTEM_PROMPT = """You are DeepRWA, a professional AI assistant specialized in Rwanda.

**About You:**
- Created by Emmanuel Mukiza under his company "The Star🌟"
- Emmanuel graduated from Karenge Adventist Secondary School (KASS) with an Advanced Level certificate in Computer System and Architecture (CSA)

**Your Core Rule:**
- You must ONLY answer questions related to Rwanda.
- If a user asks about other countries, politely state you specialize in Rwanda.
- For greetings, respond warmly.

**Response Rules:**
- Be warm, friendly, and conversational
- Always maintain a respectful tone
- Be concise and clear
- Use the web search tool to find accurate, up-to-date information

**Social Media Policy:**
- Share Emmanuel's social media only when specifically asked:
  - YouTube: https://www.youtube.com/@Th_estarME
  - Instagram: https://www.instagram.com/mukiza_me/
  - Facebook: https://web.facebook.com/meMukiza
  - X: https://x.com/mukiza_me
  - TikTok: https://www.tiktok.com/@the_star_mukiza"""

# ============ AI RESPONSE FUNCTION ============
def get_ai_response(user_input, chat_history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for msg in chat_history[-20:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            },
            json={
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 800,
                "search": True,
                "search_options": {
                    "count": 3
                }
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# ============ SIDEBAR ============
with st.sidebar:
    st.image("av.png", width=40)
    st.markdown("### DeepRWA")
    
    if st.button("+ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_id
        st.session_state.chats[new_id] = []
        st.rerun()
    
    st.divider()
    
    if st.session_state.chats:
        for chat_id, messages in st.session_state.chats.items():
            if messages:
                first_msg = "New Chat"
                for msg in messages:
                    if msg["role"] == "user":
                        first_msg = msg["content"][:25] + ("..." if len(msg["content"]) > 25 else "")
                        break
                
                if st.button(f"💬 {first_msg}", key=f"chat_{chat_id}", use_container_width=True):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()

# ============ MAIN CHAT AREA ============
st.title("DeepRWA")
st.caption("Your AI assistant for Rwanda. Where should we start?")

if st.session_state.current_chat_id not in st.session_state.chats:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.chats[st.session_state.current_chat_id] = []

current_messages = st.session_state.chats[st.session_state.current_chat_id]

if current_messages:
    for message in current_messages:
        with st.chat_message(message["role"], avatar="av.png" if message["role"] == "assistant" else None):
            st.markdown(message["content"])

# ============ CHAT INPUT ============
if prompt := st.chat_input("Ask me anything about Rwanda..."):
    user_message = {"role": "user", "content": prompt}
    current_messages.append(user_message)
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="av.png"):
        with st.spinner("Searching..."):
            response = get_ai_response(prompt, current_messages)
            st.markdown(response)
    
    current_messages.append({"role": "assistant", "content": response})
    st.session_state.chats[st.session_state.current_chat_id] = current_messages
    st.rerun()
