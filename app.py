import streamlit as st
import requests
import json
from datetime import datetime
import base64
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="DeepRWA - AI Assistant for Rwanda",
    page_icon="🇷🇼",
    layout="wide"
)

# Custom CSS for professional look
st.markdown("""
    <style>
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 1200px;
    }
    
    /* Chat container */
    .stChatMessage {
        background-color: transparent !important;
    }
    
    .stChatMessage .stMarkdown {
        padding: 10px 15px;
        border-radius: 12px;
        margin: 5px 0;
    }
    
    /* User message */
    .stChatMessage[data-testid="user"] .stMarkdown {
        background-color: #1E88E5;
        color: white;
    }
    
    /* Assistant message */
    .stChatMessage[data-testid="assistant"] .stMarkdown {
        background-color: #f0f2f6;
        color: #1a1a1a;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    /* Chat input styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        padding: 12px 20px;
        font-size: 16px;
        border: 2px solid #e0e0e0;
    }
    .stTextInput > div > div > input:focus {
        border-color: #1E88E5;
        box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #1E88E5;
        color: white;
        border-radius: 20px;
        padding: 8px 20px;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1565C0;
        box-shadow: 0 2px 8px rgba(30, 136, 229, 0.3);
        transform: translateY(-1px);
    }
    
    /* Sidebar button styling */
    .sidebar .stButton > button {
        width: 100%;
        margin: 4px 0;
    }
    
    /* Chat container width */
    .stChatMessageContainer {
        max-width: 100% !important;
    }
    
    /* Message timestamp */
    .timestamp {
        font-size: 0.75rem;
        color: #888;
        margin-top: 2px;
        display: block;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "chats" not in st.session_state:
    st.session_state.chats = {}
    
if "current_chat_id" not in st.session_state:
    import uuid
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.chats[st.session_state.current_chat_id] = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# System prompt
SYSTEM_PROMPT = """You are DeepRWA, a professional AI assistant specialized in Rwanda.

**About Me:**
- Created by Emmanuel Mukiza under his company "The Star🌟"
- Emmanuel graduated from Karenge Adventist Secondary School (KASS) with an Advanced Level certificate in Computer System and Architecture (CSA)
- He is passionate about technology, AI systems, and solving real-world problems
- DeepRWA makes information about Rwanda easily accessible to everyone

**Your Core Rule:**
- You must ONLY answer questions related to Rwanda.
- For questions about greetings, emotions, or personal matters, respond warmly but remind the user of your Rwanda focus.
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
- For greetings, respond with a warm welcome
- For personal questions, respond naturally but steer towards Rwanda topics
- Always maintain a respectful tone
- Be concise and clear

**Social Media Policy:**
- Share Emmanuel's social media only when specifically asked however you can suggest to provide it for related users' questions:
  - YouTube: https://www.youtube.com/@Th_estarME
  - Instagram: https://www.instagram.com/mukiza_me/
  - Facebook: https://web.facebook.com/meMukiza
  - X: https://x.com/mukiza_me
  - TikTok: https://www.tiktok.com/@the_star_mukiza"""

def get_ai_response(user_input, chat_history):
    # Prepare messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add chat history (last 20 messages for context)
    for msg in chat_history[-20:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": user_input})
    
    # Try free API first
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
    
    # Greetings
    if any(word in user_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
        return "Hello! 😊 I'm DeepRWA, your AI assistant for Rwanda. How can I help you explore Rwanda today?"
    
    if "how are you" in user_lower:
        return "I'm doing great, thank you for asking! 😊 I'm always happy to help with questions about Rwanda. What would you like to know?"
    
    if "thank" in user_lower:
        return "You're very welcome! 😊 Feel free to ask me anything else about Rwanda."
    
    if "who are you" in user_lower:
        return "I'm DeepRWA, your AI assistant specialized in Rwanda! 🇷🇼 I was created by Emmanuel Mukiza to help people learn about Rwanda's culture, history, tourism, and more."
    
    # Rwanda topics
    if "capital" in user_lower:
        return "The capital of Rwanda is **Kigali**! 🇷🇼 It's the country's political, economic, and cultural center."
    
    if "culture" in user_lower:
        return "Rwanda has a rich cultural heritage! 🎭 Traditional Intore dance, vibrant arts and crafts, and community values like Umuganda (community work) are central to Rwandan culture."
    
    if "paul kagame" in user_lower:
        return "Paul Kagame is the President of Rwanda. He has been instrumental in Rwanda's remarkable development and transformation since 1994."
    
    if "tourism" in user_lower or "tourist" in user_lower:
        return "Rwanda is famous for its mountain gorillas in Volcanoes National Park, beautiful Lake Kivu, Nyungwe Forest, and Akagera National Park for wildlife safaris! 🦍"
    
    if "business" in user_lower:
        return "Rwanda offers great business opportunities in agriculture, technology, tourism, and services. The government is very supportive of startups and innovation! 💼"
    
    if "history" in user_lower:
        return "Rwanda has a complex and rich history, from the ancient Kingdom of Rwanda to independence in 1962, and its remarkable recovery and development since 1994."
    
    if "emmanuel" in user_lower or "creator" in user_lower:
        return "Emmanuel Mukiza is a Rwandan technology enthusiast and the creator of DeepRWA. He founded The Star🌟 to innovate and contribute to Rwanda's development!"
    
    if "star" in user_lower:
        return "The Star🌟 is Emmanuel Mukiza's innovation and technology company, focused on creating solutions that contribute to Rwanda's development."
    
    # Check if question is about Rwanda
    if "rwanda" in user_lower:
        return "I'm here to help with anything about Rwanda! 🇷🇼 Feel free to ask me about its culture, history, tourism, famous people, or any specific topic you're curious about."
    
    # Default responses
    return "I'm DeepRWA, specialized in Rwanda 🇷🇼 I can help you with Rwandan culture, history, tourism, famous people, and more. What would you like to know about Rwanda?"

# Sidebar
with st.sidebar:
    # Use your uploaded image
    st.image("av.png", use_container_width=True)
    
    st.markdown("### 💬 Chats")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("📝 New Chat", use_container_width=True):
            import uuid
            new_id = str(uuid.uuid4())
            st.session_state.current_chat_id = new_id
            st.session_state.chats[new_id] = []
            st.rerun()
    with col2:
        if st.button("🗑️", help="Delete current chat"):
            if st.session_state.current_chat_id in st.session_state.chats:
                del st.session_state.chats[st.session_state.current_chat_id]
                if st.session_state.chats:
                    st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                else:
                    import uuid
                    new_id = str(uuid.uuid4())
                    st.session_state.current_chat_id = new_id
                    st.session_state.chats[new_id] = []
                st.rerun()
    
    st.divider()
    
    # Display chat list
    for chat_id, messages in st.session_state.chats.items():
        first_msg = "New Chat"
        for msg in messages:
            if msg["role"] == "user":
                first_msg = msg["content"][:30] + ("..." if len(msg["content"]) > 30 else "")
                break
        timestamp = datetime.now().strftime("%H:%M")
        if st.button(f"💬 {first_msg} ({timestamp})", key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()
    
    st.divider()
    
    st.markdown("---")
    st.caption("🇷🇼 DeepRWA - Your AI Assistant for Rwanda")

# Main chat area
st.title("🇷🇼 DeepRWA")

# Get current chat messages
if st.session_state.current_chat_id not in st.session_state.chats:
    import uuid
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.chats[st.session_state.current_chat_id] = []

current_messages = st.session_state.chats[st.session_state.current_chat_id]

# Display chat messages
if current_messages:
    for message in current_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")
else:
    # Welcome message
    with st.chat_message("assistant"):
        st.markdown("Hello! 😊 I'm **DeepRWA**, your AI assistant for Rwanda. I'm here to help you discover Rwanda's culture, history, tourism, and more. What would you like to know?")
        st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")

# Chat input
if prompt := st.chat_input("Ask me anything about Rwanda..."):
    # Add user message
    user_message = {"role": "user", "content": prompt}
    current_messages.append(user_message)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_ai_response(prompt, current_messages)
            st.markdown(response)
            st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")
    
    # Add assistant message
    assistant_message = {"role": "assistant", "content": response}
    current_messages.append(assistant_message)
    
    # Save to session
    st.session_state.chats[st.session_state.current_chat_id] = current_messages
    
    st.rerun()
