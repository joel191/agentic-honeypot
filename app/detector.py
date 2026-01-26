HIGH_RISK_KEYWORDS = [
    "account blocked",
    "account suspended",
    "verify immediately",
    "share otp",
    "share upi",
    "click link",
    "kyc update",
    "payment failed"
]

LOW_RISK_KEYWORDS = [
    "urgent",
    "immediately",
    "verify",
    "refund",
    "limited time",
    "bank"
]

def detect_scam_intent(message_text: str) -> dict:
    text = message_text.lower()

    high_risk_matches = [kw for kw in HIGH_RISK_KEYWORDS if kw in text]
    low_risk_matches = [kw for kw in LOW_RISK_KEYWORDS if kw in text]

    # Scam logic:
    # - Any high-risk keyword → scam
    # - OR 2+ low-risk keywords → scam
    is_scam = bool(high_risk_matches) or len(low_risk_matches) >= 2

    matched_keywords = high_risk_matches + low_risk_matches

    return {
        "is_scam": is_scam,
        "matched_keywords": matched_keywords
    }
