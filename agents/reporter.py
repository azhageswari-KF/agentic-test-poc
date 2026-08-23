"""
Reporter agent.

Aggregates what Planner/Creator/Runner produced into one Markdown summary.
In production this is also where Jira sync and flaky/defect classification
would happen -- kept out of the POC scope on purpose.
"""

import os
from datetime import datetime
from state import PipelineState

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


def reporter_node(state: PipelineState) -> PipelineState:
    scenarios = state.get("scenarios", [])
    run_result = state.get("run_result", {})

    lines = [
        f"# Test Run Report",
        f"_Generated {datetime.now().isoformat(timespec='seconds')}_",
        "",
        f"**User story:** {state['jira_ticket']}",
        f"**Target URL:** {state['target_url']}",
        "",
        "## Planned scenarios",
    ]
    for s in scenarios:
        lines.append(f"- `{s['id']}` [{s['layer']}/{s['role']}/{s['platform']}/{s['priority']}] {s['description']}")

    lines += [
        "",
        "## Creator output",
        f"- Validation passed: **{state.get('validation_passed')}**",
    ]
    if state.get("validation_errors"):
        lines.append(f"- Errors: {state['validation_errors']}")
    if state.get("feature_path"):
        lines.append(f"- Feature file: `{state['feature_path']}`")

    lines += [
        "",
        "## Runner output",
        f"- Status: **{run_result.get('status')}**",
    ]
    if run_result.get("reason"):
        lines.append(f"- Reason: {run_result['reason']}")

    report_text = "\n".join(lines)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_path = os.path.join(REPORTS_DIR, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    return {**state, "report_text": report_text, "report_path": report_path}
