"""
Creator agent.

Retrieves existing .feature files as patterns to extend, generates a new
Karate .feature file from the Planner's scenarios, and runs a lightweight
local syntax check before writing anything to disk.

NOTE on the syntax check: a production Creator should dry-run the generated
file through Karate's own parser (the real, authoritative check -- see the
Maven-based validation step in validate_with_karate() below, disabled by
default since it needs the Karate/Maven toolchain installed). The regex
check here is a cheap POC-level stand-in so the graph is runnable with zero
Java/Maven setup.
"""

import os
import re
import subprocess
from llm import get_llm
from state import PipelineState

FEATURES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "karate", "features")
GENERATED_DIR = os.path.join(FEATURES_DIR, "generated")

SYSTEM_PROMPT = """You are a Karate DSL test author. Given a list of test
scenarios and one or more example .feature files, generate ONE new Karate
.feature file that covers all the given scenarios.

Rules:
- Extend the style, structure, and step phrasing of the example file(s) below
  rather than inventing new patterns.
- Use a Background for shared setup (e.g. `driver` for UI flows).
- Tag every Scenario with its layer and role/platform, e.g. @component @guest-web.
- Output ONLY the .feature file content. No markdown fences, no commentary."""


def _retrieve_patterns() -> str:
    """Naive retrieval for the POC: concatenate existing .feature files.
    Swap for an embedding/keyword index once the pattern library grows
    past a handful of files."""
    if not os.path.isdir(FEATURES_DIR):
        return "(no existing patterns found -- this will be the first feature file)"

    patterns = []
    for root, _, files in os.walk(FEATURES_DIR):
        for f in files:
            if f.endswith(".feature"):
                with open(os.path.join(root, f), "r", encoding="utf-8") as fh:
                    patterns.append(f"# Example: {f}\n{fh.read()}")
    return "\n\n".join(patterns) if patterns else "(no existing patterns found)"


def _local_syntax_check(feature_text: str) -> list:
    """Cheap sanity check, NOT a substitute for karate.parse(). Flags the
    most common ways a generated file is unusable."""
    errors = []
    if not re.search(r"^\s*Feature:", feature_text, re.MULTILINE):
        errors.append("Missing 'Feature:' declaration")
    if not re.search(r"^\s*Scenario", feature_text, re.MULTILINE):
        errors.append("No 'Scenario' found")
    if not re.search(r"^\s*(Given|When|Then|And|\*)\s", feature_text, re.MULTILINE):
        errors.append("No Gherkin step keywords found")
    return errors


def validate_with_karate(feature_path: str) -> list:
    """Real validation step: dry-run the feature through Karate/Maven.
    Requires a Maven project with the karate dependency configured.
    Left as an optional call -- wire this in once the Maven project exists."""
    try:
        result = subprocess.run(
            ["mvn", "-q", "test", f"-Dkarate.options=--dry-run {feature_path}"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            return [result.stdout[-2000:] or result.stderr[-2000:]]
        return []
    except FileNotFoundError:
        return ["Maven not found on PATH -- skipped real Karate dry-run"]
    except Exception as e:
        return [f"Karate dry-run could not run: {e}"]


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:50]


def creator_node(state: PipelineState) -> PipelineState:
    llm = get_llm()
    patterns = _retrieve_patterns()
    scenarios_text = "\n".join(f"- [{s['layer']}/{s['role']}/{s['platform']}] {s['description']}" for s in state["scenarios"])

    prompt = f"{SYSTEM_PROMPT}\n\nExample pattern(s):\n{patterns}\n\nTarget URL:\n{state['target_url']}\n\nScenarios to cover:\n{scenarios_text}"
    feature_text = llm.invoke(prompt).content.strip()
    feature_text = re.sub(r"^```(gherkin|karate)?|```$", "", feature_text, flags=re.MULTILINE).strip()

    errors = _local_syntax_check(feature_text)

    os.makedirs(GENERATED_DIR, exist_ok=True)
    slug = _slugify(state["jira_ticket"][:40])
    feature_path = os.path.join(GENERATED_DIR, f"{slug}.feature")

    if not errors:
        with open(feature_path, "w", encoding="utf-8") as f:
            f.write(feature_text)
    else:
        feature_path = ""  # don't write invalid output to the repo

    return {
        **state,
        "feature_text": feature_text,
        "feature_path": feature_path,
        "validation_passed": len(errors) == 0,
        "validation_errors": errors,
    }
