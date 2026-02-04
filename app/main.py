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


@app.post("/api/honeypot", response_model=ScamResponse)
def honeypot_endpoint(
    data: Optional[ScamRequest] = Body(default=None),
    api_key: str = Depends(verify_api_key)
):
    session = sessions[data.sessionId]

        # --------------------------------------------------
    # GUVI Endpoint Tester compatibility (NO BODY)
    # --------------------------------------------------
    if data is None:
        return ScamResponse(
            status="success",
            scamDetected=False,
            engagementMetrics=EngagementMetrics(
                engagementDurationSeconds=0,
                totalMessagesExchanged=0
            ),
            extractedIntelligence=ExtractedIntelligence(
                bankAccounts=[],
                upiIds=[],
                phishingLinks=[],
                phoneNumbers=[]
            ),
            agentNotes="Honeypot endpoint reachable and authenticated"
        )

    # --------------------------------------------------
    # 0. Session TTL expiry
    # --------------------------------------------------
    if time.time() - session["start_time"] > SESSION_TTL:
        del sessions[data.sessionId]
        session = sessions[data.sessionId]

    # --------------------------------------------------
    # 0.1 Block closed sessions
    # --------------------------------------------------
    if session.get("closed"):
        return ScamResponse(
            status="session_closed",
            scamDetected=True,
            engagementMetrics=EngagementMetrics(
                engagementDurationSeconds=0,
                totalMessagesExchanged=len(session["messages"])
            ),
            extractedIntelligence=ExtractedIntelligence(
                bankAccounts=session["intelligence"]["bankAccounts"],
                upiIds=session["intelligence"]["upiIds"],
                phishingLinks=session["intelligence"]["phishingLinks"],
                phoneNumbers=session["intelligence"]["phoneNumbers"]
            ),
            agentNotes="Session already finalized"
        )

    # --------------------------------------------------
    # Store incoming message
    # --------------------------------------------------
    session["messages"].append(data.message)

    duration = int(time.time() - session["start_time"])
    total_messages = len(session["messages"])

    # --------------------------------------------------
    # 1. Scam detection (message-level)
    # --------------------------------------------------
    result = detect_scam_intent(data.message.text)

    if result["is_scam"]:
        session["scamDetected"] = True

    # --------------------------------------------------
    # 2. Intelligence extraction (ONLY scammer messages)
    # --------------------------------------------------
    if data.message.sender == "scammer":
        extracted = extract_intelligence(data.message.text)

        for key, values in extracted.items():
            if key not in session["intelligence"]:
                session["intelligence"][key] = []

            for value in values:
                if value not in session["intelligence"][key]:
                    session["intelligence"][key].append(value)

    # --------------------------------------------------
    # 3. Force scam if financial entities exist
    # --------------------------------------------------
    if (
        session["intelligence"]["bankAccounts"]
        or session["intelligence"]["upiIds"]
        or session["intelligence"]["phoneNumbers"]
    ):
        session["scamDetected"] = True

    scam_detected = session["scamDetected"]

    # --------------------------------------------------
    # 4. Agent notes (explainable & clean)
    # --------------------------------------------------
    if scam_detected:
        if result["matched_keywords"]:
            agent_notes = (
                "Detected scam indicators: "
                + ", ".join(result["matched_keywords"])
            )
        else:
            agent_notes = (
                "Scam confirmed based on financial redirection patterns"
            )
    else:
        agent_notes = "No scam indicators detected"

    # --------------------------------------------------
    # 5. Autonomous agent reply
    # --------------------------------------------------
    if scam_detected:
        agent_reply = generate_agent_reply(total_messages)
        session["messages"].append({
            "sender": "user",
            "text": agent_reply,
            "timestamp": str(time.time())
        })

    # --------------------------------------------------
    # 6. GUVI callback (ONLY ONCE)
    # --------------------------------------------------
    if scam_detected and total_messages >= 3 and not session.get("callbackSent"):
        send_final_callback(data.sessionId, session)
        session["callbackSent"] = True
        session["closed"] = True  # auto-close after callback

    # --------------------------------------------------
    # 7. Final response
    # --------------------------------------------------
    return ScamResponse(
        status="success",
        scamDetected=scam_detected,
        engagementMetrics=EngagementMetrics(
            engagementDurationSeconds=duration,
            totalMessagesExchanged=total_messages
        ),
        extractedIntelligence=ExtractedIntelligence(
            bankAccounts=session["intelligence"]["bankAccounts"],
            upiIds=session["intelligence"]["upiIds"],
            phishingLinks=session["intelligence"]["phishingLinks"],
            phoneNumbers=session["intelligence"]["phoneNumbers"]
        ),
        agentNotes=agent_notes
    )


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

