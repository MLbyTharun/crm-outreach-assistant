import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from agent.state import FollowUpState
from agent.nodes import make_generate_node, review_emails, send_emails


def build_graph(llm):
    """
    Builds and compiles the LangGraph follow-up agent.
    Takes the FollowUpGenerator instance so nodes can use it.
    """
    builder = StateGraph(FollowUpState)

    # Add nodes
    builder.add_node("generate_followups", make_generate_node(llm))
    builder.add_node("review_emails", review_emails)
    builder.add_node("send_emails", send_emails)

    # Add edges
    builder.add_edge(START, "generate_followups")
    builder.add_edge("generate_followups", "review_emails")
    builder.add_edge("review_emails", "send_emails")
    builder.add_edge("send_emails", END)

    return builder.compile(checkpointer=MemorySaver())