import streamlit as st
from google import genai
from langchain_community.tools.tavily_search import TavilySearchResults
import uuid

# --- 1. BRANDING & SETUP ---
st.set_page_config(page_title="Boron.AI", page_icon="🧪", layout="wide")

# --- 2. KEYS (Use st.secrets for production!) ---
GEMINI_KEY = "KEY"
TAVILY_KEY = "KEY"

client = genai.Client(api_key=GEMINI_KEY)
search_tool = TavilySearchResults(tavily_api_key=TAVILY_KEY)

# --- 3. SESSION MANAGEMENT (MULTIPLE CHATS) ---
if "all_chats" not in st.session_state:
    # Dictionary to store multiple chats: {chat_id: {"name": str, "messages": list}}
    st.session_state.all_chats = {}

if "current_chat_id" not in st.session_state:
    # Create an initial chat
    new_id = str(uuid.uuid4())
    st.session_state.all_chats[new_id] = {"name": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🧪 Boron.AI")
    
    # 🆕 New Chat Button
    if st.button("➕ Create New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.all_chats[new_id] = {"name": f"Chat {len(st.session_state.all_chats)+1}", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()

    # 📂 Previous Chats Dropdown
    chat_options = {k: v["name"] for k, v in st.session_state.all_chats.items()}
    selected_chat = st.selectbox(
        "Select a Session", 
        options=list(chat_options.keys()), 
        format_func=lambda x: chat_options[x],
        index=list(chat_options.keys()).index(st.session_state.current_chat_id)
    )
    st.session_state.current_chat_id = selected_chat

    st.markdown("---")
    
    # 📝 Summarize Feature
    if st.button("📝 Summarize This Chat", use_container_width=True):
        messages = st.session_state.all_chats[st.session_state.current_chat_id]["messages"]
        if messages:
            chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            summary_prompt = f"Summarize the key points of this research session in bullet points:\n\n{chat_text}"
            summary_resp = client.models.generate_content(model="gemini-1.5-flash", contents=[summary_prompt])
            st.info(summary_resp.text)
        else:
            st.warning("No messages to summarize yet!")

# --- 5. THE BRAIN ---
def get_boron_response(user_text):
    # Fix: Tavily now requires a dictionary input
    try:
        search_results = search_tool.run({"query": user_text})
    except:
        search_results = "Web search currently unavailable."

    prompt_content = f"""
    You are Boron.AI, a research assistant created by Shreyansh Panigrahi.
    
    INSTRUCTIONS:
    - Use the 'Search Data' to answer. 
    - If the user asks who made you, name Shreyansh Panigrahi.
    - Be professional and concise.

    Search Data: {search_results}
    User Question: {user_text}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt_content]
    )
    return response.text

# --- 6. CHAT DISPLAY ---
st.title(f"💬 {st.session_state.all_chats[st.session_state.current_chat_id]['name']}")

# Load messages for the current chat
current_messages = st.session_state.all_chats[st.session_state.current_chat_id]["messages"]

for msg in current_messages:
    st.chat_message(msg["role"]).write(msg["content"])

if user_input := st.chat_input("Ask Boron anything..."):
    # Save user message
    current_messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Rename chat based on first question
    if len(current_messages) == 1:
        st.session_state.all_chats[st.session_state.current_chat_id]["name"] = user_input[:20] + "..."

    with st.chat_message("assistant"):
        try:
            answer = get_boron_response(user_input)
            st.write(answer)
            current_messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Error: {e}")
