import streamlit as st
from google import genai
from langchain_community.tools.tavily_search import TavilySearchResults

# --- 1. BRANDING ---
st.set_page_config(page_title="Boron.AI", page_icon="🧪")
st.title("🧪 Boron.AI")

# --- 2. YOUR KEYS ---
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
TAVILY_KEY = st.secrets["TAVILY_API_KEY"]

# --- 3. THE BRAIN ---
# Using the direct Google GenAI SDK to avoid 'Contents are required' errors
client = genai.Client(api_key=GEMINI_KEY)
search_tool = TavilySearchResults(tavily_api_key=TAVILY_KEY)

def get_boron_response(user_text):
    # First, we check the web
    search_results = search_tool.run(user_text)
    
    # Then, we give that info to Gemini to explain it
    prompt = f"""
    You are Boron.AI. 
    Context from the web: {search_results}
    User Question: {user_text}
    
    Instructions: Use the web context to give a professional and logical answer.
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt # This is now explicitly defined so it CANNOT be empty
    )
    return response.text

# --- 4. CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if user_input := st.chat_input("Boron is steady. Ask me anything."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    with st.chat_message("assistant"):
        try:
            answer = get_boron_response(user_input)
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"System Error: {e}")
streamlit
langchain-google-genai
langchain-community
tavily-python
