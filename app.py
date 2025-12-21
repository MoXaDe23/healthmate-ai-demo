import streamlit as st
from triage_engine import triage
from PIL import Image
import pandas as pd
import joblib


st.set_page_config(page_title="HealthMate AI – Demo", page_icon="🩺", layout="centered")

# --- Simple localization (MVP: demo only) ---
LANG = {
    "English": {
        "title": "🩺 HealthMate AI (Demo)",
        "subtitle": "AI-powered symptom triage for low-resource settings (prototype)",
        "symptoms": "Describe your symptoms (text)",
        "age": "Age",
        "sex": "Sex",
        "pregnant": "Pregnant?",
        "followup": "Quick follow-up questions (tick what applies)",
        "run": "Get Guidance",
        "result": "Result",
        "triage_level": "Triage level",
        "why": "Why this recommendation",
        "next": "What to do next",
        "facilities": "Suggested places to seek care (demo)",
        "disclaimer": "Safety notes",
    },
    "Luganda (demo)": {
        "title": "🩺 HealthMate AI (Ekigezo)",
        "subtitle": "Okulambika obulwadde + okusalawo obwangu (prototype)",
        "symptoms": "Nyumya obubonero bwo (text)",
        "age": "Emyaka",
        "sex": "Omusajja/Omukazi",
        "pregnant": "Olina olubuto?",
        "followup": "Ebibuuzo eby’okugoberera (londa ebikukwatako)",
        "run": "Funa Obulagirizi",
        "result": "Ebisubizo",
        "triage_level": "Eddaala ly’obulabe",
        "why": "Lwaki tusazeewo bwe tutyo",
        "next": "Kiki ky’olina okukola",
        "facilities": "W’oyinza okugenda (demo)",
        "disclaimer": "Obukuumi / Okulabula",
    },
    "Swahili (demo)": {
    "title": "🩺 HealthMate AI (Onyesho)",
    "subtitle": "AI-powered symptom triage for low-resource settings (prototype)",
    "symptoms": "Eleza dalili zako (maandishi)",
    "age": "Umri",
    "sex": "Jinsia",
    "pregnant": "Mjamzito?",
    "followup": "Maswali ya haraka ya kufuatilia",
    "run": "Pata Mwongozo",
    "result": "Matokeo",
    "triage_level": "Kiwango cha hatari",
    "why": "Kwa nini mapendekezo haya",
    "next": "Hatua zinazofuata",
    "facilities": "Mahali pa kupata huduma (demo)",
    "disclaimer": "Tahadhari za usalama",
    },
    "Runyankole/Rukiga (demo)": {
    "title": "🩺 HealthMate AI (Okworeka)",
    "subtitle": "AI-powered symptom triage for low-resource settings (prototype)",
    "symptoms": "Shoboorora obubonero bwawe (ebigambo)",
    "age": "Emyaka",
    "sex": "Omusheijja/Omukazi",
    "pregnant": "Oyine'nda?",
    "followup": "Ebibuuzo by'okugyendera",
    "run": "Tuna Oburagirizi",
    "result": "Ebisubizo",
    "triage_level": "Eshonga y'obuhunga",
    "why": "Ekiragiro ky'ekyo",
    "next": "Eki orikukora",
    "facilities": "Aho orikubaasa kugenda (demo)",
    "disclaimer": "Okwegyendesereza",
    }
}

@st.cache_resource
def load_model():
    payload = joblib.load("model.joblib")
    return payload["model"], payload["feature_columns"]

def symptoms_to_features(symptom_text: str, feature_columns):
    """
    Very simple symptom extractor:
    - If a feature name appears in the user's text, mark it 1 else 0
    Dataset features look like: 'itching', 'skin_rash', 'vomiting', etc.
    """
    text = (symptom_text or "").lower()
    row = {c: 0 for c in feature_columns}
    for c in feature_columns:
        token = c.replace("_", " ")
        if token in text or c in text:
            row[c] = 1
    return pd.DataFrame([row])

# --- UI ---
st.sidebar.title("Settings")
language = st.sidebar.selectbox(
    "Language",
    ["English", "Luganda (demo)", "Swahili (demo)", "Runyankole/Rukiga (demo)"]
)
T = LANG[language]

try:
    logo = Image.open("logo.jpg")
    st.image(logo, width=120)
except:
    pass

st.title(T["title"])
st.caption(T["subtitle"])

with st.expander("Demo note (for judges)", expanded=False):
    st.write(
        "This is a prototype demonstrating end-to-end triage guidance using sample inputs. "
        "It is not a diagnostic tool. In incubation, we will improve local-language NLP, "
        "validation, and facility referral integrations. "
        "Designed for low bandwidth and future SMS/USSD support."
    )


symptom_text = st.text_area(T["symptoms"], placeholder="e.g., I have fever and headache for 2 days, body weakness...")
col1, col2, col3 = st.columns(3)
age = col1.number_input(T["age"], min_value=0, max_value=120, value=28, step=1)
sex = col2.selectbox(T["sex"], ["Male", "Female"])
pregnant = False
if sex == "Female":
    pregnant = col3.checkbox(T["pregnant"], value=False)
else:
    col3.write("")  # spacer

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

if st.button(T["run"], type="primary"):
    if not symptom_text.strip():
        st.warning("Please describe symptoms first.")
    else:
        # --- ML Prediction ---
        model, feature_columns = load_model()
        X_user = symptoms_to_features(symptom_text, feature_columns)
        pred = model.predict(X_user)[0]

        st.subheader("ML model prediction (trained on real dataset)")
        st.write(f"**Most likely condition label (dataset):** {pred}")

        # --- Triage Engine ---
        res = triage(symptom_text=symptom_text, age=int(age), sex=sex, pregnant=pregnant, answers=answers)

        # --- Display results ---


        st.subheader(T["result"])
        st.metric(T["triage_level"], res.title)

        # Add visual emphasis
        if res.level == "URGENT":
            st.error("⚠️ Urgent triage triggered")
        elif res.level == "CLINIC":
            st.warning("⏱️ Clinic review recommended")
        else:
            st.success("✅ Home care guidance")

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

        st.info("Tip for demo: try a 'danger sign' like chest pain + difficulty breathing to see URGENT triage.")
