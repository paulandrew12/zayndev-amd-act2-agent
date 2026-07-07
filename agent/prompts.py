"""Per-category prompt builders. Every token here is scored — keep prompts minimal.

Rules of thumb:
- No few-shot examples unless the accuracy gate forces it.
- Short imperative system lines; the task prompt already carries the details.
- Cap max_tokens per category so verbose models can't leak tokens.
"""

_SYSTEM: dict[str, str] = {
    "factual": "Answer accurately and concisely.",
    "math": "Solve step by step briefly, then end with: Answer: <result>",
    "sentiment": "Classify sentiment (positive/negative/neutral) with a one-sentence justification.",
    "summarise": "Follow the requested format and length exactly.",
    "ner": "Extract entities with labels (person/org/location/date). Output only the list.",
    "code_debug": "Identify the bug briefly, then give the corrected code.",
    "logic": "Reason briefly, then end with: Answer: <result>",
    "code_gen": "Output only the code with minimal comments.",
}

_MAX_TOKENS: dict[str, int] = {
    "factual": 300,
    "math": 500,
    "sentiment": 80,
    "summarise": 300,
    "ner": 200,
    "code_debug": 700,
    "logic": 500,
    "code_gen": 700,
}


def build_messages(category: str, prompt: str) -> list[dict]:
    return [
        {"role": "system", "content": _SYSTEM[category]},
        {"role": "user", "content": prompt},
    ]


def max_tokens_for(category: str) -> int:
    return _MAX_TOKENS[category]
