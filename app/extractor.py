import re

UPI_REGEX = r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b"
URL_REGEX = r"https?://[^\s]+"

PHONE_REGEX = r"(?:\+91[-\s]?)?[6-9]\d{9}"
BANK_REGEX = r"\b\d{11,18}\b"

SUSPICIOUS_KEYWORDS = [
    "urgent", "immediately", "verify", "account blocked",
    "account suspended", "kyc", "payment failed",
    "click link", "limited time", "refund"
]

def extract_intelligence(text: str) -> dict:
    text_lower = text.lower()

    phones = re.findall(PHONE_REGEX, text)
    banks = re.findall(BANK_REGEX, text)

    # Normalize phone numbers to last 10 digits
    phone_digits = {p[-10:] for p in phones}

    # 🚫 Remove phone numbers from bank accounts
    clean_banks = [
        b for b in banks
        if b[-10:] not in phone_digits
    ]

    return {
        "upiIds": re.findall(UPI_REGEX, text),
        "bankAccounts": clean_banks,
        "phishingLinks": re.findall(URL_REGEX, text),
        "phoneNumbers": phones,
        "suspiciousKeywords": [
            kw for kw in SUSPICIOUS_KEYWORDS if kw in text_lower
        ]
    }
