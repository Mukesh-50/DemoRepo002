# Build the graph: a supervisor in the middle, with four agents around it
#
#   START -> (test already exists?) -> yes -> END
#                                   -> no  -> read_test_case -> supervisor
#
#   supervisor -> explorer  -> supervisor
#              -> generator -> supervisor
#              -> reviewer  -> supervisor
#              -> healer    -> supervisor
#              -> finish    -> ask_create_pr (pauses and asks you)
#
#   ask_create_pr -> yes -> create_pull_request -> END
#                 -> no  -> END

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

from workflow.agents import explorer, generator, healer, reviewer, supervisor
from workflow.decisions import check_create_pr, check_test_exists, route_to_agent
from workflow.nodes import ask_create_pr, create_pull_request, read_test_case
from workflow.state import TestState

graph = StateGraph(TestState)

# Nodes
graph.add_node("read_test_case", read_test_case)
graph.add_node("supervisor", supervisor)
graph.add_node("explorer", explorer)
graph.add_node("generator", generator)
graph.add_node("reviewer", reviewer)
graph.add_node("healer", healer)
graph.add_node("ask_create_pr", ask_create_pr)
graph.add_node("create_pull_request", create_pull_request)

# Edges
graph.add_conditional_edges(START, check_test_exists, {"skip": END, "new": "read_test_case"})
graph.add_edge("read_test_case", "supervisor")

# The supervisor picks the next agent
graph.add_conditional_edges("supervisor", route_to_agent, {
    "explorer": "explorer",
    "generator": "generator",
    "reviewer": "reviewer",
    "healer": "healer",
    "finish": "ask_create_pr",
})

# Every agent reports back to the supervisor
for agent in ["explorer", "generator", "reviewer", "healer"]:
    graph.add_edge(agent, "supervisor")

graph.add_conditional_edges("ask_create_pr", check_create_pr, {"create": "create_pull_request", "skip": END})
graph.add_edge("create_pull_request", END)

# A checkpointer is needed so the graph can pause (interrupt) and resume later
app = graph.compile(checkpointer=MemorySaver())
