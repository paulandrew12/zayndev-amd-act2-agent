# Submission Form Copy — ZaynDev, Track 1
Paste-ready text for the lablab "Submit Project" form. Fill the final leaderboard token number where noted before submitting.

## Submission Title (≤50 chars)
`ZaynDev — Token-Efficient General-Purpose Agent`
(47 chars)

## Short Description / Summary (≤255 chars)
`A general-purpose AI agent for Track 1 that passes the accuracy gate on the fewest tokens: zero-token regex routing, strongest-model-per-category, and answer-only prompts that kill the chain-of-thought verbosity dominating the token bill.`
(238 chars)

## Long Description (≥100 words)
ZaynDev is a general-purpose agent for Track 1's eight capability categories — factual Q&A, math, sentiment, summarisation, NER, code debugging, logic, and code generation — engineered for one metric: total tokens spent clearing the accuracy gate.

Our core insight is that token count is dominated by output verbosity, not model choice. Left unconstrained, models emit chain-of-thought preamble that both wastes tokens and gets truncated before the real answer, failing the gate — and reasoning models can silently burn the entire token budget "thinking" and return no answer at all. We attack this in four stages: (1) a zero-token router — pure regex classifies each task into one of eight categories with no LLM call, unlike LLM-based routers that pay for classification and the answer; (2) strongest-allowed-model-per-category, read from ALLOWED_MODELS at runtime, because accuracy headroom is free under the gate; (3) terse, category-specific answer-only prompts that forbid preamble (measured: removing them drops accuracy AND raises tokens); (4) reasoning switched off at the API level with a graceful fallback if the proxy rejects the parameter — on real models this alone cut total tokens 29% at identical accuracy.

Measured on live models (minimax-m3 / kimi-k2p7-code): 100% accuracy across repeated full-suite runs, ~170 tokens per task end-to-end. The agent ships as a linux/amd64 container under 200 MB honouring the /input → /output contract, starts in seconds, runs tasks concurrently within the 10-minute budget, retries across allowed models so one flaky model never zeroes a task, and always writes valid JSON. Every change is validated by a 40-task eval harness whose checkers mirror the accuracy gate (including sandboxed code execution) — so no leaderboard submission is a guess. MIT-licensed, public repository; image auto-published by CI.

## Technologies / tags
Python · Docker · Fireworks AI · AMD Developer Cloud · asyncio · regex routing · LLM token optimization

## Cover image (16:9)
Use deck slide 1 (title) exported as PNG — dark, on-brand, readable at thumbnail size.

## Links
- GitHub: https://github.com/paulandrew12/zayndev-amd-act2-agent
- **Docker image (Track 1 submission field): `ghcr.io/paulandrew12/zayndev-agent:latest`**
- Video: submission/ZaynDev-Track1-demo.mp4 (2:29, ready — upload or link)

> Reminder: leaderboard rank comes from the Docker image submission, not this text. Final token number gets locked in after tuning on the hackathon's own models.
