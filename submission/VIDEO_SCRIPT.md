# Demo Video Script — ZaynDev, Track 1
**Target length: ~3:00 (hard cap 5:00). Record in Chrome + terminal. Screen-record 1080p.**

Rule of thumb: talk fast, show real things running. Judges have seen 100 decks — they reward a working demo and one sharp idea.

---

### 0:00–0:18 · Hook (talking head or title slide 1)
> "Track 1 is a token race. Pass an accuracy gate, then whoever answers on the fewest tokens wins. I'm building ZaynDev — a general-purpose agent engineered for exactly one number: total tokens. Solo, from Nairobi."

**On screen:** Title slide.

### 0:18–0:45 · The problem + the insight (slides 2 → 3)
> "Everyone reaches for a fancy router to pick a cheaper model. But the token bill isn't dominated by which model you pick — it's dominated by how much the model *says*. Left alone, these models think out loud before answering. That preamble wastes tokens on every task, and worse — it gets truncated by the token cap before the real answer arrives, so you fail the gate."

**On screen:** Slide 3 — linger on the truncated-answer example card.

### 0:45–1:35 · Architecture (slide 4, then flip to code)
> "So the design attacks verbosity in three stages. One — a zero-token router: pure regex sorts each task into one of eight categories. No LLM call, so routing costs nothing — while an LLM-based router pays for the classification *and* the answer. Two — pick the strongest allowed model per category, read live from ALLOWED_MODELS. Accuracy headroom is free under the gate. Three — a terse, answer-only prompt per category that forbids preamble."

**On screen:** Slide 4, then open `agent/router.py` (show the regex classify), then `agent/prompts.py` (show the answer-only system prompts). Keep it moving.

### 1:35–2:20 · Live proof (terminal)
> "And I don't guess — I measure. Here's my eval harness: forty labelled tasks across all eight categories, with checkers that mirror the accuracy gate, including sandboxed execution for the code tasks."

**On screen:** run `python3 eval/run_eval.py --live` — let the per-category accuracy + TOTAL TOKENS print.

> "Real API, real token counts, per category. This is the exact loop I use to trade tokens against accuracy before spending a single leaderboard submission."

**On screen (optional):** show the container running the contract — `./local/run_local.sh` producing valid `/output/results.json`.

### 2:20–2:45 · The edge (slide 7)
> "The reference approach most teams will submit sends the raw prompt and lets the model ramble — its clever router even ties 'just always use the cheap model.' The untapped lever is verbosity, and that's the one I pull hardest."

**On screen:** Slide 7 comparison.

### 2:45–3:05 · Engineering + close (slides 8 → 10)
> "It ships as a 48-megabyte linux/amd64 container, starts in under a minute, writes valid JSON every time, and isolates failures so one bad task never sinks the run. MIT-licensed, public repo. Pass the gate, spend the fewest tokens. That's ZaynDev."

**On screen:** Slide 8 briefly, end on slide 10 (repo URL held on screen 3–4s).

---

## Recording checklist
- [ ] Close noisy tabs; clean desktop; hide the .env file.
- [ ] Do a dry run of the `--live` command first so it's warm and fast on camera.
- [ ] Keep total under 5:00 — aim 3:00. Trim dead air in editing.
- [ ] Export MP4 ≤ 300MB, or upload to YouTube/Drive and paste the link.
- [ ] Speak in English (submission requirement).
