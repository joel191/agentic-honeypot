from fastapi import FastAPI, Depends, HTTPException
from app.auth import verify_api_key
from app.models import (
    ScamRequest,
    ScamResponse,
    EngagementMetrics,
    ExtractedIntelligence,
)
from app.memory import sessions
from app.detector import detect_scam_intent
from app.agent import generate_agent_reply
from app.extractor import extract_intelligence
from app.callback import send_final_callback
import time
from fastapi import FastAPI, Depends
import time

from fastapi import Body
from typing import Optional

app = FastAPI(title="Agentic Honey-Pot API")

SESSION_TTL = 300  # 5 minutes

@app.get("/api/honeypot")
def honeypot_get(
    api_key: str = Depends(verify_api_key)
):
    return {
        "status": "success",
        "message": "Honeypot endpoint reachable",
        "note": "GET request accepted for endpoint validation"
    }


from typing import Optional
from fastapi import Body

@app.post("/api/honeypot")
def honeypot_endpoint(
    data: Optional[ScamRequest] = Body(default=None),
    api_key: str = Depends(verify_api_key)
):
    # --------------------------------------------------
    # ✅ GUVI Endpoint Tester (NO BODY)
    # --------------------------------------------------
    if data is None:
        return {
            "status": "success",
            "message": "Honeypot endpoint reachable and authenticated"
        }

    # --------------------------------------------------
    # Session handling (SAFE)
    # --------------------------------------------------
    session = sessions[data.sessionId]

    # TTL expiry
    if time.time() - session["start_time"] > SESSION_TTL:
        del sessions[data.sessionId]
        session = sessions[data.sessionId]

    # Block closed sessions
    if session.get("closed"):
        return {
            "status": "session_closed",
            "scamDetected": True,
            "note": "Session already finalized"
        }

    # Store message
    session["messages"].append(data.message)
    total_messages = len(session["messages"])
    duration = int(time.time() - session["start_time"])

    # Scam detection
    result = detect_scam_intent(data.message.text)
    if result["is_scam"]:
        session["scamDetected"] = True

    # Intelligence extraction
    if data.message.sender == "scammer":
        extracted = extract_intelligence(data.message.text)
        for key, values in extracted.items():
            for value in values:
                if value not in session["intelligence"][key]:
                    session["intelligence"][key].append(value)

    # Force scam if financial entities exist
    if (
        session["intelligence"]["bankAccounts"]
        or session["intelligence"]["upiIds"]
        or session["intelligence"]["phoneNumbers"]
    ):
        session["scamDetected"] = True

    scam_detected = session["scamDetected"]

    # Agent notes
    agent_notes = (
        "Detected scam indicators: " + ", ".join(result["matched_keywords"])
        if scam_detected and result["matched_keywords"]
        else "Scam confirmed based on financial redirection patterns"
        if scam_detected
        else "No scam indicators detected"
    )

    # Callback (once)
    if scam_detected and total_messages >= 3 and not session.get("callbackSent"):
        send_final_callback(data.sessionId, session)
        session["callbackSent"] = True
        session["closed"] = True

    # Final response (NO response_model)
    return {
        "status": "success",
        "scamDetected": scam_detected,
        "engagementMetrics": {
            "engagementDurationSeconds": duration,
            "totalMessagesExchanged": total_messages
        },
        "extractedIntelligence": session["intelligence"],
        "agentNotes": agent_notes
    }



# ==================================================
# 🔁 RESET SESSION ENDPOINT (soft / hard)
# ==================================================
@app.post("/api/reset-session")
def reset_session(
    sessionId: str,
    mode: str = "hard",  # hard | soft
    reason: str = "manual_reset",
    api_key: str = Depends(verify_api_key)
):
    if sessionId not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    if mode == "soft":
        sessions[sessionId]["intelligence"] = {
            "bankAccounts": [],
            "upiIds": [],
            "phoneNumbers": [],
            "phishingLinks": [],
            "suspiciousKeywords": []
        }
        sessions[sessionId]["scamDetected"] = False
        sessions[sessionId]["messages"] = []
        sessions[sessionId]["start_time"] = time.time()
        sessions[sessionId]["callbackSent"] = False
        sessions[sessionId]["closed"] = False
    else:
        del sessions[sessionId]

    return {
        "status": "reset",
        "sessionId": sessionId,
        "mode": mode,
        "reason": reason
    }


# ==================================================
# 🧪 DEBUG SESSION VIEWER (optional)
# ==================================================
@app.get("/api/session/{sessionId}")
def view_session(
    sessionId: str,
    api_key: str = Depends(verify_api_key)
):
    if sessionId not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return sessions[sessionId]

@app.get("/")
def root():
    return {
        "message": "Agentic Honey-Pot API is running",
        "health": "/health",
        "endpoint": "/api/honeypot"
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "agentic-honeypot",
        "timestamp": int(time.time())
    }

