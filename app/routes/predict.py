from fastapi import APIRouter
from app.services.feature_extractor import extract_features
from app.services.model import predict
from app.services.google_safe import check_google_safe
from app.services.virustotal import check_virustotal

router = APIRouter()


@router.post("/predict")
def predict_url(data: dict):
    url = data.get("url")

    if not url:
        return {"error": "URL is required"}

    if not url.startswith("http"):
        url = "https://" + url

    # 🔹 ML Features
    features = extract_features(url)
    pred, prob = predict(features)

    # 🔹 Google Safe Browsing
    google_flag = check_google_safe(url)

    # 🔹 VirusTotal
    vt_score = check_virustotal(url)

    # 🔥 Trusted domains (hackathon safety layer)
    trusted_domains = ["google.com", "youtube.com", "facebook.com"]

    if any(domain in url for domain in trusted_domains):
        prob = prob * 0.2

    # 🔥 Convert API signals
    google_score = 1 if google_flag == 1 else 0

    # 🔥 Final score
    final_score = (
        prob * 40 +
        google_score * 30 +
        vt_score * 30
    )

    # 🔥 Override rules (VERY IMPORTANT)
    if google_flag == 1:
        label = "Phishing"
    elif vt_score > 0.5:
        label = "Phishing"
    elif final_score > 70:
        label = "Phishing"
    elif final_score > 30:
        label = "Suspicious"
    else:
        label = "Safe"

    return {
        "url": url,
        "prediction": label,
        "confidence": float(prob),
        "score": float(final_score),
        "details": {
            "ml_score": float(prob),
            "google_flag": google_flag,
            "virustotal_score": float(vt_score)
        }
    }