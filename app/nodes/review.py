from typing import Any, Dict

SENSITIVE_PATTERNS = ["password", "ssn", "credit card"]
FINANCIAL_KEY = "refund"

def _get(state: Any, key: str, default=None):
    try:
        return getattr(state, key)
    except Exception:
        return state.get(key, default)

def review(state: Any) -> Dict[str, Any]:
    """
    Implements:
      - Technical issues -> approve immediately
      - Billing + 'refund':
          retries == 0 -> reject
          retries == 1 -> approve
          retries >= 2 -> escalate (i.e., reject and escalated flag)
      - Sensitive info in draft -> reject with feedback
      - Default -> approve
    Always returns 'escalated' (bool).
    """
    try:
        # Get subject, description, and fallback to ticket_text
        subject = (_get(state, "subject", "") or "").lower()
        description = (_get(state, "description", "") or "").lower()
        text = (_get(state, "ticket_text", "") or "").lower() if not description else description
        
        # Combined text for better policy evaluation
        combined_text = f"{subject} {description}".lower()
        
        draft = (_get(state, "draft_reply", "") or "").lower()
        retries = int(_get(state, "retries", 0))
        escalated = bool(_get(state, "escalated", False))
        category = _get(state, "category", "")
        
        # Get existing lists for tracking
        all_drafts = _get(state, "all_drafts", []) or []
        all_feedback = _get(state, "all_feedback", []) or []

        # Default outputs
        out = {
            "escalated": escalated, 
            "retries": retries,
            "all_drafts": all_drafts,
            "all_feedback": all_feedback
        }

        # Block sensitive info
        if any(p in draft for p in SENSITIVE_PATTERNS):
            feedback = "Remove any sensitive information from the reply."
            out.update({
                "review_decision": "rejected",
                "review_feedback": feedback,
                "final_reply": None
            })
            all_feedback.append(feedback)
            return out

        # Technical issues: approve
        if category == "Technical" or any(p in combined_text for p in ["server", "error", "bug", "crash", "latency", "api"]):
            out.update({
                "review_decision": "approved",
                "final_reply": _get(state, "draft_reply")
            })
            return out
        
        # Billing refund logic
        if category == "Billing" or FINANCIAL_KEY in combined_text:
            # extreme monetary demand escalate
            if ("$" in combined_text) or ("demand" in combined_text):
                feedback = "Do not promise refunds; escalate this ticket to human support."
                out.update({
                    "review_decision": "rejected",
                    "review_feedback": feedback,
                    "escalated": True,
                    "final_reply": "Escalated to human agent"
                })
                all_feedback.append(feedback)
                return out

            # normal refund: reject first, approve on retry == 1
            if retries == 0:
                feedback = "Do not promise refunds. Offer to check billing policy and next steps."
                out.update({
                    "review_decision": "rejected",
                    "review_feedback": feedback,
                    "final_reply": None
                })
                all_feedback.append(feedback)
                return out
            elif retries == 1:
                out.update({
                    "review_decision": "approved",
                    "final_reply": _get(state, "draft_reply")
                })
                return out
            else:
                # If we've tried twice and still not successful, escalate
                feedback = "After multiple attempts, this refund request requires human attention."
                out.update({
                    "review_decision": "rejected",
                    "review_feedback": feedback,
                    "escalated": True
                })
                all_feedback.append(feedback)
                return out

        # ✅ Default fallback: approve safely
        out.update({
            "review_decision": "approved",
            "review_feedback": "Auto-approved: no issues detected.",
            "final_reply": _get(state, "draft_reply"),
            "escalated": False
        })

        return out
    except Exception as e:
        return {"error": {"node": "review", "message": str(e)}}
