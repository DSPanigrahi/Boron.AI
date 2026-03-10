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
    # We wrap the query in a dictionary to satisfy the new 2026 Tavily requirements
search_results = search_tool.run({"query": user_text})
    
    # Then, we give that info to Gemini to explain it
    prompt = f"""
    # We use a "System" block to hard-code the identity so it doesn't hallucinate about Borno AI
    prompt_content = f"""
    SYSTEM: You are Boron.AI, a high-performance Research and Study Assistant. 
    You are NOT 'Borno AI' from Bangladesh. You were built by Shreyansh Panigrahi in 2026 to assist with 
    advanced academic research and fact-checking.
    
    CONTEXT FROM WEB: {search_results}
    CONVERSATION HISTORY: {history}
    
    USER QUESTION: {user_text}
    
    INSTRUCTIONS: Answer as Boron.AI. Be logical, professional, and use the web info provided.
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt # This is now explicitly defined so it CANNOT be empty
    )
    return response.text
# --- 4. SIDEBAR HISTORY ---
with st.sidebar:
    st.markdown("---")
    if st.button("📝 Create Study Guide"):
        if st.session_state.messages:
            # Combine all messages into one big text block
            context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            
            # Send a special prompt to Gemini
            guide_prompt = f"Based on this research: {context}. Create a structured study guide. Include: 1. Main Concepts, 2. Important Terms, 3. Summary of Findings."
            
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
                contents=[guide_prompt]
            )
            
            # Show the guide in a popup (expander)
            st.session_state.study_guide = response.text
        else:
            st.warning("Ask some questions first to build a history!")

# Display the guide if it exists
if "study_guide" in st.session_state:
    with st.expander("🎓 Your Generated Study Guide", expanded=True):
        st.write(st.session_state.study_guide)
        if st.button("Close Guide"):
            del st.session_state.study_guide
            st.rerun()
    st.title("📚 Research History")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    # Display a list of your questions as a quick reference
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            # Show the first 30 characters of each question
            st.write(f"🔍 {msg['content'][:30]}...")
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

with st.chat_message("assistant"):
        try:
            answer = get_boron_response(user_input)
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Operational Error: {e}")

# --- 5. THE STUDY GUIDE (PLACED AT BOTTOM) ---
# Putting this here ensures it appears AFTER the latest chat messages
if "study_guide" in st.session_state:
    st.divider() # Adds a nice visual line
    st.subheader("🎓 Your Generated Study Guide")
    st.markdown(st.session_state.study_guide)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Download as Text"):
            st.download_button("Click to Download", st.session_state.study_guide, file_name="study_guide.txt")
    with col2:
        if st.button("Close Guide"):
            del st.session_state.study_guide
            st.rerun()
