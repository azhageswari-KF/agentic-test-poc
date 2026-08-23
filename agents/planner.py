"""
Planner agent.

Reads the raw user story (jira_ticket) and produces a structured list of
test scenarios: which coverage layer each belongs to, and which role/
platform it applies to. This is the one output worth a human glance before
Creator generates any code, since every downstream agent inherits it.
"""

import json
import re
from llm import get_llm
from state import PipelineState

SYSTEM_PROMPT = """You are a QA test planner. Given a user story and a target
application URL, break it into concrete test scenarios.

Return ONLY a JSON array, no markdown fences, no preamble. Each element:
{
  "id": "TS-1",
  "description": "short scenario description",
  "layer": "component" | "contract" | "integration" | "regression",
  "role": "guest" | "supervisor" | "worker",
  "platform": "web" | "mobile",
  "priority": "high" | "medium" | "low"
}

Cover the happy path and at least one negative/edge case. Do not invent
fields outside this schema."""


def _fallback_scenarios(jira_ticket: str) -> list:
    """Used only if the model doesn't return parseable JSON, so the POC
    never hard-crashes on a flaky local model response."""
    return [
        {
            "id": "TS-1",
            "description": f"Happy path for: {jira_ticket[:80]}",
            "layer": "component",
            "role": "guest",
            "platform": "web",
            "priority": "high",
        },
        {
            "id": "TS-2",
            "description": "Submitting the form with required fields empty shows a validation error",
            "layer": "component",
            "role": "guest",
            "platform": "web",
            "priority": "medium",
        },
    ]


def planner_node(state: PipelineState) -> PipelineState:
    llm = get_llm()
    prompt = f"{SYSTEM_PROMPT}\n\nUser story:\n{state['jira_ticket']}\n\nTarget URL:\n{state['target_url']}"

    raw = llm.invoke(prompt).content.strip()
    # Strip accidental markdown fences before parsing
    cleaned = re.sub(r"^```(json)?|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        scenarios = json.loads(cleaned)
        assert isinstance(scenarios, list) and len(scenarios) > 0
    except Exception:
        scenarios = _fallback_scenarios(state["jira_ticket"])

    return {**state, "scenarios": scenarios}
