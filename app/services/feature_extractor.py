import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import joblib

# Load encoder
try:
    tld_encoder = joblib.load("app/models/tld_encoder.pkl")
except:
    tld_encoder = None


def normalize_url(url: str):
    return url.lower()


def get_tld(url):
    domain = urlparse(url).netloc
    return domain.split('.')[-1]


# =========================
# 🔍 URL FEATURE EXTRACTION
# =========================
def extract_url_features(url: str):
    parsed = urlparse(url)

    return {
        "URLLength": len(url),
        "NoOfDots": url.count('.'),
        "NoOfSubDomain": max(len(parsed.netloc.split('.')) - 2, 0),
        "NoOfDigits": sum(c.isdigit() for c in url),
        "IsHTTPS": int(parsed.scheme == "https"),

        "NoOfEqual": url.count("="),
        "NoOfQmark": url.count("?"),
        "NoOfAmp": url.count("&"),
        "NoOfObfuscatedChar": sum(c in "%@" for c in url),
        "IsDomainIP": int(parsed.netloc.replace('.', '').isdigit()),
        "LineLength": len(url),
    }


# =========================
# 🌐 HTML FEATURE EXTRACTION
# =========================
def extract_html_features(url: str):
    try:
        res = requests.get(
            url,
            timeout=3,
            headers={"User-Agent": "Mozilla/5.0"},
            allow_redirects=True
        )

        soup = BeautifulSoup(res.text, "html.parser")

        return {
            "HasTitle": int(soup.title is not None),
            "HasMeta": int(soup.find("meta") is not None),
            "HasFavicon": int(soup.find("link", rel=lambda x: x and "icon" in x)),

            "HasExternalFormSubmit": 0,
            "HasCopyright": 0,
            "HasSocialNetworking": 0,
            "HasPasswordField": int(soup.find("input", {"type": "password"}) is not None),
            "HasSubmitButton": int(soup.find("input", {"type": "submit"}) is not None),

            "HasKeywordBank": int("bank" in res.text.lower()),
            "HasKeywordPay": int("pay" in res.text.lower()),
            "HasKeywordCrypto": int("crypto" in res.text.lower()),

            "NoOfPopup": 0,
            "NoOfiFrame": len(soup.find_all('iframe')),
            "NoOfImage": len(soup.find_all('img')),
            "NoOfJS": len(soup.find_all('script')),
            "NoOfCSS": len(soup.find_all('link')),
            "NoOfURLRedirect": len(res.history),
            "NoOfHyperlink": len(soup.find_all('a')),
        }

    except:
        # Safe fallback
        return {
            "HasTitle": 1,
            "HasMeta": 1,
            "HasFavicon": 1,
            "HasExternalFormSubmit": 0,
            "HasCopyright": 0,
            "HasSocialNetworking": 0,
            "HasPasswordField": 0,
            "HasSubmitButton": 1,
            "HasKeywordBank": 0,
            "HasKeywordPay": 0,
            "HasKeywordCrypto": 0,

            "NoOfPopup": 0,
            "NoOfiFrame": 0,
            "NoOfImage": 5,
            "NoOfJS": 5,
            "NoOfCSS": 2,
            "NoOfURLRedirect": 0,
            "NoOfHyperlink": 10,
        }


# =========================
# 🧠 REASON GENERATION (NEW)
# =========================
def generate_reasons_from_features(url: str, features: dict):
    reasons = []

    # URL-based checks
    if features["URLLength"] > 75:
        reasons.append("URL is unusually long")

    if features["NoOfDots"] > 5:
        reasons.append("Too many dots in URL (possible subdomain spoofing)")

    if features["NoOfSubDomain"] > 3:
        reasons.append("Too many subdomains detected")

    if features["NoOfDigits"] > 5:
        reasons.append("URL contains many numbers (suspicious pattern)")

    if features["IsHTTPS"] == 0:
        reasons.append("Connection is not secure (HTTP)")

    if features["NoOfObfuscatedChar"] > 0:
        reasons.append("URL contains obfuscated characters like % or @")

    if features["IsDomainIP"] == 1:
        reasons.append("Uses IP address instead of domain name")

    # Keyword checks
    suspicious_words = ["login", "verify", "secure", "bank", "account", "update"]
    if any(word in url for word in suspicious_words):
        reasons.append("Contains sensitive keywords like login/verify")

    # HTML-based checks
    if features["HasPasswordField"] == 1:
        reasons.append("Page contains password input field")

    if features["NoOfiFrame"] > 2:
        reasons.append("Multiple iframes detected")

    if features["NoOfURLRedirect"] > 2:
        reasons.append("Multiple redirects detected")

    if features["HasKeywordBank"] == 1:
        reasons.append("Bank-related content detected")

    if features["HasKeywordCrypto"] == 1:
        reasons.append("Crypto-related content detected")

    return reasons


# =========================
# 🔗 MAIN FEATURE FUNCTION
# =========================
def extract_features(url: str):
    url = normalize_url(url)

    url_features = extract_url_features(url)
    html_features = extract_html_features(url)

    # Encode TLD
    tld = get_tld(url)

    if tld_encoder:
        try:
            tld_encoded = tld_encoder.transform([tld])[0]
        except:
            tld_encoded = 0
    else:
        tld_encoded = 0

    combined_features = {
        **url_features,
        **html_features,
        "TLD": tld_encoded
    }

    # 🔥 Generate reasons here
    reasons = generate_reasons_from_features(url, combined_features)

    return combined_features, reasons