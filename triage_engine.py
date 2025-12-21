from dataclasses import dataclass
from typing import Dict, List, Tuple
@dataclass
class TriageResult:
    level: str                  # "SELF_CARE" | "CLINIC" | "URGENT"
    title: str                  # user-friendly label
    reasons: List[str]          # why this triage level
    advice: List[str]           # what to do next
    disclaimers: List[str]      # safety text
    suggested_facilities: List[str]  # placeholders for demo


# Simple NLP-ish keyword detection (MVP-friendly)
KEYWORDS = {
    "fever": ["fever", "hot", "temperature", "high temp", "burning"],
    "cough": ["cough", "coughing"],
    "chest_pain": ["chest pain", "tightness", "pressure in chest", "pain in chest"],
    "sob": ["shortness of breath", "can't breathe", "breathless", "difficulty breathing", "sob"],
    "abd_pain": ["abdominal pain", "stomach pain", "tummy pain", "belly pain"],
    "vomiting": ["vomit", "vomiting", "throwing up"],
    "diarrhea": ["diarrhea", "loose stool", "watery stool"],
    "headache": ["headache", "migraine", "head pain"],
    "pregnant": ["pregnant", "pregnancy"],
    "bleeding": ["bleeding", "blood in stool", "vomiting blood", "coughing blood"],
    "fainting": ["faint", "collapsed", "passed out", "syncope"],
    "confusion": ["confused", "confusion", "drowsy", "not responding"],
    "severe_pain": ["severe", "worst", "unbearable"],
}


def detect_flags(symptom_text: str) -> Dict[str, bool]:
    text = (symptom_text or "").lower().strip()
    flags = {k: False for k in KEYWORDS.keys()}
    for flag, words in KEYWORDS.items():
        for w in words:
            if w in text:
                flags[flag] = True
                break
    return flags


def risk_score(flags: Dict[str, bool], answers: Dict[str, bool], age: int, pregnant: bool) -> Tuple[int, List[str]]:
    score = 0
    reasons = []

    # Red flags (high risk)
    if answers.get("difficulty_breathing"):
        score += 5; reasons.append("You reported difficulty breathing.")
    if answers.get("chest_pain_now") or flags.get("chest_pain"):
        score += 5; reasons.append("Chest pain/tightness can be serious.")
    if answers.get("confusion") or flags.get("confusion"):
        score += 5; reasons.append("Confusion/drowsiness is a danger sign.")
    if answers.get("fainting") or flags.get("fainting"):
        score += 5; reasons.append("Fainting/collapse is a danger sign.")
    if answers.get("bleeding") or flags.get("bleeding"):
        score += 5; reasons.append("Bleeding can be an emergency.")

    # Fever-related
    if answers.get("fever_high") or flags.get("fever"):
        score += 2; reasons.append("Fever may suggest an infection.")
    if answers.get("fever_days_3plus"):
        score += 2; reasons.append("Fever lasting ≥ 3 days needs review.")
    if answers.get("severe_headache") and flags.get("headache"):
        score += 3; reasons.append("Severe headache with fever can be serious.")

    # GI-related
    if flags.get("vomiting") or answers.get("persistent_vomiting"):
        score += 2; reasons.append("Persistent vomiting increases dehydration risk.")
    if flags.get("diarrhea") or answers.get("diarrhea_many"):
        score += 2; reasons.append("Frequent diarrhea can cause dehydration.")
    if answers.get("unable_to_drink"):
        score += 4; reasons.append("Unable to drink/keep fluids down is a danger sign.")

    # Vulnerable groups
    if age >= 65:
        score += 2; reasons.append("Older adults are at higher risk of complications.")
    if age <= 5:
        score += 2; reasons.append("Young children are at higher risk of complications.")
    if pregnant:
        score += 2; reasons.append("Pregnancy requires a lower threshold to seek care.")

    return score, reasons


def triage(symptom_text: str, age: int, sex: str, pregnant: bool, answers: Dict[str, bool]) -> TriageResult:
    flags = detect_flags(symptom_text)
    score, reasons = risk_score(flags, answers, age, pregnant)

    # Determine level
    if score >= 8:
        level = "URGENT"
        title = "Seek urgent care now"
        advice = [
            "Go to the nearest health facility or emergency unit now.",
            "If available, call a trusted person to accompany you.",
            "If symptoms worsen (breathing, chest pain, confusion), seek help immediately."
        ]
    elif score >= 4:
        level = "CLINIC"
        title = "See a clinician within 24–48 hours"
        advice = [
            "Visit a clinic/health center within the next 1–2 days for assessment.",
            "Continue monitoring symptoms. If new danger signs appear, seek urgent care.",
            "Stay hydrated and rest. Avoid self-medicating with antibiotics."
        ]
    else:
        level = "SELF_CARE"
        title = "Home care + monitoring"
        advice = [
            "Rest, drink plenty of fluids, and monitor symptoms.",
            "Use simple supportive care (e.g., oral rehydration for diarrhea).",
            "If symptoms persist >48 hours or worsen, visit a clinic."
        ]

    disclaimers = [
        "HealthMate AI provides general guidance and triage support — not a medical diagnosis.",
        "If you feel severely unwell or unsafe, seek care immediately regardless of this result.",
        "For children, pregnancy, or chronic illness, seek care sooner when unsure."
    ]

    # Demo facility suggestions (placeholders)
    suggested_facilities = [
        "Nearest Health Centre III / IV",
        "Katabi Military Hospital",
        "District Hospital",
        "Regional Referral Hospital",
        "Grade B Entebbe Regional Referral Hospital",
        "Dr Bata StateHouse Hospital",
        "Emmanuel Hospital Entebbe",
        "Mulago National Referral Hospital (demo example)"
    ]

    # Keep reasons concise for demo
    reasons = list(dict.fromkeys(reasons))[:6]  # de-duplicate and cap

    return TriageResult(
        level=level,
        title=title,
        reasons=reasons if reasons else ["Based on the information provided."],
        advice=advice,
        disclaimers=disclaimers,
        suggested_facilities=suggested_facilities
    )
