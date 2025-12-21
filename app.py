import streamlit as st
import pandas as pd
import joblib
import base64

from triage_engine import triage

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="HealthMate AI – Demo", page_icon="🩺", layout="centered")


# -----------------------------
# LOGO (Base64) – required for HTML header img
# -----------------------------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

if "LOGO_B64" not in st.session_state:
    try:
        st.session_state["LOGO_B64"] = get_base64_of_bin_file("logo.png")
    except:
        st.session_state["LOGO_B64"] = ""


# -----------------------------
# STYLING (HealthMate palette)
# -----------------------------
st.markdown("""
<style>
/* Whole app background */
.stApp {
    background-color: #F8FAFC;
}
[data-testid="stAppViewContainer"] {
    background-color: #F8FAFC;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

/* HealthMate Header band */
.hm-header {
    background: linear-gradient(90deg, #0E8F8B, #0E8F8B);
    padding: 1.1rem 1.2rem;
    border-radius: 14px;
    color: white;
    margin-bottom: 1.2rem;
    border: 1px solid rgba(255,255,255,0.10);
}

.hm-header h1 {
    color: white;
    margin: 0;
    line-height: 1.1;
    font-size: 2rem;
    font-weight: 700;
}

.hm-header p {
    color: #E6FFFA;
    margin-top: 0.35rem;
    margin-bottom: 0;
    font-size: 1rem;
}

/* Improve readability */
label, .stMarkdown, .stTextArea, .stSelectbox, .stNumberInput {
    color: #0F172A !important;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Localization (Demo)
# -----------------------------
LANG = {
    "English": {
        "title": "HealthMate AI",
        "subtitle": "AI-powered symptom triage for low-resource settings (prototype)",
        "symptoms": "Describe your symptoms (text)",
        "symptoms_help": "Example: fever, headache, vomiting, cough, body weakness…",
        "age": "Age",
        "sex": "Sex",
        "pregnant": "Pregnant?",
        "followup": "Quick follow-up questions (tick what applies)",
        "run": "🩺 Get Health Guidance",
        "result": "Result",
        "triage_level": "Triage level",
        "why": "Why this recommendation",
        "next": "What to do next",
        "facilities": "Suggested places to seek care (demo)",
        "disclaimer": "Safety notes",
        "reset": "🔄 Start New Case",
        "ml_title": "ML model prediction (trained on real dataset)",
        "ml_label": "Most likely condition label (dataset)",
        "demo_cases": "🎯 Quick Demo Cases",
        "demo_mild": "Mild (Home care)",
        "demo_mod": "Moderate (Clinic)",
        "demo_sev": "Severe (Urgent)",
    },
    "Luganda (demo)": {
        "title": "HealthMate AI (Ekigezo)",
        "subtitle": "AI-powered symptom triage for low-resource settings (prototype)",
        "symptoms": "Nyumya obubonero bwo (text)",
        "symptoms_help": "Okugeza: omusujja, okulumwa omutwe, okusesema, okukohola…",
        "age": "Emyaka",
        "sex": "Omusajja/Omukazi",
        "pregnant": "Olina olubuto?",
        "followup": "Ebibuuzo eby’okugoberera",
        "run": "🩺 Funa Obulagirizi",
        "result": "Ebisubizo",
        "triage_level": "Eddaala ly’obulabe",
        "why": "Lwaki tusazeewo bwe tutyo",
        "next": "Kiki ky’olina okukola",
        "facilities": "W’oyinza okugenda (demo)",
        "disclaimer": "Okulabula",
        "reset": "🔄 Tandika omusango omupya",
        "ml_title": "Ekiragiro kya ML (trained on real dataset)",
        "ml_label": "Ekizinga okukwatagana (dataset label)",
        "demo_cases": "🎯 Eby’okugezesa",
        "demo_mild": "Kyangu (Ewaka)",
        "demo_mod": "Ky’omu (Ddwaaliro)",
        "demo_sev": "Kizito (Mangu)",
    },
    "Swahili (demo)": {
        "title": "HealthMate AI (Onyesho)",
        "subtitle": "AI-powered symptom triage for low-resource settings (prototype)",
        "symptoms": "Eleza dalili zako (maandishi)",
        "symptoms_help": "Mfano: homa, maumivu ya kichwa, kutapika, kikohozi…",
        "age": "Umri",
        "sex": "Jinsia",
        "pregnant": "Mjamzito?",
        "followup": "Maswali ya haraka ya kufuatilia",
        "run": "🩺 Pata Mwongozo",
        "result": "Matokeo",
        "triage_level": "Kiwango cha hatari",
        "why": "Kwa nini mapendekezo haya",
        "next": "Hatua zinazofuata",
        "facilities": "Mahali pa kupata huduma (demo)",
        "disclaimer": "Tahadhari za usalama",
        "reset": "🔄 Anza kesi mpya",
        "ml_title": "Utabiri wa ML (trained on real dataset)",
        "ml_label": "Lebo inayowezekana (dataset label)",
        "demo_cases": "🎯 Mifano ya Haraka",
        "demo_mild": "Nyepesi (Nyumbani)",
        "demo_mod": "Wastani (Kliniki)",
        "demo_sev": "Hatari (Dharura)",
    },
    "Runyankole/Rukiga (demo)": {
        "title": "HealthMate AI (Okworeka)",
        "subtitle": "AI-powered symptom triage for low-resource settings (prototype)",
        "symptoms": "Shoboorora obubonero bwawe (ebigambo)",
        "symptoms_help": "Okugeza: omuswijja, okuruma omutwe, okusesema, okukohola…",
        "age": "Emyaka",
        "sex": "Omushaijja/Omukazi",
        "pregnant": "Olina olubuto?",
        "followup": "Ebibuuzo by’okugyendera",
        "run": "🩺 Tunga Oburagirizi",
        "result": "Ebisubizo",
        "triage_level": "Eshonga y’obuhunga",
        "why": "Ekiragiro ky’ekyo",
        "next": "Eki orikukora",
        "facilities": "Aho orikubaasa kugenda (demo)",
        "disclaimer": "Okwegyendesereza",
        "reset": "🔄 Tandika omusango omupya",
        "ml_title": "Ekiragiro kya ML (trained on real dataset)",
        "ml_label": "Ekirango ekirikukwatagana (dataset label)",
        "demo_cases": "🎯 Eby’okugezesaho",
        "demo_mild": "Kyangu (Ewaka)",
        "demo_mod": "Ky’omu (Kiliniki)",
        "demo_sev": "Kizito (Emergensi)",
    }
}


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Settings")
language = st.sidebar.selectbox(
    "Language",
    ["English", "Luganda (demo)", "Swahili (demo)", "Runyankole/Rukiga (demo)"]
)
T = LANG[language]

st.sidebar.markdown("### 🩺 About HealthMate AI")
st.sidebar.write(
    "HealthMate AI is a safety-first, AI-powered symptom triage assistant "
    "designed for low-resource and low-bandwidth settings."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ Medical Disclaimer")
st.sidebar.caption(
    "This tool provides general guidance and triage support only. "
    "It does not diagnose and does not replace a healthcare professional."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌍 Supported Languages (Demo)")
st.sidebar.caption("• English\n• Luganda\n• Swahili\n• Runyankole/Rukiga")

st.sidebar.markdown("---")
with st.sidebar.expander("🛣️ Roadmap"):
    st.write(
        "- Stronger local-language NLP\n"
        "- Low-bandwidth optimization\n"
        "- SMS/USSD access for feature phones\n"
        "- Facility referral mapping\n"
        "- Clinical validation studies"
    )


# -----------------------------
# Model loading + symptom feature conversion
# -----------------------------
@st.cache_resource
def load_model():
    payload = joblib.load("model.joblib")
    return payload["model"], payload["feature_columns"]

def symptoms_to_features(symptom_text: str, feature_columns):
    text = (symptom_text or "").lower()
    row = {c: 0 for c in feature_columns}
    for c in feature_columns:
        token = c.replace("_", " ")
        if token in text or c in text:
            row[c] = 1
    return pd.DataFrame([row])


# -----------------------------
# Header (Logo inside teal band)
# -----------------------------
st.markdown(f"""
<div class="hm-header" style="display:flex; align-items:center; gap:16px;">
  <div style="background:white; padding:10px; border-radius:12px;">
    <img src="data:image/png;base64,{st.session_state.get('LOGO_B64','')}" width="90" />
  </div>
  <div>
    <h1 style="margin:0;">{T["title"]}</h1>
    <p style="margin:0.35rem 0 0 0;">{T["subtitle"]}</p>
  </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# Demo note
# -----------------------------
with st.expander("Demo note (for judges)", expanded=False):
    st.write(
        "This is a prototype demonstrating end-to-end triage guidance using sample inputs. "
        "It is not a diagnostic tool. In incubation, we will improve local-language NLP, "
        "validation, and facility referral integrations. "
        "Designed for low bandwidth and future SMS/USSD support."
    )


# -----------------------------
# Demo preset buttons (optional but highly recommended)
# -----------------------------
st.markdown(f"### {T['demo_cases']}")
cA, cB, cC = st.columns(3)

if cA.button(T["demo_mild"], use_container_width=True):
    st.session_state["symptoms"] = "mild headache and fever since yesterday"
if cB.button(T["demo_mod"], use_container_width=True):
    st.session_state["symptoms"] = "fever and vomiting for four days"
if cC.button(T["demo_sev"], use_container_width=True):
    st.session_state["symptoms"] = "chest tightness and difficulty breathing"


# -----------------------------
# Inputs
# -----------------------------
symptom_text = st.text_area(
    T["symptoms"],
    value=st.session_state.get("symptoms", ""),
    placeholder=T["symptoms_help"]
)

col1, col2, col3 = st.columns(3)
age = col1.number_input(T["age"], min_value=0, max_value=120, value=28, step=1)
sex = col2.selectbox(T["sex"], ["Male", "Female"])
pregnant = False
if sex == "Female":
    pregnant = col3.checkbox(T["pregnant"], value=False)
else:
    col3.write("")

st.subheader(T["followup"])
c1, c2 = st.columns(2)

answers = {}
answers["difficulty_breathing"] = c1.checkbox("Difficulty breathing / breathlessness")
answers["chest_pain_now"] = c1.checkbox("Chest pain / tightness right now")
answers["confusion"] = c1.checkbox("Confusion / very drowsy / not responding")
answers["fainting"] = c1.checkbox("Fainted / collapsed")
answers["bleeding"] = c1.checkbox("Any bleeding (vomit blood, blood in stool, coughing blood)")

answers["fever_high"] = c2.checkbox("Very high fever (≥39°C) or feels extremely hot")
answers["fever_days_3plus"] = c2.checkbox("Fever for 3 days or more")
answers["severe_headache"] = c2.checkbox("Severe headache (worst ever) especially with fever")
answers["persistent_vomiting"] = c2.checkbox("Persistent vomiting")
answers["diarrhea_many"] = c2.checkbox("Diarrhea many times per day")
answers["unable_to_drink"] = c2.checkbox("Unable to drink/keep fluids down")

st.divider()


# -----------------------------
# Run inference + show results
# -----------------------------
if st.button(T["run"], type="primary", use_container_width=True):
    if not symptom_text.strip():
        st.warning("Please describe symptoms first.")
    else:
        # ML prediction
        model, feature_columns = load_model()
        X_user = symptoms_to_features(symptom_text, feature_columns)
        pred = model.predict(X_user)[0]

        st.subheader(T["ml_title"])
        st.write(f"**{T['ml_label']}:** {pred}")

        # Safety-first triage
        res = triage(symptom_text=symptom_text, age=int(age), sex=sex, pregnant=pregnant, answers=answers)

        st.subheader(T["result"])
        st.metric(T["triage_level"], res.title)

        # Color-coded clinical feedback
        if res.level == "URGENT":
            st.error("🔴 Urgent: Seek care immediately")
        elif res.level == "CLINIC":
            st.warning("🟠 Clinic visit recommended within 24–48 hours")
        else:
            st.success("🟢 Home care and monitoring advised")

        st.markdown(f"### {T['why']}")
        for r in res.reasons:
            st.write("• " + r)

        st.markdown(f"### {T['next']}")
        for a in res.advice:
            st.write("• " + a)

        st.markdown(f"### {T['facilities']}")
        for f in res.suggested_facilities:
            st.write("• " + f)

        st.markdown(f"### {T['disclaimer']}")
        for d in res.disclaimers:
            st.caption("• " + d)

        # Reset button
        if st.button(T["reset"], use_container_width=True):
            st.session_state["symptoms"] = ""
            st.rerun()

        st.info("Tip for demo: Try 'chest tightness + difficulty breathing' to trigger urgent triage.")
