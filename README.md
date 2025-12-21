# HealthMate AI (Demo) 🩺
**AI-powered symptom triage for low-resource settings** — a deployed Streamlit prototype that combines:
- a **trained machine learning model** (real dataset)
- plus **safety-first triage logic** (red-flag escalation & disclaimers)

> ⚠️ **Medical Disclaimer:** HealthMate AI provides general health guidance and triage support.  
> It **does not diagnose** and is **not a substitute** for professional medical care.

---

## ✅ What this prototype demonstrates
- End-to-end user workflow: **symptom input → ML prediction → triage guidance**
- A **real trained model** saved as `model.joblib`
- Live demo UI built with **Streamlit**
- Safety-first escalation to urgent care when danger signs are present

---

## 🧠 AI / ML Model
- Dataset: A public symptom–disease dataset from Kaggle (Training.csv / Testing.csv)
- Model: `RandomForestClassifier` (scikit-learn)
- Training script: `train_model.py`
- Output: `model.joblib` (model + feature columns)

**Important note:** This dataset is used as a **proof-of-concept training proxy**.  
Future versions will incorporate **locally relevant data**, clinician review, and validation studies.

---

## 🧩 Project Structure
```text
healthmate_demo/
  app.py                 # Streamlit UI (main app)
  triage_engine.py       # Safety-first triage logic
  train_model.py         # ML training script (real dataset)
  model.joblib           # Saved trained model
  requirements.txt       # Dependencies
  data/
    Training.csv
    Testing.csv
