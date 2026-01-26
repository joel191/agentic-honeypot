# 🛡️ Agentic Honey-Pot for Scam Detection & Intelligence Extraction  
**GUVI – India AI Impact Buildathon**

---

## 🚀 Project Overview

This project implements an **AI-powered Agentic Honey-Pot system** that detects scam messages and autonomously engages scammers in multi-turn conversations to extract actionable intelligence.

The system is designed as a **stateful REST API**, capable of:
- Detecting scam intent without alerting the scammer
- Handing over the conversation to an autonomous AI agent
- Extracting structured scam intelligence
- Sending a **mandatory final result callback** to GUVI’s evaluation endpoint

The solution strictly adheres to the official problem statement and evaluation requirements.

---

## 🎯 Problem Statement

**Agentic Honey-Pot for Scam Detection & Intelligence Extraction**

**Objective:**
- Detect scam intent from incoming messages
- Activate an autonomous agent upon detection
- Maintain believable multi-turn conversations
- Extract high-value scam intelligence
- Return structured API responses
- Trigger a mandatory final callback for evaluation

---

## 🧠 System Architecture

### Core Modules

| File | Description |
|----|----|
| `main.py` | API entry point & orchestration |
| `detector.py` | Scam intent detection logic |
| `agent.py` | Autonomous conversational agent |
| `extractor.py` | Intelligence extraction engine |
| `memory.py` | Session-level state management |
| `callback.py` | Mandatory GUVI callback handler |
| `models.py` | Request & response schemas |
| `auth.py` | API key authentication |

---

## 🔁 Agentic Flow

1. Message received via REST API
2. Scam intent is analyzed
3. Once detected, conversation is handed over to AI agent
4. Multi-turn engagement continues
5. Scam intelligence is extracted incrementally
6. After sufficient engagement:
   - Final result callback is sent to GUVI
   - Session is safely closed

---

## 📡 API Specification

### Endpoint

POST /api/honeypot

### Authentication

Header: x-api-key: <your_api_key>


### Request Body
{
  "sessionId": "string",
  "message": {
    "sender": "scammer",
    "text": "string",
    "timestamp": "ISO-8601"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}

### Responsebody

{
  "status": "success",
  "scamDetected": true,
  "engagementMetrics": {
    "engagementDurationSeconds": 45,
    "totalMessagesExchanged": 3
  },
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": [],
    "phoneNumbers": [],
    "phishingLinks": []
  },
  "agentNotes": "Detected scam indicators: urgent, verify"
}

### Extracted Intelligence

The system extracts and categorizes:

Bank Account Numbers

UPI IDs

Phone Numbers

Phishing URLs

Suspicious Keywords

Special handling ensures:

Phone numbers are never misclassified as bank accounts

Real-world formats (+91, spaces, punctuation) are handled correctly

### 🔔 Mandatory Final Result Callback (GUVI)
Callback Endpoint
POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult

##Callback Trigger Conditions

Scam intent confirmed

Minimum multi-turn engagement (≥ 3 messages)

Callback not previously sent for the session

Callback Payload
{
  "sessionId": "string",
  "scamDetected": true,
  "totalMessagesExchanged": 4,
  "extractedIntelligence": {...},
  "agentNotes": "Scammer used urgency and redirection tactics"
}


✅ Callback is sent exactly once per session
✅ Session is auto-closed after callback

###🧪 Session Management Features

Session-based scam detection (sticky behavior)

Auto session expiry (TTL)

Manual session reset (soft / hard)

Duplicate callback prevention

Closed-session protection


# 🏗️ Tech Stack

Backend: FastAPI (Python)

State Management: In-memory sessions

HTTP Client: requests

Pattern Extraction: Regex-based NLP

Authentication: API key

## Compliance Checklist
Requirements
Public REST API	✅
API Key Security	✅
Multi-turn Engagement	✅
Autonomous Agent	✅
Structured Intelligence	✅
Explainable Output	✅
Mandatory Final Callback	✅
No Hardcoding	✅


# Conclusion

This project delivers a fully compliant, production-grade Agentic Honey-Pot system aligned exactly with the GUVI India AI Impact Buildathon problem statement and evaluation criteria.
