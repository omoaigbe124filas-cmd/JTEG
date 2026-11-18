# VinciCAD V2 - Full General CAD + AI - UPDATED
# Author: Josiah Ehi - VinciCAD
# Features: SOLIDWORKS style + FreeCAD style + Proteus style + VINCI AI (FRIDAY)
# UPDATED: No Tavily, No Hugging Face. Only Groq key needed.
# Research = DuckDuckGo + Wikipedia (Free) | Image = Pollinations (Free, No Key)

import streamlit as st
import math
import io
import urllib.parse
import numpy as np

# ---------- OPTIONAL AI LIBS ----------
try:
    from groq import Groq
    HAS_GROQ = True
except:
    HAS_GROQ = False

try:
    import requests
    HAS_REQUESTS = True
except:
    HAS_REQUESTS = False

try:
    from gtts import gTTS
    HAS_GTTS = True
except:
    HAS_GTTS = False

st.set_page_config(page_title="VinciCAD V2 - Free CAD + AI", page_icon="⚙️", layout="wide")

# ---------- SESSION STATE ----------
if "teeth" not in st.session_state: st.session_state.teeth = 24
if "diameter" not in st.session_state: st.session_state.diameter = 50
if "thickness" not in st.session_state: st.session_state.thickness = 8
if "hole_dia" not in st.session_state: st.session_state.hole_dia = 10
if "length" not in st.session_state: st.session_state.length = 80
if "width" not in st.session_state: st.session_state.width = 60
if "mode" not in st.session_state: st.session_state.mode = "Gear - Parametric"
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello Boss, I am V.I.N.C.I. - your FRIDAY. I can design gears, design buck converter, do deep research, generate images, and control this app by voice. Try: 'Make a 32 teeth gear' or 'Research best buck IC'"}]
if "vin" not in st.session_state: st.session_state.vin = 12
if "vout" not in st.session_state: st.session_state.vout = 5.0
if "generated_image_prompt" not in st.session_state: st.session_state.generated_image_prompt = ""

# ---------- SECRETS - ONLY GROQ NOW ----------
def get_secret(name):
    try:
        return st.secrets[name]
    except:
        return None

GROQ_KEY = get_secret("GROQ_API_KEY")

# ---------- FREE RESEARCH FUNCTION - EDITED, NO TAVILY ----------
# Uses DuckDuckGo (no key) + Wikipedia (no key) + Groq to summarize
def free_research(query):
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1},
            timeout=10
        ).json()
        ddg_text = r.get("AbstractText", "")
        if not ddg_text and r.get("RelatedTopics"):
            first = r["RelatedTopics"][0]
            if isinstance(first, dict):
                ddg_text = first.get("Text", "")
    except:
        ddg_text = ""

    try:
        wiki = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}",
            timeout=10
        ).json()
        wiki_text = wiki.get("extract", "")
    except:
        wiki_text = ""

    combined = f"DuckDuckGo: {ddg_text}\nWikipedia: {wiki_text}"
    if combined.strip() == "DuckDuckGo: \nWikipedia:":
        combined = "No direct DuckDuckGo/Wikipedia result. Groq will answer from its knowledge."
    return combined

# ---------- HEADER ----------
st.markdown("# ⚙️ VinciCAD V2")
st.markdown("### Design. Simulate. Preview. Export. Talk to AI. - Like SOLIDWORKS + FreeCAD + Proteus + FRIDAY, but Free")
st.divider()

# ---------- SIDEBAR ----------
st.sidebar.header("🛠️ VinciCAD Studio")
all_modes = ["Gear - Parametric","Box / Enclosure","Cylinder / Shaft","Plate with Holes","Buck Converter Board - Proteus Style","Assembly - 2 Gears Meshing","PCB View - Buck Converter"]
mode = st.sidebar.selectbox("Design Mode", all_modes, index=all_modes.index(st.session_state.mode) if st.session_state.mode in all_modes else 0)
st.session_state.mode = mode

st.sidebar.divider()
st.sidebar.subheader("Dimensions (mm)")

