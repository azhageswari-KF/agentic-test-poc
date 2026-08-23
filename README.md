# Agentic SDLC QA Automation -- POC

A minimal LangGraph pipeline demonstrating Planner -> Creator -> Runner -> Reporter
against one sample user story for https://dreamjourney-ce04d.web.app/

## What's real vs. stubbed in this POC

| Piece | Status |
|---|---|
| Planner (LLM call, JSON scenario output) | Real -- calls your local Ollama model |
| Creator (LLM call, Karate feature generation) | Real -- calls the model, writes `.feature` file |
| Creator's syntax validation | **Stubbed**: regex-based sanity check only. Swap in `validate_with_karate()` in `agents/creator.py` once you have a Maven/Karate project -- that's the real, authoritative check |
| Runner (Maven/Karate execution) | **Conditional**: runs `mvn test` if a `pom.xml` exists in this folder, otherwise reports "skipped" honestly rather than faking a pass |
| Reporter | Real -- writes a Markdown report to `reports/` |
| Jira sync, GitHub PR creation, flaky-test history | Not built yet -- next increments after this loop is proven |

## Setup

1. Create and activate a virtual environment, then:
   ```
   pip install -r requirements.txt
   ```
2. Install [Ollama](https://ollama.com) and pull a model:
   ```
   ollama pull llama3.1:8b
   ```
3. Copy `.env.example` to `.env` (defaults are fine to start).

## Run

```
python main.py
```

This runs the sample user story in `main.py` through all four agents and
prints the final report. A generated `.feature` file lands in
`karate/features/generated/`, and the full report is also saved under
`reports/`.

## The sample user story

Guest books a travel package via the booking form on the Dream Journey site
(name, phone, place, people count, address, message -> "Success" confirmation).
See `main.py` for the full acceptance criteria used as Planner's input.

## Wiring in real execution

To make Runner actually execute the generated Karate feature:
1. Add a Maven project (`pom.xml`) with the `karate` dependency in this folder.
2. Point it at `karate/features/generated/`.
3. Confirm the CSS selectors in the seed pattern (`karate/features/booking_form_example.feature`)
   against the live DOM -- they're illustrative placeholders, not inspected
   selectors, since this POC only fetched the page's rendered text content.

## Next increments (not in this POC)

- Feedback loop: Reporter's results back into Planner (see `graph.py` comment)
- GitHub App-scoped commit + PR instead of writing straight to the local `karate/` folder
- Real Karate dry-run validation in `creator.py` instead of the regex stand-in
- Flaky-vs-real-vs-infra classification in Runner (currently pass/fail/skip only)
