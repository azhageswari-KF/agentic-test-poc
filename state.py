"""
Shared state schema passed between every agent node in the LangGraph.

This is the one contract all four agents read from and write to -- it's the
"structured plan artifact" pattern discussed in design: no agent re-derives
intent from scratch, they only extend what the previous agent produced.
"""

from typing import TypedDict, List, Dict, Any


class TestScenario(TypedDict):
    id: str
    description: str
    layer: str      # component | contract | integration | regression
    role: str        # e.g. guest, supervisor, worker
    platform: str    # web | mobile
    priority: str    # high | medium | low


class PipelineState(TypedDict, total=False):
    # ---- input ----
    jira_ticket: str        # raw user story / acceptance criteria text
    target_url: str         # application under test

    # ---- Planner output ----
    scenarios: List[TestScenario]

    # ---- Creator output ----
    feature_text: str
    feature_path: str
    validation_passed: bool
    validation_errors: List[str]

    publish_result: Dict[str, Any]

    # ---- Runner output ----
    run_result: Dict[str, Any]

    # ---- Reporter output ----
    report_text: str
    report_path: str