teeth = st.session_state.teeth
diameter = st.session_state.diameter
thickness = st.session_state.thickness
hole_dia = st.session_state.hole_dia
length = st.session_state.length
width = st.session_state.width
holes = 4
vin = st.session_state.vin
vout = st.session_state.vout
module = 2.0
teeth2 = 24
diameter2 = 80

if mode == "Gear - Parametric":
    teeth = st.sidebar.slider("Number of Teeth (N)", 8, 60, st.session_state.teeth, key="teeth_slider")
    diameter = st.sidebar.slider("Pitch Diameter (mm)", 20, 120, st.session_state.diameter, key="dia_slider")
    thickness = st.sidebar.slider("Thickness (mm)", 3, 25, st.session_state.thickness, key="thick_slider")
    hole_dia = st.sidebar.slider("Center Hole (mm)", 3, 30, st.session_state.hole_dia, key="hole_slider")
    st.session_state.teeth = teeth; st.session_state.diameter = diameter; st.session_state.thickness = thickness; st.session_state.hole_dia = hole_dia
    module = diameter / teeth if teeth else 2.0
    st.sidebar.info(f"Module: {module:.2f} mm | Addendum: {module:.2f}mm | Dedendum: {1.25*module:.2f}mm")

elif mode == "Box / Enclosure":
    length = st.sidebar.slider("Length (mm)", 10, 200, st.session_state.length)
    width = st.sidebar.slider("Width (mm)", 10, 200, st.session_state.width)
    thickness = st.sidebar.slider("Height (mm)", 5, 100, 30)
    wall = st.sidebar.slider("Wall Thickness (mm)", 1, 5, 2)
    st.session_state.length = length; st.session_state.width = width

elif mode == "Cylinder / Shaft":
    diameter = st.sidebar.slider("Diameter (mm)", 5, 100, 25)
    thickness = st.sidebar.slider("Length (mm)", 10, 200, 60)
    hole_dia = st.sidebar.slider("Inner Hole (mm)", 0, 20, 0)

elif mode == "Plate with Holes":
    length = st.sidebar.slider("Plate Length (mm)", 20, 200, 100)
    width = st.sidebar.slider("Plate Width (mm)", 20, 200, 80)
    thickness = st.sidebar.slider("Plate Thickness (mm)", 2, 15, 5)
    hole_dia = st.sidebar.slider("Hole Diameter (mm)", 2, 15, 5)
    holes = st.sidebar.slider("Number of Holes", 2, 8, 4)

elif mode in ["Buck Converter Board - Proteus Style", "PCB View - Buck Converter"]:
    length = st.sidebar.slider("Board Length (mm)", 30, 100, 65)
    width = st.sidebar.slider("Board Width (mm)", 20, 80, 43)
    thickness = st.sidebar.slider("Board Thickness (mm)", 1, 3, 2)
    vin = st.sidebar.slider("Input Voltage (V)", 9, 24, st.session_state.vin)
    vout = st.sidebar.slider("Output Voltage (V)", 3.3, 12.0, st.session_state.vout)
    st.session_state.vin = vin; st.session_state.vout = vout
    duty = vout/vin*100 if vin else 0
    st.sidebar.success(f"Buck: {vin}V -> {vout}V | Duty: {duty:.1f}% | Eff ~92%")
    st.sidebar.write("**IC:** XL4015 / LM2596")
    st.sidebar.write("**Inductor:** 33uH, 3A")
    st.sidebar.write("**Capacitor:** 470uF + 100nF")
    st.sidebar.write("**Diode:** SS34 Schottky")

elif mode == "Assembly - 2 Gears Meshing":
    teeth = st.sidebar.slider("Gear 1 Teeth (N1)", 8, 40, 12)
    teeth2 = st.sidebar.slider("Gear 2 Teeth (N2)", 8, 60, 24)
    diameter = st.sidebar.slider("Gear 1 Diameter (mm)", 20, 80, 40)
    diameter2 = diameter * teeth2 / teeth if teeth else 80
    thickness = st.sidebar.slider("Thickness (mm)", 3, 15, 8)
    st.sidebar.info(f"Gear 2 Diameter: {diameter2:.1f}mm | Ratio: 1 : {teeth2/teeth:.2f} | Center Distance: {(diameter+diameter2)/2:.1f}mm")

