# Agentic QA POC — Framework Replication Assignment

## Objective

Rebuild the **Planner → Creator → Publisher (PR)** slice of the agentic test
automation POC using a different agent framework than the reference
implementation (which uses LangGraph). The goal is to evaluate which
framework fits the team best before committing to one for the full
four-agent build (Planner, Creator, Runner, Reporter).

**This is a framework comparison exercise, not a copy exercise.** Study the
reference implementation's *behavior and contracts* below, then build it
your own way in your chosen framework — don't just port the LangGraph code
line-for-line, that defeats the point.

## Scope

**In scope:**
- Planner agent — turns a user story into structured test scenarios
- Creator agent — generates a Karate `.feature` file from those scenarios
- Publisher step — commits the file to a new branch and opens a PR

**Out of scope for this exercise** (full POC has these, you don't need to):
- Runner (executing the tests)
- Reporter (aggregating results)
- The feedback loop back into Planner

## Pick a framework

Any of these are free/open-source and reasonable to evaluate. Pick one per
person or pair, so we get more than one data point:

| Framework | One-line notes |
|---|---|
| **CrewAI** | Role-based agents (Planner/Creator as distinct "crew members" with goals), good if you want built-in task delegation between agents |
| **LangChain (plain, no LangGraph)** | Lower-level — you wire the sequence yourself with chains/agents, more control, more boilerplate |
| **AutoGen** | Strong for conversational multi-agent patterns; worth trying if you want Planner and Creator to "discuss" a scenario before finalizing it |
| **LlamaIndex Workflows** | Event-driven step framework, worth a look if the team likes explicit step/event modeling |

Whatever you pick, keep using a free local model via Ollama (same as the
reference build) or Gemini's free tier — no paid API spend for this
exercise.

## What each piece must do

### 1. Planner
**Input:** a user story (free text, Jira-style) + a target URL
**Output:** a list of test scenarios, each with:
```json
{
  "id": "TS-1",
  "description": "short scenario description",
  "layer": "component | contract | integration | regression",
  "role": "guest | supervisor | worker",
  "platform": "web | mobile",
  "priority": "high | medium | low"
}
```
Must handle a model returning malformed JSON without crashing — fall back
to a small default scenario list rather than throwing.

### 2. Creator
**Input:** Planner's scenario list + at least one example `.feature` file to
pattern-match against (a seed file is provided — see Reference material)
**Output:** a new Karate `.feature` file, written locally
**Must include:** a basic syntax sanity check before writing the file (at
minimum: confirm `Feature:`, `Scenario`, and Gherkin step keywords are
present) — don't write invalid output to disk.

### 3. Publisher
**Input:** Creator's validated `.feature` file
**Must do, using the GitHub REST API (or your framework's GitHub tool if it
has one):**
1. Create a new branch off the base branch (never write to it directly)
2. Commit the feature file to that branch
3. Open a PR with the user story and Planner's scenario list in the PR
   description, so a reviewer doesn't have to guess what it's testing

**Guardrails to preserve — these aren't optional:**
- Publisher must not run at all if Creator's validation failed
- The token/credential used must have write access but **no merge rights**
- If GitHub credentials aren't configured, skip gracefully and say why —
  don't fail the whole run

## Reference material

The working LangGraph reference implementation (already shared) has:
- `state.py` — the exact schema above, as a Python TypedDict
- `agents/planner.py`, `agents/creator.py`, `agents/publisher.py` — one way
  to implement this logic
- `git_ops.py` — the GitHub REST API calls Publisher needs
- `karate/features/booking_form_example.feature` — the seed pattern for
  Creator to extend
- `main.py` — the same sample user story to test against (Dream Journey
  booking form), so everyone's output is comparable

Use the same sample story and target URL (`https://dreamjourney-ce04d.web.app/`)
so results across frameworks are apples-to-apples.

## Deliverables

1. Working code in your chosen framework, runnable with `python main.py`
   equivalent
2. A short README: setup steps, what's stubbed vs real (same honesty
   standard as the reference — if something's skipped, say so, don't fake
   a result)
3. One sample PR opened against a personal/scratch repo (or a "would have
   opened PR with this branch/title/body" printout if you don't want to
   set up a live repo)
4. A half-page write-up: what was easier or harder in this framework vs.
   the LangGraph reference — this is the actual point of the exercise

## Definition of done

- [ ] Planner produces valid scenario JSON for the sample story (or falls
      back cleanly if the model output is malformed)
- [ ] Creator produces a `.feature` file that passes the basic syntax check
- [ ] Publisher either opens a real PR or clearly reports why it skipped
- [ ] Publisher never touches the base branch directly
- [ ] README and comparison write-up included
