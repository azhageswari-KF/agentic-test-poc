"""
Wires Planner -> Creator -> Runner -> Reporter into a single LangGraph.

This is intentionally a straight line for the POC. The feedback loop
(Reporter's flaky/defect signal back into Planner) is a deliberate Phase 2
addition once the straight-line version is proven reliable.
"""

from langgraph.graph import StateGraph, END
from state import PipelineState
from agents.planner import planner_node
from agents.creator import creator_node
from agents.runner import runner_node
from agents.reporter import reporter_node


def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("planner", planner_node)
    graph.add_node("creator", creator_node)
    graph.add_node("runner", runner_node)
    graph.add_node("reporter", reporter_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "creator")
    graph.add_edge("creator", "runner")
    graph.add_edge("runner", "reporter")
    graph.add_edge("reporter", END)

    return graph.compile()