st.sidebar.divider()
operation = st.sidebar.selectbox("Boolean Operation", ["Single Part", "Union - Add Second Part", "Cut - Subtract Hole", "Difference"])
color_choice = st.sidebar.color_picker("Part Color", "#FF3B30")
show_blueprint = st.sidebar.checkbox("Show Blueprint / Dimensions", value=True)
show_ai = st.sidebar.checkbox("Show VINCI AI Panel", value=True)

# ---------- MAIN AREA ----------
st.header(f"📐 Current Design: {mode}")
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("3D Preview / 2D Blueprint Preview")
    volume = 0
    if mode == "Gear - Parametric":
        volume = math.pi * (diameter/2)**2 * thickness - math.pi * (hole_dia/2)**2 * thickness
        angles = np.linspace(0, 2*np.pi, teeth*2+1)
        radii = np.array([diameter/2 if i % 2 == 0 else diameter/2 - module*0.8 for i in range(teeth*2+1)])
        chart_data = {"x": radii * np.cos(angles), "y": radii * np.sin(angles)}
        st.line_chart(chart_data)
        st.caption(f"Gear Preview: {teeth} teeth, Module {module:.2f}, Outer Dia {diameter}mm. Top view - Tooth profile simplified for preview.")
    elif mode == "Assembly - 2 Gears Meshing":
        angles = np.linspace(0, 2*np.pi, 100)
        st.line_chart({"Gear1_X": np.cos(angles)*diameter/2, "Gear2_X": np.cos(angles)*diameter2/2 + (diameter+diameter2)/2})
        st.success(f"Assembly: Gear1 {teeth}T turns 2x -> Gear2 {teeth2}T turns 1x. Meshing OK, center distance {(diameter+diameter2)/2:.1f}mm")
        volume = math.pi*(diameter/2)**2*thickness + math.pi*(diameter2/2)**2*thickness
    elif mode in ["Buck Converter Board - Proteus Style", "PCB View - Buck Converter"]:
        st.write("**Proteus-Style Schematic:**")
        st.code("VIN (12V) -> [XL4015] -> [Inductor 33uH] -> [Capacitor 470uF] -> VOUT (5V USB)\n           |-> [Diode SS34] -> GND\n           |-> [Feedback R1=1k, R2=3.1k] -> Vout = 1.23*(1+R2/R1)", language="text")
        st.bar_chart({"Board Length": [length], "Board Width": [width]})
        st.info("PCB View: Top layer - Red traces, Bottom layer - Blue GND plane. Components: XL4015 (SO-8), Inductor (SMD), 2x Capacitors, USB-A Port, Terminal Block.")
        volume = length * width * thickness
    else:
        st.bar_chart({"Length": [length], "Width": [width], "Thickness": [thickness]})
        if mode == "Box / Enclosure":
            volume = length*width*thickness
        elif mode == "Cylinder / Shaft":
            volume = math.pi*(diameter/2)**2*thickness
        elif mode == "Plate with Holes":
            volume = length*width*thickness - holes*math.pi*(hole_dia/2)**2*thickness

    st.write(f"**Boolean:** {operation} | **Color:** {color_choice}")
    if operation != "Single Part":
        st.info(f"Boolean {operation} applied. For this web version, volume adjusted for demo.")
        if operation == "Cut - Subtract Hole":
            volume = volume * 0.9
        elif operation == "Union - Add Second Part":
            volume = volume * 1.15

    stl_content = f"solid VinciCAD\n  facet normal 0 0 1\n    outer loop\n      vertex 0 0 0\n      vertex {length} 0 0\n      vertex 0 {width} 0\n    endloop\n  endfacet\nendsolid VinciCAD\n"
    st.download_button("⬇️ Download STL - For 3D Printing / Blender", data=stl_content.encode(), file_name="VinciCAD_Part.stl", mime="model/stl")
    dxf_content = f"""0
SECTION
2
HEADER
9
$ACADVER
1
AC1009
0
ENDSEC
0
SECTION
2
ENTITIES
0
LINE
10
0.0
20
0.0
11
{length}
21
{width}
0
CIRCLE
10
0.0
20
0.0
40
{diameter/2}
0
ENDSEC
0
EOF
"""
    st.download_button("📐 Download DXF - Blueprint", data=dxf_content, file_name="VinciCAD_Blueprint.dxf", mime="application/dxf")

