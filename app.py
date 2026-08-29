import streamlit as st
import requests
import json
from datetime import datetime
import uuid
import base64
from pathlib import Path

# ============ PAGE CONFIGURATION ============
st.set_page_config(
    page_title="DeepRWA",
    page_icon="av.png",
    layout="wide"
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
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        max-width: 1000px;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f7f7f8;
        padding-top: 2rem !important;
        border-right: 1px solid #e5e5e5;
        width: 280px !important;
    }
    
    /* Sidebar toggle button */
    .st-emotion-cache-1rsv1bx {
        display: none !important;
    }
    
    /* Sidebar logo */
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 4px 16px 4px;
        border-bottom: 1px solid #e5e5e5;
        margin-bottom: 16px;
    }
    .sidebar-logo img {
        width: 28px;
        height: 28px;
        border-radius: 50%;
    }
    .sidebar-logo span {
        font-size: 18px;
        font-weight: 700;
        color: #1a1a1a;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: transparent !important;
        padding: 4px 0 !important;
    }
    
    .stChatMessage .stMarkdown {
        padding: 12px 16px;
        border-radius: 16px;
        margin: 2px 0;
        max-width: 85%;
        word-wrap: break-word;
        font-size: 15px;
        line-height: 1.6;
    }
    
    .stChatMessage[data-testid="user"] .stMarkdown {
        background-color: #1E88E5;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    
    .stChatMessage[data-testid="assistant"] .stMarkdown {
        background-color: #f0f2f6;
        color: #1a1a1a;
        border-bottom-left-radius: 4px;
    }
    
    /* Chat input */
    .stTextInput > div > div > input {
        border-radius: 25px;
        padding: 12px 20px;
        font-size: 15px;
        border: 1px solid #e5e5e5;
        background-color: white;
    }
    .stTextInput > div > div > input:focus {
        border-color: #1E88E5;
        box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
    }
    
    /* Timestamp */
    .timestamp {
        font-size: 0.7rem;
        color: #999;
        margin-top: 2px;
        display: block;
    }
    
    /* Sidebar button */
    .stButton > button {
        background-color: transparent;
        color: #1a1a1a;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 8px 12px;
        font-weight: 400;
        font-size: 14px;
        transition: all 0.2s ease;
        width: 100%;
        text-align: left;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .stButton > button:hover {
        background-color: #e5e5e5;
        border-color: #d1d1d1;
    }
    
    /* Chat list items */
    .chat-item {
        padding: 8px 12px;
        margin: 2px 0;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        color: #1a1a1a;
        border: none;
        background: transparent;
        width: 100%;
        text-align: left;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: background 0.2s;
    }
    .chat-item:hover {
        background-color: #e5e5e5;
    }
    .chat-item.active {
        background-color: #e5e5e5;
    }
    .chat-item .time {
        font-size: 11px;
        color: #999;
        margin-left: auto;
        white-space: nowrap;
    }
    
    /* New chat button style */
    .new-chat-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 16px;
        background-color: #e5e5e5;
        border-radius: 8px;
        font-weight: 500;
        color: #1a1a1a;
        cursor: pointer;
        transition: background 0.2s;
        border: none;
        width: 100%;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .new-chat-btn:hover {
        background-color: #d1d1d1;
    }
    
    /* Hide sidebar toggle */
    .st-emotion-cache-16idsys {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============ SESSION STATE ============
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.chats[st.session_state.current_chat_id] = []

# ============ SYSTEM PROMPT ============
SYSTEM_PROMPT = """You are DeepRWA, a professional AI assistant specialized in Rwanda.

**About Me:**
- Created by Emmanuel Mukiza under his company "The Star🌟"
- Emmanuel graduated from Karenge Adventist Secondary School (KASS) with an Advanced Level certificate in Computer System and Architecture (CSA)

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
- Use real web search results to provide accurate, up-to-date information
- Always verify facts before providing answers

**Social Media Policy:**
- Share Emmanuel's social media only when specifically asked:
  - YouTube: https://www.youtube.com/@Th_estarME
  - Instagram: https://www.instagram.com/mukiza_me/
  - Facebook: https://web.facebook.com/meMukiza
  - X: https://x.com/mukiza_me
  - TikTok: https://www.tiktok.com/@the_star_mukiza"""

# ============ WEB SEARCH FUNCTION ============
def search_web(query):
    """Search the web using a free API"""
    try:
        # Try DuckDuckGo API (free, no key required)
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            # Extract relevant information
            results = []
            if data.get("AbstractText"):
                results.append(data["AbstractText"])
            if data.get("RelatedTopics"):
                for topic in data["RelatedTopics"][:3]:
                    if "Text" in topic:
                        results.append(topic["Text"])
            if results:
                return " ".join(results[:3])
    except:
        pass
    
    return None

# ============ AI RESPONSE FUNCTION ============
def get_ai_response(user_input, chat_history):
    # First, try to search the web
    search_results = search_web(user_input)
    
    # Prepare messages for AI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add search results as context if available
    if search_results:
        context = f"Here is the latest search result information:\n{search_results}\n\nBased on this information, provide a clear and accurate answer to the user's question."
        messages.append({"role": "system", "content": context})
    
    for msg in chat_history[-20:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})
    
    # Try DeepSeek API
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
    
    # If search results exist, return them
    if search_results:
        return search_results
    
    # Final fallback - intelligent response
    user_lower = user_input.lower()
    
    # Check for specific Rwanda topics
    if "capital" in user_lower and "rwanda" in user_lower:
        return "The capital of Rwanda is **Kigali**. It is the country's political, economic, and cultural center."
    
    if "rwamagana" in user_lower:
        return "Rwamagana is a district located in the Eastern Province of Rwanda. It is known for being a commercial and administrative center."
    
    if "zeo trap" in user_lower:
        return "ZEO Trap is a Rwandan musician and artist known for his contributions to the Rwandan music scene."
    
    if "2010" in user_lower and "rwanda" in user_lower:
        return "In 2010, Rwanda experienced significant developments including economic growth, infrastructure projects, and progress in education and healthcare."
    
    if "rwanda" in user_lower:
        return "I'm here to help with anything about Rwanda! I can provide information about its culture, history, tourism, famous people, and more. What specific topic would you like to know?"
    
    return "I'm DeepRWA, specialized in Rwanda. I can help you with Rwandan culture, history, tourism, famous people, and more. What would you like to know about Rwanda?"

# ============ SIDEBAR ============
with st.sidebar:
    # Logo
    if Path("av.png").exists():
        with open("av.png", "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div class="sidebar-logo">
                <img src="data:image/png;base64,{img_data}" alt="DeepRWA">
                <span>DeepRWA</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="sidebar-logo">
                <span style="font-size:24px;font-weight:700;color:#1a1a1a;">DeepRWA</span>
            </div>
        """, unsafe_allow_html=True)
    
    # New Chat button
    if st.button("+ New Chat", key="new_chat_btn", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_id
        st.session_state.chats[new_id] = []
        st.rerun()
    
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    
    # Chat list
    if st.session_state.chats:
        for chat_id, messages in st.session_state.chats.items():
            if messages:
                first_msg = "New Chat"
                for msg in messages:
                    if msg["role"] == "user":
                        first_msg = msg["content"][:25] + ("..." if len(msg["content"]) > 25 else "")
                        break
                
                time_str = datetime.now().strftime("%I:%M %p")
                
                if chat_id == st.session_state.current_chat_id:
                    st.markdown(f"""
                        <button class="chat-item active">
                            💬 {first_msg}
                            <span class="time">{time_str}</span>
                        </button>
                    """, unsafe_allow_html=True)
                else:
                    if st.button(f"💬 {first_msg} ({time_str})", key=f"chat_{chat_id}", use_container_width=True):
                        st.session_state.current_chat_id = chat_id
                        st.rerun()

# ============ MAIN CHAT AREA ============
# Title with small avatar
col1, col2 = st.columns([0.5, 10])
with col1:
    if Path("av.png").exists():
        st.image("av.png", width=32)
with col2:
    st.title("DeepRWA")
    st.caption("Your AI assistant for Rwanda. Where should we start?")

st.divider()

# Get current chat messages
if st.session_state.current_chat_id not in st.session_state.chats:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.chats[st.session_state.current_chat_id] = []

current_messages = st.session_state.chats[st.session_state.current_chat_id]

# Display chat messages (no welcome message)
if current_messages:
    for idx, message in enumerate(current_messages):
        with st.chat_message(message["role"], avatar="av.png" if message["role"] == "assistant" else None):
            st.markdown(message["content"])
            st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")

# ============ CHAT INPUT ============
if prompt := st.chat_input("Ask me anything about Rwanda..."):
    # Add user message
    user_message = {"role": "user", "content": prompt}
    current_messages.append(user_message)
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")
    
    # Get AI response
    with st.chat_message("assistant", avatar="av.png"):
        with st.spinner("Searching and thinking..."):
            response = get_ai_response(prompt, current_messages)
            st.markdown(response)
            st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")
    
    # Add assistant message
    current_messages.append({"role": "assistant", "content": response})
    
    # Save to session
    st.session_state.chats[st.session_state.current_chat_id] = current_messages
    
    st.rerun()
