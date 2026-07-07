# ZaynDev — Token-Efficient General-Purpose AI Agent

Track 1 entry for the **AMD Developer Hackathon: ACT II** (lablab.ai, July 2026).

An agent that answers tasks across 8 capability categories (factual Q&A, math,
sentiment, summarisation, NER, code debugging, logic, code generation) using
Fireworks AI models — optimised to pass the accuracy gate on the fewest tokens.

## How it works

1. **Zero-token routing** — each task is classified into a category with pure
   heuristics (regex/keywords). No LLM call is spent on routing.
2. **Model selection** — each category maps to a preference-ordered list of
   models, intersected with the runtime `ALLOWED_MODELS` list.
3. **Minimal prompting** — short single-line system prompts, no few-shot,
   per-category `max_tokens` caps, `temperature=0`.
4. **Parallel execution** — tasks run concurrently (default 8) to stay well
   inside the 10-minute budget with a 25s per-request timeout.

## Container contract

- Reads `/input/tasks.json` — `[{"task_id": "...", "prompt": "..."}, ...]`
- Writes `/output/results.json` — `[{"task_id": "...", "answer": "..."}, ...]`
- Env (injected by harness): `FIREWORKS_API_KEY`, `FIREWORKS_BASE_URL`,
  `ALLOWED_MODELS`

## Run locally

```bash
cp .env.example .env   # fill in your own key for local testing
docker build -t zayndev-agent .
./local/run_local.sh
```

## Build & push (Apple Silicon)

```bash
docker buildx build --platform linux/amd64 -t <registry>/zayndev-agent:latest --push .
```

## License

MIT
