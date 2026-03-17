import joblib
import pandas as pd

model = joblib.load("app/models/xgb_model.pkl")

EXPECTED_COLUMNS = model.get_booster().feature_names


def predict(features: dict):
    df = pd.DataFrame([features])

    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = 0

    df = df[EXPECTED_COLUMNS]

    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1]

    return prediction, probability