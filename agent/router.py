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
# Tune these against the accuracy gate once we can measure.
MODEL_PREFS: dict[str, list[str]] = {
    "code_debug": ["kimi-k2p7-code", "minimax-m3", "gemma-4-31b-it"],
    "code_gen": ["kimi-k2p7-code", "minimax-m3", "gemma-4-31b-it"],
    "math": ["minimax-m3", "gemma-4-31b-it", "gemma-4-31b-it-nvfp4"],
    "logic": ["minimax-m3", "gemma-4-31b-it", "gemma-4-31b-it-nvfp4"],
    "factual": ["gemma-4-31b-it", "gemma-4-31b-it-nvfp4", "minimax-m3"],
    "summarise": ["gemma-4-26b-a4b-it", "gemma-4-31b-it", "gemma-4-31b-it-nvfp4"],
    "sentiment": ["gemma-4-26b-a4b-it", "gemma-4-31b-it", "gemma-4-31b-it-nvfp4"],
    "ner": ["gemma-4-31b-it", "gemma-4-26b-a4b-it", "minimax-m3"],
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


def pick_model(category: str, allowed: list[str]) -> str:
    allowed_list = [m.strip() for m in allowed]
    for pref in MODEL_PREFS.get(category, []):
        # exact ID (or exact tail after a provider prefix) first
        for a in allowed_list:
            if a == pref or a.endswith("/" + pref):
                return a
        # then loose substring as a fallback for renamed variants
        for a in allowed_list:
            if pref in a:
                return a
    return allowed_list[0]  # fall back to the first allowed model
