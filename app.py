import streamlit as st
import requests
import json
from datetime import datetime
import base64
from pathlib import Path
import uuid

# ============ PAGE CONFIGURATION ============
st.set_page_config(
    page_title="DeepRWA - AI Assistant for Rwanda",
    page_icon="av.png",  # Your custom favicon
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CUSTOM CSS ============
st.markdown("""
    <style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 1200px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: transparent !important;
        padding: 8px 0 !important;
    }
    
    .stChatMessage .stMarkdown {
        padding: 10px 16px;
        border-radius: 16px;
        margin: 4px 0;
        max-width: 80%;
        word-wrap: break-word;
    }
    
    /* User messages */
    .stChatMessage[data-testid="user"] .stMarkdown {
        background-color: #1E88E5;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    
    /* Assistant messages */
    .stChatMessage[data-testid="assistant"] .stMarkdown {
        background-color: #f0f2f6;
        color: #1a1a1a;
        border-bottom-left-radius: 4px;
    }
    
    /* Timestamp */
    .timestamp {
        font-size: 0.7rem;
        color: #999;
        margin-top: 2px;
        display: block;
        clear: both;
    }
    
    /* Chat input */
    .stTextInput > div > div > input {
        border-radius: 25px;
        padding: 12px 20px;
        font-size: 15px;
        border: 2px solid #e0e0e0;
        background-color: white;
    }
    .stTextInput > div > div > input:focus {
        border-color: #1E88E5;
        box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.15);
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #1E88E5;
        color: white;
        border-radius: 20px;
        padding: 8px 20px;
        font-weight: 500;
        border: none;
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #1565C0;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(30, 136, 229, 0.3);
    }
    
    /* Avatar in chat messages */
    .avatar-container {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        margin-bottom: 12px;
    }
    .avatar-img {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        object-fit: cover;
        flex-shrink: 0;
    }
    .avatar-img-small {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        object-fit: cover;
        flex-shrink: 0;
    }
    
    /* Sidebar avatar */
    .sidebar-avatar {
        display: block;
        margin: 0 auto 16px auto;
        width: 120px;
        border-radius: 50%;
        border: 3px solid #1E88E5;
        padding: 4px;
        background: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Chat list items */
    .chat-list-item {
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 10px;
        cursor: pointer;
        transition: background 0.2s ease;
        font-size: 0.9rem;
        background-color: transparent;
        border: none;
        text-align: left;
        width: 100%;
        color: #333;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .chat-list-item:hover {
        background-color: #e8f0fe;
    }
    .chat-list-item.active {
        background-color: #d2e3fc;
        font-weight: 500;
    }
    .chat-list-item .chat-time {
        font-size: 0.7rem;
        color: #888;
        margin-left: auto;
        white-space: nowrap;
    }
    
    /* Sidebar section titles */
    .sidebar-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 16px 0 8px 0;
        padding: 0 4px;
    }
    
    /* Divider */
    .sidebar-divider {
        margin: 12px 0;
        border: none;
        border-top: 1px solid #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# ============ SESSION STATE ============
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.chats[st.session_state.current_chat_id] = []
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1

# ============ SYSTEM PROMPT ============
SYSTEM_PROMPT = """You are DeepRWA, a professional AI assistant specialized in Rwanda.

**About Me:**
- Created by Emmanuel Mukiza under his company "The Star🌟"
- Emmanuel graduated from Karenge Adventist Secondary School (KASS) with an Advanced Level certificate in Computer System and Architecture (CSA)
- He is passionate about technology, AI systems, and solving real-world problems

**Your Core Rule:**
- You must ONLY answer questions related to Rwanda.
- For greetings, respond warmly but remind the user of your Rwanda focus.
- If a user asks about other countries, politely state you specialize in Rwanda.

**Your Main Topics:**
1. Location Finder: Provinces, districts, sectors, cells, villages
2. Product & Price Finder: Where to find products and price ranges
3. Famous People: Biographies of notable Rwandans
4. History & Culture: Rwanda's history and cultural traditions
5. Tourism & Travel: Tourist attractions, national parks, travel tips
6. Events & News: Current events and festivals in Rwanda

**Response Rules:**
- Be warm, friendly, and conversational
- Greet users cheerfully
- Always maintain a respectful tone
- Be concise and clear

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
                "Authorization": "Bearer sk-..."
            },
            json={
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except:
        pass
    
    # Fallback responses
    user_lower = user_input.lower()
    
    if any(word in user_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
        return "Hello! 👋 I'm DeepRWA, your AI assistant for Rwanda. How can I help you explore Rwanda today?"
    
    if "how are you" in user_lower:
        return "I'm doing great, thank you for asking! 😊 I'm always happy to help with questions about Rwanda."
    
    if "thank" in user_lower:
        return "You're very welcome! 😊 Feel free to ask me anything else about Rwanda."
    
    if "who are you" in user_lower:
        return "I'm DeepRWA, your AI assistant specialized in Rwanda! 🇷🇼 I was created by Emmanuel Mukiza to help people learn about Rwanda."
    
    if "capital" in user_lower:
        return "The capital of Rwanda is **Kigali**! 🇷🇼 It's the country's political, economic, and cultural center."
    
    if "culture" in user_lower:
        return "Rwanda has a rich cultural heritage! 🎭 Traditional Intore dance, vibrant arts and crafts, and community values like Umuganda are central to Rwandan culture."
    
    if "tourism" in user_lower or "tourist" in user_lower:
        return "Rwanda is famous for its mountain gorillas in Volcanoes National Park, beautiful Lake Kivu, Nyungwe Forest, and Akagera National Park! 🦍"
    
    if "emmanuel" in user_lower or "creator" in user_lower:
        return "Emmanuel Mukiza is a Rwandan technology enthusiast and the creator of DeepRWA. He founded The Star🌟 to innovate and contribute to Rwanda's development!"
    
    if "rwanda" in user_lower:
        return "I'm here to help with anything about Rwanda! 🇷🇼 Feel free to ask me about its culture, history, tourism, famous people, or any specific topic you're curious about."
    
    return "I'm DeepRWA, specialized in Rwanda 🇷🇼 I can help you with Rwandan culture, history, tourism, famous people, and more. What would you like to know about Rwanda?"

# ============ SIDEBAR ============
with st.sidebar:
    # Avatar in sidebar
    st.image("av.png", use_container_width=True, output_format="PNG")
    st.markdown("---")
    
    st.markdown("### 💬 Chats")
    
    # New Chat button
    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_id
        st.session_state.chats[new_id] = []
        st.session_state.chat_counter += 1
        st.rerun()
    
    st.divider()
    
    # Chat list
    if st.session_state.chats:
        for chat_id, messages in st.session_state.chats.items():
            first_msg = "New Chat"
            for msg in messages:
                if msg["role"] == "user":
                    first_msg = msg["content"][:25] + ("..." if len(msg["content"]) > 25 else "")
                    break
            
            chat_time = ""
            if messages:
                last_msg = messages[-1]
                chat_time = datetime.now().strftime("%I:%M %p")
            
            is_active = chat_id == st.session_state.current_chat_id
            label = f"💬 {first_msg} ({chat_time})" if chat_time else f"💬 {first_msg}"
            
            if st.button(label, key=f"chat_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.rerun()
    
    st.divider()
    st.caption("🇷🇼 DeepRWA · Your AI Assistant for Rwanda")

# ============ MAIN CHAT AREA ============
# Title with avatar in header
col1, col2 = st.columns([1, 12])
with col1:
    st.image("av.png", width=40)
with col2:
    st.title("DeepRWA")
    st.caption("Your AI assistant for Rwanda")

st.divider()

# Get current chat messages
if st.session_state.current_chat_id not in st.session_state.chats:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.chats[st.session_state.current_chat_id] = []

current_messages = st.session_state.chats[st.session_state.current_chat_id]

# Display chat messages
if current_messages:
    for idx, message in enumerate(current_messages):
        with st.chat_message(message["role"], avatar="av.png" if message["role"] == "assistant" else None):
            st.markdown(message["content"])
            # Add timestamp for each message (only show for the last 3 messages to avoid clutter)
            if idx >= len(current_messages) - 5:
                st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")
else:
    # Welcome message
    with st.chat_message("assistant", avatar="av.png"):
        st.markdown("Hello! 👋 I'm **DeepRWA**, your AI assistant for Rwanda. I'm here to help you discover Rwanda's culture, history, tourism, and more. What would you like to know?")
        st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")

# ============ CHAT INPUT ============
if prompt := st.chat_input("Ask me anything about Rwanda..."):
    # Add user message
    user_message = {"role": "user", "content": prompt, "timestamp": datetime.now().isoformat()}
    current_messages.append(user_message)
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")
    
    # Get AI response
    with st.chat_message("assistant", avatar="av.png"):
        with st.spinner("Thinking..."):
            response = get_ai_response(prompt, current_messages)
            st.markdown(response)
            st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")
    
    # Add assistant message
    assistant_message = {"role": "assistant", "content": response, "timestamp": datetime.now().isoformat()}
    current_messages.append(assistant_message)
    
    # Save to session
    st.session_state.chats[st.session_state.current_chat_id] = current_messages
    
    st.rerun()
