# app/nodes/refine.py
from typing import Any, Dict
from app.nodes.retrieve import retrieve
from app.nodes.draft import draft as generate_draft

MAX_RETRIES = 2

def _get(state: Any, key: str, default=None):
    try:
        return getattr(state, key)
    except Exception:
        return state.get(key, default)

def refine(state: Any) -> Dict[str, Any]:
    """
    Increment retries, use review_feedback to adjust retrieval,
    re-run retrieval and draft. Return merged updates.
    """
    try:
        current_retries = int(_get(state, "retries", 0))
        new_retries = current_retries + 1
        
        # Get previous feedback for context refinement
        review_feedback = _get(state, "review_feedback", "")

        # If exceeding retries, set escalated flag and return; escalate node will finalize
        if new_retries >= MAX_RETRIES:
            return {
                "retries": new_retries,
                "escalated": True,
                "final_reply": "This ticket has been escalated to a human agent.",
                "done": True  # NEW field to tell graph to stop
            }


        # Create a refined state that incorporates the feedback
        refined_state = dict(state) if hasattr(state, "items") else state.__dict__.copy()
        
        # Preserve existing drafts and feedback for logging
        all_drafts = _get(state, "all_drafts", []) or []
        all_feedback = _get(state, "all_feedback", []) or []

        # Apply feedback to improve context retrieval
        # Note: The retrieve node will now use this feedback to prioritize better documents
        
        # Run retrieval with the enhanced state (now with feedback)
        retrieve_update = retrieve(refined_state)  # returns {"context": ...}
        
        # Create a new pseudo state with the updated context
        pseudo_state = refined_state.copy()
        pseudo_state.update(retrieve_update)
        
        # Generate new draft with the refined context
        draft_update = generate_draft(pseudo_state)  # returns {"draft_reply": ...}

        # Merge all updates
        merged = {
            "retries": new_retries, 
            "escalated": bool(_get(state, "escalated", False)),
            "all_drafts": all_drafts,
            "all_feedback": all_feedback
        }
        merged.update(retrieve_update)
        merged.update(draft_update)
        
        return merged
    except Exception as e:
        return {"error": {"node": "refine", "message": str(e)}}
