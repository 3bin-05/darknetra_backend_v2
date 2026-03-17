def calculate_score(ml_prob, google_score=0, vt_score=0, rule_score=0):
    final_score = (
        ml_prob * 40 +
        google_score * 30 +
        vt_score * 30 +
        rule_score * 20
    )

    if final_score > 70:
        return "Phishing", round(final_score, 2)
    elif final_score > 30:
        return "Suspicious", round(final_score, 2)
    else:
        return "Safe", round(final_score, 2)