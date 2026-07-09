"""Track 1 entrypoint: read /input/tasks.json, answer all tasks, write /output/results.json.

Hardened against the ways a Track 1 submission scores ZERO:
- Always writes a complete, valid results.json (one entry per input task).
- Per-task model fallback: if the preferred model errors/times out, try the next
  allowed model before giving up — one flaky model can't sink a batch.
- Global run-budget guard: on approaching the 10-minute limit, write whatever
  finished rather than getting killed with no output.
- No task can throw out of the batch; the worst case is an empty answer.
"""
import asyncio
import json
import os
import sys

from agent.fireworks import FireworksClient
from agent.router import classify, model_candidates
from agent.prompts import build_messages, max_tokens_for

INPUT_PATH = os.environ.get("TASKS_PATH", "/input/tasks.json")
OUTPUT_PATH = os.environ.get("RESULTS_PATH", "/output/results.json")
CONCURRENCY = int(os.environ.get("CONCURRENCY", "8"))
# Leave slack under the 10-minute hard limit so we always flush results.
RUN_BUDGET_SEC = float(os.environ.get("RUN_BUDGET_SEC", "540"))


async def solve(client, allowed, task, sem, results):
    task_id = task.get("task_id", "") if isinstance(task, dict) else ""
    prompt = task.get("prompt", "") if isinstance(task, dict) else ""
    answer = ""
    if prompt:
        category = classify(prompt)
        messages = build_messages(category, prompt)
        mt = max_tokens_for(category)
        async with sem:
            for model in model_candidates(category, allowed):
                try:
                    res = await client.chat(model=model, messages=messages, max_tokens=mt)
                    if res.content.strip():
                        answer = res.content
                        break
                except Exception as e:  # try the next allowed model
                    print(f"[warn] task {task_id} model {model} failed: {e}", file=sys.stderr)
                    continue
    results[task_id] = answer


async def run() -> int:
    api_key = os.environ["FIREWORKS_API_KEY"]
    base_url = os.environ["FIREWORKS_BASE_URL"]
    allowed = [m.strip() for m in os.environ["ALLOWED_MODELS"].split(",") if m.strip()]

    with open(INPUT_PATH) as f:
        tasks = json.load(f)

    results: dict[str, str] = {}
    sem = asyncio.Semaphore(CONCURRENCY)
    async with FireworksClient(api_key=api_key, base_url=base_url) as client:
        coros = [solve(client, allowed, t, sem, results) for t in tasks]
        try:
            await asyncio.wait_for(asyncio.gather(*coros, return_exceptions=True), timeout=RUN_BUDGET_SEC)
        except asyncio.TimeoutError:
            print("[warn] run budget hit — flushing partial results", file=sys.stderr)

    # One entry per input task, in original order; unfinished tasks get "".
    out = [{"task_id": (t.get("task_id", "") if isinstance(t, dict) else ""),
            "answer": results.get(t.get("task_id", "") if isinstance(t, dict) else "", "")}
           for t in tasks]
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(out, f)
    answered = sum(1 for r in out if r["answer"])
    print(f"[done] {answered}/{len(out)} answered -> {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
