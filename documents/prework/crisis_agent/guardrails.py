"""Safety boundaries for the crisis-response agent.

The agent provides general legal INFORMATION and routes families to attorneys.
It never provides legal ADVICE about a specific case. Gloo's server-side
guardrails are the backstop (HTTP 403 -> GuardrailBlock); the stage prompts
enforce the boundary by construction, and every output carries a disclaimer.
"""

NOT_LEGAL_ADVICE_EN = (
    "I am not a lawyer and this is not legal advice. Immigration law changes "
    "often and every case is different. Please review everything here with a "
    "qualified immigration attorney as soon as possible."
)

NOT_LEGAL_ADVICE_ES = (
    "No soy abogado y esto no es asesoramiento legal. Las leyes de inmigración "
    "cambian con frecuencia y cada caso es diferente. Por favor revise todo "
    "esto con un abogado de inmigración calificado lo antes posible."
)

SYSTEM_BOUNDARY = """You are assisting a pastor who is helping an immigrant family in crisis.
Hard rules you must follow:
1. Provide general legal INFORMATION only. Never give legal advice, never predict
   how a specific case will turn out, never recommend a legal strategy.
2. Always urge the family to consult a qualified immigration attorney promptly.
3. Ground factual claims in the sources provided to you; cite them by name.
4. If asked for advice on a specific person's case, state the boundary briefly
   and route to an attorney instead.
5. Be calm, clear, and compassionate. Avoid frightening or sensational language.
6. Respond in the family's language (Spanish if the intake says Spanish) unless
   asked otherwise.
"""

# Phrases that must never appear in agent output. Checked before display.
BANNED_PHRASES = [
    "you should plead",
    "your case will",
    "you will win",
    "guaranteed",
]


def check_output(text):
    """Return a list of problems found in generated text (empty = clean)."""
    problems = []
    lowered = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            problems.append(f"banned phrase: {phrase!r}")
    return problems


def disclaimer(language="es"):
    return NOT_LEGAL_ADVICE_ES if language == "es" else NOT_LEGAL_ADVICE_EN
