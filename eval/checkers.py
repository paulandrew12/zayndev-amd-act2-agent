"""Accuracy checkers that mimic the hackathon's accuracy gate locally.

The real gate is an LLM-judge on unseen variants; these deterministic checkers let
us measure accuracy offline for free. `keyword` is our stand-in for the fuzzy
categories (factual/summarise) — swap in a real LLM judge once credits land.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def _nums(text: str) -> list[float]:
    return [float(x) for x in re.findall(r"-?\d[\d,]*\.?\d*", text.replace(",", ""))]


def check_numeric(answer: str, reference, tol: float = 1e-6) -> bool:
    # Prefer a number after an "Answer:" marker; else fall back to the last number.
    tail = answer.rsplit("answer:", 1)[-1] if "answer:" in answer.lower() else answer
    candidates = _nums(tail) or _nums(answer)
    if not candidates:
        return False
    return any(abs(c - float(reference)) <= tol for c in candidates[-2:])


def check_label(answer: str, reference: str) -> bool:
    return reference.lower() in answer.lower()


def check_contains_all(answer: str, reference: list) -> bool:
    a = answer.lower()
    return all(str(item).lower() in a for item in reference)


def check_keyword(answer: str, reference: list, threshold: float = 0.5) -> bool:
    a = answer.lower()
    hits = sum(1 for k in reference if str(k).lower() in a)
    return hits / len(reference) >= threshold


def _extract_code(answer: str) -> str:
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", answer, re.S)
    return blocks[-1] if blocks else answer


def check_code(answer: str, reference: dict, timeout: float = 8.0) -> bool:
    """Run the model's code against reference asserts in an isolated subprocess.

    Note: executes model-generated code. Runs in a temp dir with a hard timeout;
    only ever run this on trusted eval data, never on untrusted submissions.
    """
    code = _extract_code(answer)
    script = code + "\n\n" + "\n".join(reference["tests"]) + "\nprint('EVAL_OK')\n"
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "cand.py"
        p.write_text(script)
        try:
            r = subprocess.run(
                [sys.executable, str(p)],
                capture_output=True, text=True, timeout=timeout, cwd=d,
            )
        except subprocess.TimeoutExpired:
            return False
        return r.returncode == 0 and "EVAL_OK" in r.stdout


def check(task: dict, answer: str) -> bool:
    kind = task["check"]
    ref = task["reference"]
    if kind == "numeric":
        return check_numeric(answer, ref)
    if kind == "label":
        return check_label(answer, ref)
    if kind == "contains_all":
        return check_contains_all(answer, ref)
    if kind == "keyword":
        return check_keyword(answer, ref, task.get("threshold", 0.5))
    if kind == "code":
        return check_code(answer, ref)
    raise ValueError(f"unknown check kind: {kind}")
