"""
Runner agent.

Scopes and triggers execution of the generated feature. In production this
dispatches a GitHub Actions job that runs Maven/Karate; for the POC it runs
Maven locally if a pom.xml exists, and otherwise reports honestly that
execution was skipped rather than faking a result.
"""

import os
import subprocess
from state import PipelineState


def runner_node(state: PipelineState) -> PipelineState:
    if not state.get("validation_passed"):
        return {**state, "run_result": {
            "status": "skipped",
            "reason": "Creator's output failed local validation -- nothing to run",
        }}

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pom_path = os.path.join(project_root, "pom.xml")

    if not os.path.isfile(pom_path):
        return {**state, "run_result": {
            "status": "skipped",
            "reason": "No pom.xml found -- wire up a Maven/Karate project to actually execute. "
                      "Feature file was generated and validated at: " + state["feature_path"],
        }}

    tag_expr = "--tags @component,@regression"
    try:
        result = subprocess.run(
            ["mvn", "-q", "test", f"-Dkarate.options={tag_expr} {state['feature_path']}"],
            capture_output=True, text=True, timeout=300, cwd=project_root,
        )
        return {**state, "run_result": {
            "status": "passed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "output_tail": (result.stdout or result.stderr)[-2000:],
        }}
    except subprocess.TimeoutExpired:
        return {**state, "run_result": {"status": "timeout", "reason": "Maven run exceeded 300s"}}
