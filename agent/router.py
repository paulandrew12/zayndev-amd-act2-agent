"""Zero-token task router: classify the prompt into one of 8 categories with
heuristics (no LLM call — classification must cost nothing), then pick the
strongest allowed model for that category.

Ranking is by raw token count, not model price, so we default to capable
models and win on prompt/output brevity instead.
"""
import re

CATEGORIES = (
    "factual", "math", "sentiment", "summarise",
    "ner", "code_debug", "logic", "code_gen",
)

# Ordered model preference per category; first match present in ALLOWED_MODELS wins.
# Serverless models (minimax/kimi) lead everywhere: per the organizers (9 Jul),
# Gemma is allowed but requires a manual on-demand deployment (~$7/hr even idle,
# 404 if not deployed) and "you don't need Gemma to pass the gate". Gemma IDs stay
# as tail fallbacks — if they 404, model_candidates() falls through automatically.
MODEL_PREFS: dict[str, list[str]] = {
    "code_debug": ["kimi-k2p7-code", "minimax-m3", "gemma-4-31b-it"],
    "code_gen": ["kimi-k2p7-code", "minimax-m3", "gemma-4-31b-it"],
    "math": ["minimax-m3", "kimi-k2p7-code", "gemma-4-31b-it"],
    "logic": ["minimax-m3", "kimi-k2p7-code", "gemma-4-31b-it"],
    "factual": ["minimax-m3", "kimi-k2p7-code", "gemma-4-31b-it"],
    "summarise": ["minimax-m3", "kimi-k2p7-code", "gemma-4-26b-a4b-it"],
    "sentiment": ["minimax-m3", "kimi-k2p7-code", "gemma-4-26b-a4b-it"],
    "ner": ["minimax-m3", "kimi-k2p7-code", "gemma-4-31b-it"],
}

_CODE_MARKERS = re.compile(
    r"```|def |class |function\s|=>|;\s*$|\breturn\b|\bimport\b|\bconsole\.log\b|\bprintf?\b", re.M
)

_NUMWORD = r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|dozen|hundred|thousand|half|twice|double)"

_MATH = re.compile(
    r"\b(?:calculat|how (?:much|many)|percent|per cent|discount|interest|average|mean of|sum of"
    r"|total|product of|area|perimeter|volume|speed|distance|ratio|divisible|remainder|value of"
    r"|square|cube|km/h|per (?:hour|day|year|second))\b|%"
)

_LOGIC = re.compile(
    r"\ball\s+\w+\s+are\s+\w+"                                   # syllogism
    r"|\bnecessarily\b"
    r"|\bwhich\s+(?:box|one|colou?r|person|house|door|cup|hat)\b"
    r"|\b(?:not in the|is not in|neither|taller than|shorter than|older than|younger than"
    r"|faster than|to the (?:left|right) of|seated|sits? next to|directly (?:above|below))\b"
    r"|\bif\b.*\bthen\b"
    r"|\b(?:constraint|puzzle|deduce|who (?:is|owns|lives|sits)|order of|must be true|logically)\b"
)


def _has_number(p: str) -> bool:
    return bool(re.search(r"\d", p) or re.search(r"\b" + _NUMWORD + r"\b", p))


def classify(prompt: str) -> str:
    p = prompt.lower()
    has_code = bool(_CODE_MARKERS.search(prompt))

    if has_code and re.search(r"\b(bug|fix|debug|error|incorrect|wrong|broken|crash|fails?|opposite|doesn'?t work)\b", p):
        return "code_debug"
    if re.search(r"\b(write|implement|create|generate|complete)\b.*\b(function|class|method|script|program|code)\b", p) or (
        has_code and re.search(r"\b(write|implement|complete)\b", p)
    ):
        return "code_gen"
    if re.search(r"\b(sentiment|positive|negative|neutral|tone of|feeling|emotion)\b", p) and re.search(
        r"\b(classif\w*|label|review|tweet|comment|text below|following|feeling|tone)\b", p
    ):
        return "sentiment"
    if re.search(r"\b(summari[sz]e|summary|condense|tl;?dr|shorten|in (?:one|two|three|\d+) (?:sentence|word|bullet|line))\b", p):
        return "summarise"
    if re.search(r"\b(extract|identify|list)\b.*\b(entit|person|people|organi[sz]ation|location|date)s?\b", p) or (
        "named entit" in p
    ):
        return "ner"
    if _MATH.search(p) and _has_number(p):
        return "math"
    if _LOGIC.search(p):
        return "logic"
    return "factual"


def model_candidates(category: str, allowed: list[str]) -> list[str]:
    """Preference-ordered list of allowed models for a category, best first, with
    every other allowed model appended as a last-resort fallback. The agent tries
    them in order so one flaky/unavailable model never zeroes out a task."""
    allowed_list = [m.strip() for m in allowed if m.strip()]
    ordered: list[str] = []
    for pref in MODEL_PREFS.get(category, []):
        for a in allowed_list:  # exact / tail match first
            if (a == pref or a.endswith("/" + pref)) and a not in ordered:
                ordered.append(a)
        for a in allowed_list:  # then loose substring
            if pref in a and a not in ordered:
                ordered.append(a)
    for a in allowed_list:  # remaining allowed models as final fallbacks
        if a not in ordered:
            ordered.append(a)
    return ordered or allowed_list


def pick_model(category: str, allowed: list[str]) -> str:
    cands = model_candidates(category, allowed)
    return cands[0] if cands else (allowed[0] if allowed else "")