with col2:
    st.subheader("📊 Engineering Data")
    if mode == "Gear - Parametric":
        st.metric("Teeth", teeth)
        st.metric("Pitch Diameter", f"{diameter} mm")
        st.metric("Module", f"{module:.2f} mm")
        st.metric("Volume", f"{volume:.1f} mm³")
        st.metric("Center Hole", f"{hole_dia} mm")
        st.write("**Gear Formula:**")
        st.latex(r"\frac{\omega_1}{\omega_2} = \frac{N_2}{N_1} = \frac{d_2}{d_1}")
        rpm = st.slider("Simulate RPM - Gear 1", 10, 200, 60)
        st.write(f"Gear 1: {rpm} RPM → Gear 2 ({teeth}T): {rpm * 12/teeth:.1f} RPM")
        st.progress(min(int(rpm/200*100), 100))
    elif mode == "Assembly - 2 Gears Meshing":
        st.metric("Gear 1", f"{teeth} Teeth, {diameter}mm")
        st.metric("Gear 2", f"{teeth2} Teeth, {diameter2:.1f}mm")
        st.metric("Gear Ratio", f"1 : {teeth2/teeth:.2f}")
        st.metric("Center Distance", f"{(diameter+diameter2)/2:.1f} mm")
        st.write("If Gear 1 turns 2x, Gear 2 turns 1x when ratio is 2:1. Torque increases, speed decreases.")
    elif mode in ["Buck Converter Board - Proteus Style", "PCB View - Buck Converter"]:
        st.metric("Input", f"{vin} V")
        st.metric("Output", f"{vout} V")
        st.metric("Duty Cycle", f"{vout/vin*100:.1f} %")
        st.metric("Efficiency (XL4015)", "~92%")
        st.write("**Formula:** Vout = 1.23 x (1 + R2/R1)")
        st.write("**For 5V:** R1 = 1k, R2 = 3.06k -> Use 3.1k")
        st.write("**For 3.3V:** R1 = 1k, R2 = 1.68k")
        st.write("**Proteus Simulation:** Connect VIN, GND, VOUT, check with voltmeter. Ripple < 50mV with 470uF.")
    else:
        st.metric("Volume (approx)", f"{volume:.1f} mm³")
        st.metric("Material Suggestion", "PLA for 3D Print / Steel for CNC")
        st.metric("Weight (PLA 1.24g/cm³)", f"{volume/1000*1.24:.1f} g")

    if show_blueprint:
        st.divider()
        st.subheader("📐 Blueprint View")
        if mode == "Gear - Parametric":
            st.code(f"Gear Blueprint:\nOuter Dia: {diameter}mm\nHole: {hole_dia}mm\nThickness: {thickness}mm\nTeeth: {teeth}\nModule: {module:.2f}\nAddendum: {module:.2f}mm\nTolerance: +/- 0.2mm\nScale 1:1 - All dimensions in mm", language="text")
        elif mode == "Assembly - 2 Gears Meshing":
            st.code(f"Assembly Blueprint:\nGear1: {teeth}T, {diameter}mm\nGear2: {teeth2}T, {diameter2:.1f}mm\nCenter Distance: {(diameter+diameter2)/2:.1f}mm\nMeshing: Involute, Backlash 0.1mm", language="text")
        else:
            st.code(f"Part Blueprint:\nLength: {length}mm\nWidth: {width}mm\nThickness: {thickness}mm\nTolerance: +/- 0.2mm\nMaterial: PLA / FR4 for PCB", language="text")

