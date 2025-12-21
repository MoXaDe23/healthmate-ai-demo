import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
import joblib

DATA_PATH = os.path.join("data", "Training.csv")
MODEL_PATH = "model.joblib"

def main():
    df = pd.read_csv(DATA_PATH)

    # Many versions of this dataset include an extra unnamed column at the end
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    target_col = "prognosis"  # common label name in this dataset
    if target_col not in df.columns:
        raise ValueError(f"Expected target column '{target_col}' not found. Columns: {df.columns.tolist()[:10]}...")

    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Train/validation split for quick sanity check
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_val)
    acc = accuracy_score(y_val, preds)

    # Save model + feature columns (VERY IMPORTANT for deployment)
    payload = {
        "model": model,
        "feature_columns": list(X.columns)
    }
    joblib.dump(payload, MODEL_PATH)

    print(f"✅ Trained model saved to {MODEL_PATH}")
    print(f"✅ Validation accuracy (quick check): {acc:.3f}")
    print(f"✅ Features: {len(X.columns)}")

if __name__ == "__main__":
    main()
