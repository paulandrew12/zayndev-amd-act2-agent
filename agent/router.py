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


def classify(prompt: str) -> str:
    p = prompt.lower()
    has_code = bool(_CODE_MARKERS.search(prompt))

    if has_code and re.search(r"\b(bug|fix|debug|error|incorrect|wrong|broken|why does(n't| not)? .* work)\b", p):
        return "code_debug"
    if re.search(r"\b(write|implement|create|generate)\b.*\b(function|class|method|script|program|code)\b", p) or (
        has_code and re.search(r"\b(write|implement|complete)\b", p)
    ):
        return "code_gen"
    if re.search(r"\b(sentiment|positive|negative|neutral|tone of|feeling|emotion)\b", p) and re.search(
        r"\b(classify|label|review|tweet|comment|text below|following)\b", p
    ):
        return "sentiment"
    if re.search(r"\b(summari[sz]e|summary|condense|tl;?dr|shorten|in \d+ (sentence|word|bullet))\b", p):
        return "summarise"
    if re.search(r"\b(extract|identify|list)\b.*\b(entit|person|people|organi[sz]ation|location|date)s?\b", p) or (
        "named entit" in p
    ):
        return "ner"
    if re.search(r"\d+(\.\d+)?\s*(%|percent)|\bcalculate|how (much|many)|total\b|\bsum\b|\baverage\b|\bprofit|projection", p) and re.search(r"\d", p):
        return "math"
    if re.search(r"\b(if .* then|constraint|puzzle|deduce|who (is|owns|lives)|seated|order of|must be true|logically)\b", p):
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