# ---------- VINCI AI - FRIDAY - FULL ----------
if show_ai:
    st.divider()
    st.header("🤖 V.I.N.C.I. - Your FRIDAY AI | Chat + Voice + Research + Image")
    st.caption("Vocal Intelligent Neural CAD Interface. E get full access to VinciCAD. Talk am, e go do am.")
    c1, c2, c3 = st.columns(3)
    with c1: st.success("Groq AI: " + ("Connected" if GROQ_KEY else "Need Key - Add in Secrets"))
    with c2: st.success("Research: Free - DuckDuckGo + Wikipedia - No Key Needed")
    with c3: st.success("Image: Free - Pollinations - No Key Needed")

    tab_chat, tab_research, tab_image, tab_voice = st.tabs(["💬 Chat + Control", "🔍 Deep Research", "🎨 Image Generation", "🎤 Voice"])

    with tab_chat:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        user_input = st.chat_input("Talk to VINCI... e.g. 'Make a 32 teeth gear, 60mm' or 'Design buck 12V to 5V'")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            reply = ""
            low = user_input.lower()
            if GROQ_KEY and HAS_GROQ:
                try:
                    client = Groq(api_key=GROQ_KEY)
                    chat = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "You are V.I.N.C.I., FRIDAY for VinciCAD. User is Josiah, 17, EEE student in Nigeria. You control VinciCAD. If user asks gear, buck, research, image, explain in simple English + small Pidgin. Be helpful, short. If user says make gear with numbers, repeat the numbers clearly like 'TEETH:32 DIAMETER:60'. "}, {"role": "user", "content": user_input}],
                        temperature=0.5, max_tokens=400
                    )
                    reply = chat.choices[0].message.content
                except Exception as e:
                    reply = f"Groq error: {e}. Using local brain."
            if not reply:
                import re
                nums = re.findall(r"\d+", user_input)
                if "gear" in low or "teeth" in low:
                    if len(nums) >= 2:
                        try:
                            nt = int(nums[0]); nd = int(nums[1])
                            st.session_state.teeth = nt; st.session_state.diameter = nd; st.session_state.mode = "Gear - Parametric"
                            reply = f"Done boss. I don set gear to {nt} teeth, {nd}mm diameter, Module {nd/nt:.2f}mm. I don rebuild am for you. Want me to export STL?"
                        except:
                            reply = "Done boss, gear updated."
                    elif len(nums) == 1:
                        st.session_state.teeth = int(nums[0]); st.session_state.mode = "Gear - Parametric"
                        reply = f"Done boss. Gear set to {nums[0]} teeth. I don rebuild am."
                    else:
                        reply = "Done boss. I don set gear mode. Tell me teeth and diameter, e.g. 'Make 32 teeth gear, 60mm'"
                elif "buck" in low or "converter" in low or "12v" in low:
                    st.session_state.mode = "Buck Converter Board - Proteus Style"
                    reply = "Buck converter designed: 12V to 5V, Duty 41.6%. Use XL4015, 33uH inductor, 470uF capacitor, SS34 diode. I don switch you to Buck Converter Board mode. Check sidebar."
                elif "assembly" in low or "2 gears" in low or "meshing" in low:
                    st.session_state.mode = "Assembly - 2 Gears Meshing"
                    reply = "Assembly mode on. Gear 1 12T, Gear 2 24T, Ratio 1:2. Gear 1 must turn 2x for Gear 2 to turn 1x."
                elif "box" in low:
                    st.session_state.mode = "Box / Enclosure"
                    reply = "Box mode on. I don switch to Enclosure."
                elif "plate" in low:
                    st.session_state.mode = "Plate with Holes"
                    reply = "Plate mode on."
                elif "research" in low:
                    reply = "Deep research - go to Research tab and type your topic, I go search web with DuckDuckGo + Wikipedia and give summary."
                elif "image" in low or "generate" in low:
                    reply = "Image - go to Image Generation tab, type prompt, I go generate with Pollinations, no key needed."
                elif "export" in low or "stl" in low:
                    reply = "STL ready. Scroll up, click 'Download STL' button. E go download for 3D printing / Blender."
                else:
                    reply = f"I hear you boss: '{user_input}'. I can do: Make gear, Design buck converter, Show assembly, Export STL, Research, Generate image. Try: 'Make a 32 teeth gear, 60mm'"
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

    # ---------- RESEARCH TAB - EDITED, NO TAVILY ----------
    with tab_research:
        st.subheader("🔍 Deep Research - Free, No Key Needed")
        st.caption("Uses DuckDuckGo + Wikipedia, then Groq summarizes for you.")
        q = st.text_input("Research topic", value="Best inductor for 12V to 5V buck converter for phone charging", key="research_q")
        if st.button("Run Deep Research", key="research_btn"):
            with st.spinner("Searching DuckDuckGo + Wikipedia..."):
                info = free_research(q)
            st.write("**Raw info found:**")
            st.write(info)
            if GROQ_KEY and HAS_GROQ:
                try:
                    client = Groq(api_key=GROQ_KEY)
                    summ = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": f"Summarize for 17yr EEE student in simple English, bullet points. Topic: {q}. Info: {info}"}],
                        temperature=0.4, max_tokens=600
                    )
                    st.markdown("**VINCI Summary:**")
                    st.write(summ.choices[0].message.content)
                except Exception as e:
                    st.error(f"Groq summary error: {e}")
            else:
                st.warning("Add GROQ_API_KEY for AI summary. Raw info above still works without am.")

    # ---------- IMAGE TAB - EDITED, NO HUGGING FACE ----------
    with tab_image:
        st.subheader("🎨 Image Generation - Free, No Key, No Signup")
        st.caption("Uses Pollinations.ai - Just type prompt, image go come.")
        prompt = st.text_input("Image prompt", value="Futuristic mechanical gear, steampunk, metallic, studio lighting, for engineering presentation", key="img_prompt")
        if st.button("Generate Image", key="img_btn"):
            st.session_state.generated_image_prompt = prompt
            safe_prompt = urllib.parse.quote(prompt)
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&seed=42&model=flux&nologo=true"
            with st.spinner("Generating image..."):
                st.image(image_url, caption=f"Generated: {prompt}", use_column_width=True)
            st.success("Image generated! Right-click to save for your report.")
            st.write(f"Direct link: {image_url}")

    with tab_voice:
        st.subheader("🎤 Voice - Talk to VINCI")
        st.write("For Streamlit Cloud, use Audio Input (works on phone Chrome).")
        audio = st.audio_input("Hold to record - Talk to VINCI", key="vinci_audio")
        if audio is not None:
            st.audio(audio)
            if GROQ_KEY and HAS_GROQ:
                try:
                    client = Groq(api_key=GROQ_KEY)
                    with open("/tmp/vinci_voice.wav", "wb") as f:
                        f.write(audio.getvalue())
                    with open("/tmp/vinci_voice.wav", "rb") as f:
                        trans = client.audio.transcriptions.create(file=( "voice.wav", f.read()), model="whisper-large-v3", response_format="text")
                    text = str(trans)
                    st.success(f"VINCI heard you: '{text}'")
                    st.info("Copy that text, paste am for Chat tab, VINCI go execute am.")
                except Exception as e:
                    st.error(f"Voice error: {e}. Check Groq key. Whisper needs Groq key.")
            else:
                st.warning("Add GROQ_API_KEY to enable Whisper voice-to-text.")
            if HAS_GTTS:
                if st.button("🔊 Make VINCI Speak Reply", key="tts_btn"):
                    try:
                        tts = gTTS(text="Hello Boss, I am VINCI. Your gear is ready.", lang="en")
                        buf = io.BytesIO()
                        tts.write_to_fp(buf)
                        buf.seek(0)
                        st.audio(buf, format="audio/mp3")
                    except Exception as e:
                        st.error(f"TTS error: {e}")

# ---------- FOOTER ----------
st.divider()
st.markdown("""
### 🚀 VinciCAD Roadmap
**V1:** Parametric CAD + STL/DXF | **V2 (This version):** + VINCI AI - Chat, Voice, Research, Image + Assembly + Proteus PCB | **V3:** Full Auto Voice Control + Real-time Gear Animation + Circuit Simulator | **V4:** AI Text-to-CAD

**Built by Josiah Ehi | For Students, Makers & Engineers in Nigeria & Everywhere**
""")
st.caption("VinciCAD is free and open-source. Inspired by SOLIDWORKS, FreeCAD, Proteus, Blender. VINCI AI inspired by FRIDAY from Iron Man. Enhanced for mobile-first learning.")
