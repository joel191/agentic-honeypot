import time
from collections import defaultdict

SESSION_TTL = 300  # 5 minutes

def new_session():
    return {
        "start_time": time.time(),
        "messages": [],
        "scamDetected": False,
        "callbackSent": False,   # ✅ REQUIRED
        "closed": False,
        "intelligence": {
            "bankAccounts": [],
            "upiIds": [],
            "phoneNumbers": [],
            "phishingLinks": [],
            "suspiciousKeywords": []
        }
    }

sessions = defaultdict(new_session)
