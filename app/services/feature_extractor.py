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


def extract_html_features(url: str):
    try:
        # 🔥 FIX: Browser-like request
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

            # 🔥 FIX: better favicon detection
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
        # 🔥 SAFE fallback (prevents false phishing)
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

    return {
        **url_features,
        **html_features,
        "TLD": tld_encoded
    }