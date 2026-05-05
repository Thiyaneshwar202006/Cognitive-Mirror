import streamlit as st
import google.generativeai as genai
import scenarios

def run_exam_mode(model_name):
    st.header("🧪 Scenario Lab")
    st.markdown("Test your logic, lateral thinking, and ethics.")

    # 1. Initialize State
    if "exam_stage" not in st.session_state:
        st.session_state.exam_stage = "idle"
    if "current_scenario" not in st.session_state:
        st.session_state.current_scenario = None
    if "exam_messages" not in st.session_state:
        st.session_state.exam_messages = []

    # 2. Controls
    if st.button("Load New Challenge"):
        st.session_state.current_scenario = scenarios.get_random_scenario()
        st.session_state.exam_stage = "active"
        st.session_state.exam_messages = [] 
        st.rerun()

    # 3. Active View
    if st.session_state.exam_stage == "active" and st.session_state.current_scenario:
        sc = st.session_state.current_scenario
        st.info(f"**Type:** {sc['type']}")
        st.markdown(f"### {sc['text']}")
        st.write("---")

        # Display Chat
        for msg in st.session_state.exam_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Handle Input
        if ans := st.chat_input("Your answer..."):
            st.session_state.exam_messages.append({"role": "user", "content": ans})
            with st.chat_message("user"):
                st.markdown(ans)
            
            system_prompt = f"""
            You are an Examiner checking a student's answer to this scenario: "{sc['text']}".
            1. If clearly WRONG: Give a hint.
            2. If RIGHT: Challenge them with a "What if?" variation.
            """
            
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.exam_messages]
            
            with st.spinner("Grading..."):
                try:
                    model = genai.GenerativeModel(model_name)
                    chat = model.start_chat(history=history[:-1])
                    response = chat.send_message(f"SYSTEM: {system_prompt}\nUSER ANSWER: {ans}")
                    st.session_state.exam_messages.append({"role": "assistant", "content": response.text})
                    st.rerun()
                except Exception as e:
                    st.error(f"AI Error: {e}")

    elif st.session_state.exam_stage == "idle":
        st.write("👈 Click 'Load New Challenge' to begin.")