import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURATION ---
# Ideally, store this in a .env file or Streamlit secrets
# For local testing, you can hardcode it (not recommended for production) or use os.environ
os.environ["GOOGLE_API_KEY"] = "AIzaSyDvJ2KT_0wmTd_5vUOIp3qt6xqdAtzFTvE"

# Configure Gemini
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    st.error("⚠️ Google API Key missing. Please set GOOGLE_API_KEY in your environment variables.")
    st.stop()

# --- SYSTEM PROMPTS ---

SYSTEM_PROMPT_CORE = """
You are the AI reasoning layer of a web-based application designed to help students and early-career professionals understand how they think.
This system is for self-awareness and growth, NOT evaluation.

--------------------------------WHAT YOU ARE
- A pattern observer
- A reflection guide
- A human-centered insight generator

--------------------------------WHAT YOU ARE NOT
- A judge
- A recruiter
- A therapist
- A diagnostic system

--------------------------------ETHICAL RULES (MANDATORY)
1. Never diagnose mental or emotional conditions.
2. Never assign fixed labels, scores, or types.
3. Never predict success or failure.
4. Never compare users with others.
5. Insights apply ONLY to this session.

--------------------------------ROLE OF AI
You observe patterns in: reasoning structure, clarity vs hesitation, emotional tone, adaptation.
You do NOT evaluate correctness.

--------------------------------OUTPUT RULES
- Use simple words.
- Avoid psychology jargon.
- Avoid absolute statements.
- Use phrases like: "you seem to…", "in this situation…", "this may suggest…"

--------------------------------FINAL OUTPUT STRUCTURE (Only for 'final' mode)
1. How You Tend to Think
2. How Emotions Show Up While Solving Problems
3. How You Handle Pressure and Uncertainty
4. Where Your Creativity or Strengths Appear
5. Environments That May Suit You Better
6. Growth Suggestions
"""

def get_ui_prompt(mode):
    """Generates the dynamic instructions based on the current mode."""
    return f"""
    MODE: {mode}

    USER TYPE: Student or early-career professional
    SESSION TYPE: Deep real-world problem solving
    LANGUAGE STYLE: Simple words with multi-layer meaning

    --------------------------------INSTRUCTIONS FOR CURRENT MODE
    If MODE = "start":
    - Explain what this session is and what it is NOT (short, calm, friendly).
    - Ask if the user is ready to begin.

    If MODE = "problem":
    - Present ONE real-world scenario related to study or early-career work.
    - Start simple, then gradually add uncertainty.
    - Ask only one question.

    If MODE = "analyze":
    - Acknowledge the user’s response briefly.
    - Ask a deeper or follow-up question to probe their thinking process.
    - Do NOT reveal analysis yet.

    If MODE = "final":
    - Generate insights using the fixed FINAL OUTPUT STRUCTURE in the system prompt.
    - Keep language simple but meaningful.
    - Be supportive and non-judgmental . 
    """

# --- APP LOGIC ---

def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "mode" not in st.session_state:
        st.session_state.mode = "start"
        # Trigger the initial greeting from AI
        get_ai_response(user_input="Hello, please start the session.", override_mode="start")

def get_ai_response(user_input, override_mode=None):
    """Communicates with Gemini, sending the history + system prompt + mode instructions."""
    
    current_mode = override_mode if override_mode else st.session_state.mode
    
    # 1. Build the History for the API
    # We convert Streamlit's chat history into the format Gemini expects
    history_for_model = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        history_for_model.append({"role": role, "parts": [msg["content"]]})
    
    # 2. Construct the full prompt
    # We combine the Core System Prompt + The Dynamic UI Prompt + The User's latest input
    dynamic_instruction = get_ui_prompt(current_mode)
    
    full_prompt_structure = [
        SYSTEM_PROMPT_CORE,
        dynamic_instruction,
        f"User Input: {user_input}"
    ]

    # 3. Call Gemini
    model = genai.GenerativeModel('gemini-2.5-flash') # Or gemini-pro
    
    try:
        # If it's the very first message, we just send the prompt. 
        # Otherwise, we might want to use chat_session, but for tight control over the 'Mode',
        # passing the history manually + system instruction often works better for state machines.
        
        # Simpler approach: Send history + new prompt
        chat = model.start_chat(history=history_for_model)
        response = chat.send_message(f"SYSTEM INSTRUCTION: {SYSTEM_PROMPT_CORE} \n {dynamic_instruction} \n USER MESSAGE: {user_input}")
        
        ai_text = response.text
        
        # 4. Update Streamlit State
        if not override_mode: # Don't duplicate the user input for the hidden start trigger
            st.session_state.messages.append({"role": "user", "content": user_input})
            
        st.session_state.messages.append({"role": "assistant", "content": ai_text})
        
        return ai_text

    except Exception as e:
        st.error(f"Error communicating with AI: {e}")
        return None

# --- UI LAYOUT ---

st.set_page_config(page_title="Metacognition Mirror", page_icon="🧠")

st.title("🧠 The Thinking Mirror")
st.markdown("A space to understand *how* you solve problems.")

init_session()

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Area
if prompt := st.chat_input("Type your response here..."):
    
    # Logic to switch modes based on flow
    if st.session_state.mode == "start":
        st.session_state.mode = "problem"
    elif st.session_state.mode == "problem":
        st.session_state.mode = "analyze"
    
    # Get AI Response
    get_ai_response(prompt)
    st.rerun()

# Control Panel for "Finish Session"
if st.session_state.mode == "analyze":
    st.write("---")
    st.info("The AI is analyzing your thought process. Continue answering questions, or click below when you want your insights.")
    if st.button("End Session & See Insights"):
        st.session_state.mode = "final"
        # Trigger the final report generation
        with st.spinner("Generating your reflection profile..."):
            get_ai_response("I am finished. Please generate the insights now.")
        st.rerun()

if st.session_state.mode == "final":
    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()