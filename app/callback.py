import requests

GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

def send_final_callback(
    session_id: str,
    session_data: dict
):
    payload = {
        "sessionId": session_id,
        "scamDetected": session_data["scamDetected"],
        "totalMessagesExchanged": len(session_data["messages"]),
        "extractedIntelligence": session_data["intelligence"],
        "agentNotes": "Scammer used urgency and redirection tactics"
    }

    try:
        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload,
            timeout=5
        )
        return response.status_code
    except Exception as e:
        print("Callback failed:", e)
        return None
