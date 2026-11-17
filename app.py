# ---------- VINCI AI - JTEG PANEL ----------
st.divider()
st.header("🤖 V.I.N.C.I. - Josiah Technologies and Engineering Group AI")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello Boss, I am VINCI. Talk to me - I can design, research, generate images and control VinciCAD by voice. Try: 'Make a 32 teeth gear'"}]

# Show chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Voice + Text Input
# For voice, install: pip install streamlit-mic-recorder
# from streamlit_mic_recorder import mic_recorder
# audio = mic_recorder(start_prompt="🎤 Hold to Talk to VINCI", key="vinci_mic")
# If audio, use Whisper to convert to text

user_input = st.chat_input("Talk to VINCI... e.g. 'Make a 32 teeth gear, 60mm'")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Simple Brain - In V2, replace this with Groq / Gemini API + Tool Calling
    low = user_input.lower()
    if "32 teeth" in low or "make a gear" in low:
        reply = "Done boss. I don set gear to 32 teeth, 60mm diameter. I don rebuild am for you. Want me to export STL?"
        # Here AI would call set_gear_params(32, 60, 8, 10)
    elif "buck" in low:
        reply = "Buck converter designed: 12V to 5V, Duty 41.6%. Use XL4015, 33uH inductor, 470uF capacitor. I don add am to Board Mode."
    elif "research" in low:
        reply = "Deep research started... I search web for best buck converter IC. Result: XL4015 is best for 5A, LM2596 is best for learning. Full report dey for Research tab."
    elif "image" in low:
        reply = "Generating image of futuristic gear... Done. Check Gallery. E go be good for your presentation."
    else:
        reply = f"I hear you boss: '{user_input}'. In full version, I go use Groq AI to understand and control the app. For now, try 'Make a gear' or 'Design buck converter'."

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# Voice toggle
st.caption("🎤 Voice: Hold mic button to talk to VINCI. VINCI go reply with voice using gTTS. Works on phone Chrome.")
st.caption("🔍 Deep Research: VINCI uses Tavily Search + LLM to research any EEE topic and give summary with sources.")





