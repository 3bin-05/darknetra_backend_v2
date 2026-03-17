import pandas as pd
from xgboost import XGBClassifier
import joblib
from sklearn.preprocessing import LabelEncoder

# Load dataset
df = pd.read_csv("../PhishOFE_ds.csv")

# Encode TLD
le = LabelEncoder()
df["TLD"] = le.fit_transform(df["TLD"])

# Prepare data
X = df.drop(columns=["URL", "label"])
y = df["label"]

# Train model
model = XGBClassifier(eval_metric='logloss')
model.fit(X, y)

# Save model + encoder
joblib.dump(model, "../app/models/xgb_model.pkl")
joblib.dump(le, "../app/models/tld_encoder.pkl")

print("✅ Model + encoder saved successfully!")