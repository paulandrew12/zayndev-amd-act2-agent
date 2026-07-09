"""Local scoring harness — mirrors the hackathon: accuracy gate, then total tokens.

Offline (default): validate routing accuracy + estimate prompt tokens. No API needed.
Live (--live):      call the real models, check answers, report accuracy + REAL tokens.

Usage:
    python3 eval/run_eval.py           # offline: routing + token estimate
    python3 eval/run_eval.py --live    # needs a working key in .env
"""
import argparse
import asyncio
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))   # for `agent`
sys.path.insert(0, str(HERE))   # for `checkers`

import checkers  # noqa: E402
from agent.router import classify, pick_model  # noqa: E402
from agent.prompts import build_messages, max_tokens_for  # noqa: E402

DATASET = HERE / "dataset.json"
DEFAULT_MODELS = "minimax-m3,kimi-k2p7-code,gemma-4-31b-it,gemma-4-26b-a4b-it,gemma-4-31b-it-nvfp4"


def load_env():
    envf = ROOT / ".env"
    if envf.exists():
        for line in envf.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def est_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def report_routing(tasks) -> None:
    ok = 0
    for t in tasks:
        pred, gold = classify(t["prompt"]), t["category"]
        if pred == gold:
            ok += 1
        else:
            print(f"  route MISS {t['task_id']:10s} gold={gold:11s} pred={pred}")
    print(f"\nRouting accuracy: {ok}/{len(tasks)} = {ok / len(tasks) * 100:.0f}%")


async def run_live(tasks, allowed):
    from agent.fireworks import FireworksClient
    api_key = os.environ["FIREWORKS_API_KEY"]
    base_url = os.environ["FIREWORKS_BASE_URL"]
    sem = asyncio.Semaphore(6)

    async def one(t):
        async with sem:
            cat = classify(t["prompt"])
            model = pick_model(cat, allowed)
            res = await client.chat(model, build_messages(cat, t["prompt"]), max_tokens_for(cat))
            return t, model, res

    async with FireworksClient(api_key, base_url) as client:
        return await asyncio.gather(*(one(t) for t in tasks))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="call real models (needs .env key)")
    ap.add_argument("--repeat", type=int, default=1, help="run the live eval N times and report accuracy/token spread (temp-0 is non-deterministic)")
    args = ap.parse_args()

    load_env()
    tasks = json.load(open(DATASET))
    allowed = [m.strip() for m in os.environ.get("ALLOWED_MODELS", DEFAULT_MODELS).split(",") if m.strip()]

    report_routing(tasks)

    if not args.live:
        est = sum(
            est_tokens(build_messages(classify(t["prompt"]), t["prompt"])[0]["content"] + t["prompt"])
            for t in tasks
        )
        print(f"[offline] est. prompt tokens (input only): ~{est}")
        print("[offline] run with --live once credits land for accuracy + real token counts.")
        return

    if os.environ.get("FIREWORKS_API_KEY", "PASTE_YOUR_KEY_HERE") == "PASTE_YOUR_KEY_HERE":
        print("\n[live] No API key set in .env yet — paste it and retry.")
        return

    def score_once(verbose):
        outs = asyncio.run(run_live(tasks, allowed))
        total_tokens = passed_total = 0
        cat = defaultdict(lambda: {"n": 0, "ok": 0, "tok": 0})
        for t, model, res in sorted(outs, key=lambda x: x[0]["task_id"]):
            ok = checkers.check(t, res.content)
            total_tokens += res.total_tokens
            passed_total += ok
            c = cat[t["category"]]; c["n"] += 1; c["ok"] += ok; c["tok"] += res.total_tokens
            if verbose:
                print(f"  {'OK ' if ok else 'FAIL'} {t['task_id']:10s} [{model.split('/')[-1]:24s}] tok={res.total_tokens}")
        return passed_total, total_tokens, cat

    n = len(tasks)
    if args.repeat <= 1:
        print()
        passed, toks, cat = score_once(verbose=True)
        print(f"\nAccuracy gate: {passed}/{n} = {passed / n * 100:.0f}%")
        print(f"TOTAL TOKENS (leaderboard metric): {toks}")
        print("\nPer-category:")
        for c in sorted(cat):
            s = cat[c]
            print(f"  {c:12s} acc={s['ok']}/{s['n']}  tokens={s['tok']}  (avg {s['tok'] // s['n']}/task)")
    else:
        import statistics as st
        accs, tks = [], []
        for i in range(args.repeat):
            passed, toks, _ = score_once(verbose=False)
            accs.append(passed / n * 100); tks.append(toks)
            print(f"  run {i + 1}: acc={passed}/{n} ({accs[-1]:.0f}%)  tokens={toks}")
        print(f"\nOver {args.repeat} runs (temp-0 non-determinism):")
        print(f"  accuracy: mean {st.mean(accs):.1f}%  min {min(accs):.0f}%  max {max(accs):.0f}%")
        print(f"  tokens:   mean {st.mean(tks):.0f}  min {min(tks)}  max {max(tks)}")


if __name__ == "__main__":
    main()
