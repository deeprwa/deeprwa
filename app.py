import streamlit as st
import requests
import json
import os

# Set page configuration
st.set_page_config(
    page_title="DeepRWA - AI Assistant for Rwanda",
    page_icon="🇷🇼",
    layout="wide"
)

# Custom CSS for better appearance
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .stButton > button {
        background-color: #1E88E5;
        color: white;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #1565C0;
        color: white;
    }
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm DeepRWA, your AI assistant specialized in Rwanda. How can I help you today?"}
    ]

if "new_chat" not in st.session_state:
    st.session_state.new_chat = False

# Title and description
st.title("🇷🇼 DeepRWA")
st.caption("Your AI assistant for Rwanda. Where should we start right now?")

# Sidebar for chat management
with st.sidebar:
    st.header("Chat Management")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm DeepRWA, your AI assistant specialized in Rwanda. How can I help you today?"}
        ]
        st.session_state.new_chat = True
        st.rerun()
    
    if st.button("🗑️ Delete All Chats", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm DeepRWA, your AI assistant specialized in Rwanda. How can I help you today?"}
        ]
        st.rerun()
    
    st.divider()
    
    # Display chat history count
    st.info(f"📝 {len([m for m in st.session_state.messages if m['role'] == 'user'])} messages in this chat")
    
    st.divider()
    
    # About the agent
    st.markdown("### About DeepRWA")
    st.markdown("""
    **Created by:** Emmanuel Mukiza  
    **Company:** The Star🌟  
    **Purpose:** Providing accurate information about Rwanda
    """)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# The system prompt for DeepRWA
SYSTEM_PROMPT = """You are DeepRWA, a professional AI assistant specialized only in information about Rwanda.

**About Me:**
- I was created by Emmanuel Mukiza, a Rwandan national, under his developing company "The Star🌟".
- The Star🌟 was launched on August 8, 2023, and is a two-person team dedicated to innovation and technology.
- Emmanuel graduated from Karenge Adventist Secondary School (KASS) with an Advanced Level (A-level) certificate in Computer System and Architecture (CSA). CSA is a combination that focuses on understanding both the hardware and software components of computer systems, including topics like computer architecture, operating systems, and system design.
- He is passionate about technology, AI systems, and both technical and soft skills (hardware and software). His goal is to understand how technology works globally and to participate in solving real-world problems.
- He aims to pursue a career in AI and contribute to Rwanda's development on a global scale.
- He created DeepRWA to make information about Rwanda easily accessible to everyone, including Rwandans, foreigners, and visitors, so that anyone can have accurate information about the country.

**Your Core Rule:**
- You must ONLY answer questions related to Rwanda.
- If a user asks about any other country or topic, you must politely and clearly state that you are a specialist on Rwanda and cannot answer questions about other topics.

**Your Main Topics:**
1.  **Location Finder:** Provide accurate information on Rwanda's provinces, districts, sectors, cells, and villages.
2.  **Product & Price Finder:** Share information on where to find specific products in Rwanda and their typical price ranges.
3.  **Famous People:** Provide biographies and information about notable Rwandans in entertainment, politics, sports, and history.
4.  **History & Culture:** Provide detailed, factual information on Rwanda's history, from kingdoms to the present, and its rich cultural traditions.
5.  **Tourism & Travel:** Provide information about tourist attractions, national parks (e.g., Volcanoes National Park, Nyungwe Forest), and general travel tips for visitors to Rwanda.
6.  **Events & News:** Share information about current events, upcoming festivals, and major news happening in Rwanda.

**Rules for Your Responses:**
- Always prioritize factual accuracy. Use your knowledge to provide accurate information.
- If you cannot find a definitive answer, politely tell the user you could not find the information.
- Be concise, clear, and easy to understand.
- Always maintain a respectful tone, especially on sensitive topics like Rwanda's history.
- For questions not related to Rwanda, politely state: "I am specialized only in topics about Rwanda. I cannot answer questions about other countries or topics."

**Social Media Policy:**
- You know Emmanuel's social media accounts, but you should only share them if a user specifically asks for them (e.g., "What are Emmanuel's social media accounts?").
- If a user asks for them, share the links:
    - YouTube: https://www.youtube.com/@Th_estarME
    - Instagram: https://www.instagram.com/mukiza_me/
    - Facebook: https://web.facebook.com/meMukiza
    - X (Twitter): https://x.com/mukiza_me
    - TikTok: https://www.tiktok.com/@the_star_mukiza
- For any other questions related to Emmanuel or The Star🌟, provide a clear and helpful answer without automatically including the social media links. However you can mention a if you want I can share his social medias after a user asked a related question."""

# Function to get AI response using free DeepSeek API
def get_ai_response(user_input):
    # Prepare the messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    
    # Add conversation history (last 10 messages for context)
    for msg in st.session_state.messages[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": user_input})
    
    try:
        # Use DeepSeek's free API (no key required for basic usage)
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer sk-..."  # Note: You may need a free key from DeepSeek
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
        else:
            # Fallback: Try a local response or a simpler API
            return get_fallback_response(user_input)
    
    except Exception as e:
        return get_fallback_response(user_input)

# Fallback response function (works without any API)
def get_fallback_response(user_input):
    # Simple keyword-based responses for common questions
    user_input_lower = user_input.lower()
    
    if "capital" in user_input_lower and "rwanda" in user_input_lower:
        return "The capital of Rwanda is **Kigali**. It is the country's political, economic, and cultural center."
    
    if "culture" in user_input_lower and "rwanda" in user_input_lower:
        return "Rwanda has a rich cultural heritage, including the traditional Intore dance, vibrant arts and crafts, and strong community values like Umuganda (community work)."
    
    if "paul kagame" in user_input_lower:
        return "Paul Kagame is the President of Rwanda. He has been a key figure in Rwanda's development and is known for his leadership in transforming the country."
    
    if "tourism" in user_input_lower or "tourist" in user_input_lower:
        return "Rwanda is famous for its mountain gorillas in Volcanoes National Park, the beautiful Lake Kivu, Nyungwe Forest National Park, and the Akagera National Park for wildlife safaris."
    
    if "business" in user_input_lower or "job" in user_input_lower:
        return "Rwanda offers various business opportunities in agriculture, technology, tourism, and services. The government is supportive of startups and innovation."
    
    if "history" in user_input_lower and "rwanda" in user_input_lower:
        return "Rwanda has a rich and complex history, from the ancient Kingdom of Rwanda to the colonial period, independence in 1962, the tragic genocide in 1994, and its remarkable recovery and development since then."
    
    if "emmanuel" in user_input_lower:
        return "Emmanuel Mukiza is a Rwandan technology enthusiast and the creator of DeepRWA. He founded The Star🌟, a two-person innovation and technology company, and is passionate about AI and technology."
    
    if "star" in user_input_lower:
        return "The Star🌟 is a Rwandan innovation and technology company founded by Emmanuel Mukiza on August 8, 2023. It is a two-person team dedicated to innovation and technology."
    
    # Check if the question is about Rwanda
    if "rwanda" in user_input_lower:
        return "I'm DeepRWA, your AI assistant for Rwanda. I can provide information about Rwanda's history, culture, tourism, provinces, famous people, and more. Please ask me a specific question about Rwanda!"
    
    # If the question is not about Rwanda
    return "I am specialized only in topics about Rwanda. I cannot answer questions about other countries or topics. Please ask me something about Rwanda!"

# Chat input
if prompt := st.chat_input("Ask me anything about Rwanda..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get AI response
    with st.spinner("Thinking..."):
        response = get_ai_response(prompt)
    
    # Add assistant response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to update the chat display
    st.rerun()
