import streamlit as st
import google.generativeai as genai
import os
import chat_model  # Imports your Service 1 file
import exam_model  # Imports your Service 2 file

# --- CONFIGURATION ---
st.set_page_config(page_title="Cognitive Mirror", page_icon="🧠", layout="wide")

# 1. API KEY SETUP
# We set it here so both modules can use it.
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDVd4w_ebl1Yn1uSRg3HfedXKzNMuzU7C0" # I added the key you provided

# 2. MODEL SETUP
# Use 'gemini-pro' or 'gemini-1.5-flash'
MODEL_NAME = "gemini-2.5-flash-lite"

# 3. Configure Google AI (Runs once)
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    st.error("⚠️ API Key Error.")
    st.stop()

# --- SIDEBAR & NAVIGATION ---
with st.sidebar:
    st.title("🧩 Navigation")
    # This button determines which file we "run"
    app_mode = st.radio("Choose Mode:", ["The Thinking Mirror", "Scenario Lab"])
    
    st.write("---")
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- MAIN ROUTING LOGIC ---
if app_mode == "The Thinking Mirror":
    # Call the function inside chat_model.py
    chat_model.run_chat_mode(MODEL_NAME)

elif app_mode == "Scenario Lab":
    # Call the function inside exam_model.py
    exam_model.run_exam_mode(MODEL_NAME)