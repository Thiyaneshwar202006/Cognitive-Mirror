import streamlit as st
import google.generativeai as genai
import os

# --- SYSTEM PROMPTS (Your exact original text) ---
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
    - Be supportive and non-judgmental. 
    """

# --- THE WRAPPER FUNCTION (Crucial for Option B) ---
def run_chat_mode(model_name):
    
    # 1. Configuration (We skip page_config to avoid errors)
    st.title("🧠 The Thinking Mirror")
    st.markdown("A space to understand *how* you solve problems.")

    # 2. Session Initialization (Renamed variables to avoid conflict with Exam Mode)
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_mode" not in st.session_state:
        st.session_state.chat_mode = "start"
        
        # Trigger the initial greeting
        try:
            model = genai.GenerativeModel(model_name)
            chat = model.start_chat(history=[])
            response = chat.send_message(f"{SYSTEM_PROMPT_CORE}\nMODE: start\nUser: Hello")
            st.session_state.chat_messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error starting AI: {e}")

    # 3. Display Chat History
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 4. User Input Area
    if prompt := st.chat_input("Type your response here..."):
        
        # Logic to switch modes
        if st.session_state.chat_mode == "start":
            st.session_state.chat_mode = "problem"
        elif st.session_state.chat_mode == "problem":
            st.session_state.chat_mode = "analyze"
        
        # Display User Message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build History for API
        history_for_model = []
        for msg in st.session_state.chat_messages:
            role = "user" if msg["role"] == "user" else "model"
            history_for_model.append({"role": role, "parts": [msg["content"]]})

        # Dynamic Instructions
        dynamic_instruction = get_ui_prompt(st.session_state.chat_mode)

        # Call Gemini
        try:
            model = genai.GenerativeModel(model_name) 
            with st.spinner("Thinking..."):
                chat = model.start_chat(history=history_for_model[:-1])
                response = chat.send_message(f"SYSTEM INSTRUCTION: {SYSTEM_PROMPT_CORE} \n {dynamic_instruction} \n USER MESSAGE: {prompt}")
                
                ai_text = response.text
                st.session_state.chat_messages.append({"role": "assistant", "content": ai_text})
                st.rerun()

        except Exception as e:
            st.error(f"Error communicating with AI: {e}")

    # 5. Control Panel for "Finish Session"
    if st.session_state.chat_mode == "analyze":
        st.write("---")
        st.info("The AI is analyzing your thought process.")
        if st.button("End Session & See Insights"):
            st.session_state.chat_mode = "final"
            
            # Trigger final report
            prompt = "I am finished. Please generate the insights now."
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            
            history_for_model = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.chat_messages]
            dynamic_instruction = get_ui_prompt("final")
            
            with st.spinner("Generating your reflection profile..."):
                try:
                    model = genai.GenerativeModel(model_name)
                    chat = model.start_chat(history=history_for_model[:-1])
                    response = chat.send_message(f"SYSTEM INSTRUCTION: {SYSTEM_PROMPT_CORE} \n {dynamic_instruction} \n USER MESSAGE: {prompt}")
                    st.session_state.chat_messages.append({"role": "assistant", "content": response.text})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.chat_mode == "final":
        if st.button("Start Over"):
            st.session_state.chat_messages = []
            st.session_state.chat_mode = "start"
            st.rerun()