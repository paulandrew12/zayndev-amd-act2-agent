"""Track 1 entrypoint: read /input/tasks.json, answer all tasks, write /output/results.json."""
import asyncio
import json
import os
import sys

from agent.fireworks import FireworksClient
from agent.router import classify, pick_model
from agent.prompts import build_messages, max_tokens_for

INPUT_PATH = os.environ.get("TASKS_PATH", "/input/tasks.json")
OUTPUT_PATH = os.environ.get("RESULTS_PATH", "/output/results.json")
CONCURRENCY = int(os.environ.get("CONCURRENCY", "8"))


async def solve(client: FireworksClient, allowed: list[str], task: dict, sem: asyncio.Semaphore) -> dict:
    task_id = task.get("task_id", "")
    prompt = task.get("prompt", "")
    async with sem:
        try:
            category = classify(prompt)
            model = pick_model(category, allowed)
            messages = build_messages(category, prompt)
            result = await client.chat(model=model, messages=messages, max_tokens=max_tokens_for(category))
            answer = result.content
        except Exception as e:  # never let one task sink the run
            print(f"[warn] task {task_id} failed: {e}", file=sys.stderr)
            answer = ""
    return {"task_id": task_id, "answer": answer}


async def run() -> int:
    api_key = os.environ["FIREWORKS_API_KEY"]
    base_url = os.environ["FIREWORKS_BASE_URL"]
    allowed = [m.strip() for m in os.environ["ALLOWED_MODELS"].split(",") if m.strip()]

    with open(INPUT_PATH) as f:
        tasks = json.load(f)

    sem = asyncio.Semaphore(CONCURRENCY)
    async with FireworksClient(api_key=api_key, base_url=base_url) as client:
        results = await asyncio.gather(*(solve(client, allowed, t, sem) for t in tasks))

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(list(results), f)
    print(f"[done] {len(results)} tasks -> {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
