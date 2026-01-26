import random

PHASE_1 = [
    "What is this about? I didn’t receive any message earlier.",
    "Why will my account be blocked?",
    "Is this really from the bank?"
]

PHASE_2 = [
    "Okay, I want to fix this. What should I do now?",
    "Can you please explain the steps again?",
    "I’m trying but I’m a bit confused."
]

PHASE_3 = [
    "The app is not opening, can you resend the UPI ID?",
    "I tried but it failed. Please share the link again.",
    "Is this the correct account number? Please confirm."
]

def generate_agent_reply(turn_count: int) -> str:
    if turn_count < 2:
        return random.choice(PHASE_1)
    elif turn_count < 5:
        return random.choice(PHASE_2)
    else:
        return random.choice(PHASE_3)
