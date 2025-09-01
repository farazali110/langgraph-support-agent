from langgraph.graph import StateGraph, END
from app.state import GraphState
from app.nodes.classify import classify
from app.nodes.retrieve import retrieve
from app.nodes.draft import draft
from app.nodes.review import review
from app.nodes.refine import refine, MAX_RETRIES
from app.nodes.escalate import escalate


def build_graph():
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("classify", classify)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("draft", draft)
    workflow.add_node("review", review)
    workflow.add_node("refine", refine)
    workflow.add_node("escalate", escalate)

    # Entry point
    workflow.set_entry_point("classify")

    # === Conditional edges with error handling ===
    workflow.add_conditional_edges(
        "classify",
        lambda s: "end" if getattr(s, "error", None) else "retrieve",
        {"retrieve": "retrieve", "end": END}
    )

    workflow.add_conditional_edges(
        "retrieve",
        lambda s: "end" if getattr(s, "error", None) else "draft",
        {"draft": "draft", "end": END}
    )

    workflow.add_conditional_edges(
        "draft",
        lambda s: "end" if getattr(s, "error", None) else "review",
        {"review": "review", "end": END}
    )

    workflow.add_conditional_edges(
        "review",
        lambda s: (
            "end" if getattr(s, "error", None)
            else "end" if getattr(s, "review_decision", None) == "approved"
            else "end" if getattr(s, "review_decision", None) == "rejected" and getattr(s, "sensitive", False)
            else "refine" if getattr(s, "review_decision", None) == "rejected" and int(getattr(s, "retries", 0)) < MAX_RETRIES
            else "escalate"
        ),
        {"refine": "refine", "escalate": "escalate", "end": END}
    )

    workflow.add_conditional_edges(
        "refine",
        lambda s: (
            "end" if getattr(s, "error", None)
            else "review" if int(getattr(s, "retries", 0)) < MAX_RETRIES
            else "escalate"
        ),
        {"review": "review", "escalate": "escalate", "end": END}
    )

    workflow.add_edge("escalate", END)

    # ✅ Compile workflow with recursion limit
    graph = workflow.compile()
    return graph


# Export compiled graph as 'app' for LangGraph
app = build_graph()  # <- Changed from 'graph' to 'app'


if __name__ == "__main__":
    # Manual driver for quick testing
    samples = [
        {"subject": "Server Error", "description": "The server is down with a 500 error"},
        {"subject": "Refund Request", "description": "I need a refund for my last invoice"},
        {"subject": "Urgent: Money Back", "description": "I demand a $1M refund immediately"},
        {"subject": "General Question", "description": "Can you tell me your office hours?"}
    ]

    class StateWrapper:
        def __init__(self, data):
            if hasattr(data, "items"):
                self.__dict__.update(dict(data))
            else:
                self.__dict__.update(data.__dict__)
        def __repr__(self):
            return str(self.__dict__)

    for sample in samples:
        print(f"\n=== Ticket: {sample['subject']} - {sample['description']} ===")
        result = app.invoke(  # <- Updated from 'graph.invoke' to 'app.invoke'
            {
                "subject": sample['subject'],
                "description": sample['description'],
                "ticket_text": sample['description'],
            },
            config={"recursion_limit": 50}
        )

        state = StateWrapper(result)
        print("category:", getattr(state, "category", None))
        print("retries:", getattr(state, "retries", 0))
        print("review_decision:", getattr(state, "review_decision", None))
        print("final_reply:", getattr(state, "final_reply", None))
        print("escalated:", getattr(state, "escalated", False))
