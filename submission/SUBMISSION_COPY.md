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

Our core insight is that token count is dominated by output verbosity, not model choice. Left unconstrained, models emit chain-of-thought preamble that both wastes tokens and gets truncated before the real answer, failing the gate. We attack this in three stages: (1) a zero-token router — pure regex classifies each task into one of eight categories with no LLM call, unlike LLM-based routers that pay for classification and the answer; (2) strongest-allowed-model-per-category, read from ALLOWED_MODELS at runtime, because accuracy headroom is free under the gate; (3) terse, category-specific answer-only prompts that forbid preamble, with generous token caps as a truncation backstop.

The agent ships as a 48 MB linux/amd64 container honouring the /input → /output contract, starts in under 60 seconds, runs tasks concurrently within the 10-minute budget, isolates per-task failures, and always writes valid JSON. Every change is validated by a 40-task eval harness whose checkers mirror the accuracy gate (including sandboxed code execution) and report real per-category accuracy and token counts — so no leaderboard submission is a guess. MIT-licensed, public repository.

## Technologies / tags
Python · Docker · Fireworks AI · AMD Developer Cloud · asyncio · regex routing · LLM token optimization

## Cover image (16:9)
Use deck slide 1 (title) exported as PNG — dark, on-brand, readable at thumbnail size.

## Links
- GitHub: https://github.com/paulandrew12/zayndev-amd-act2-agent
- Video: (paste MP4/YouTube link)

> Reminder: leaderboard rank comes from the Docker image submission, not this text. Final token number gets locked in after tuning on the hackathon's own models.
