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

    # Ensure URL format
    if not url.startswith("http"):
        url = "https://" + url

    # =========================
    # 🔹 FEATURE EXTRACTION
    # =========================
    features, reasons = extract_features(url)

    # =========================
    # 🔹 ML PREDICTION
    # =========================
    pred, prob = predict(features)

    # =========================
    # 🔹 EXTERNAL APIs
    # =========================
    google_flag = check_google_safe(url)
    vt_score = check_virustotal(url)

    # =========================
    # 🔥 TRUSTED DOMAINS (HACK)
    # =========================
    trusted_domains = ["google.com", "youtube.com", "facebook.com"]

    if any(domain in url for domain in trusted_domains):
        prob = prob * 0.2

    # =========================
    # 🔥 SCORE CALCULATION
    # =========================
    google_score = 1 if google_flag == 1 else 0

    final_score = (
        prob * 40 +
        google_score * 30 +
        vt_score * 30
    )

    # =========================
    # 🔥 LABEL DECISION
    # =========================
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

    # =========================
    # 🧠 ADD REASONS (CORE FEATURE)
    # =========================

    # ML reasoning
    if pred == 1 or label == "Phishing":
        reasons.append("Machine learning model detected phishing patterns")

    # Google Safe Browsing
    if google_flag == 1:
        reasons.append("Blocked by Google Safe Browsing")

    # VirusTotal reasoning
    if vt_score > 0.5:
        reasons.append("Flagged as malicious by VirusTotal")
    elif vt_score > 0:
        reasons.append("Some security vendors marked this as suspicious")

    # HTTPS check
    if features.get("IsHTTPS") == 0:
        reasons.append("Website is not using secure HTTPS connection")

    # Safe fallback
    if not reasons:
        reasons.append("No strong phishing indicators detected")

    # Remove duplicates (clean output)
    reasons = list(set(reasons))

    # =========================
    # 📦 FINAL RESPONSE
    # =========================
    return {
        "url": url,
        "prediction": label,
        "confidence": float(prob),
        "score": float(final_score),

        # 🔥 NEW FEATURE
        "reasons": reasons,

        "details": {
            "ml_score": float(prob),
            "google_flag": google_flag,
            "virustotal_score": float(vt_score)
        }
    }