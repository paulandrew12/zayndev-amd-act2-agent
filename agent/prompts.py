"""Per-category prompt builders. Every token here is scored — keep prompts minimal
AND suppress the model's chain-of-thought preamble, which wastes tokens and (worse)
gets truncated before the real answer, failing the accuracy gate.

Design rules:
- Terse system line (prompt tokens are scored too).
- Explicitly forbid restating the question / "thinking out loud".
- Tight max_tokens per category as a backstop.
- Keep just enough working on math/logic to preserve accuracy.
"""

_SYSTEM: dict[str, str] = {
    "factual": "Answer directly in at most 3 sentences. No preamble.",
    "math": "Reply with at most two short lines of working, then a final line 'Answer: <number>'. Do not restate the question or re-check.",
    "sentiment": "Reply with exactly one word: positive, negative, or neutral.",
    "summarise": "Output only the summary in the requested length/format. No preamble.",
    "ner": "Output only the entities, one per line as 'text - label' (person/org/location/date).",
    "code_debug": "Reply with one short line naming the bug, then a single ```python block with the fixed code. No reasoning, no extra text.",
    "logic": "Reply with at most two short lines of reasoning, then a final line 'Answer: <result>'. Do not restate the question.",
    "code_gen": "Output only a single ```python block with the function. No explanation, no reasoning, before or after.",
}

# max_tokens is a TRUNCATION BACKSTOP, not a target. Obedient instruct models stop
# early and cost few tokens regardless of the cap; a generous cap just prevents a
# verbose model from being cut off mid-answer (which fails the accuracy gate).
# The token WIN comes from the prompt making the model concise, not from a tight cap.
_MAX_TOKENS: dict[str, int] = {
    "factual": 256,
    "math": 384,
    "sentiment": 64,
    "summarise": 256,
    "ner": 200,
    "code_debug": 768,
    "logic": 384,
    "code_gen": 768,
}


def build_messages(category: str, prompt: str) -> list[dict]:
    return [
        {"role": "system", "content": _SYSTEM[category]},
        {"role": "user", "content": prompt},
    ]


def max_tokens_for(category: str) -> int:
    return _MAX_TOKENS[category]
