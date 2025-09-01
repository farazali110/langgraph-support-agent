# app/nodes/classify.py
from typing import Any, Dict, Optional

def _get(state: Any, key: str, default=None):
    try:
        return getattr(state, key)
    except Exception:
        return state.get(key, default)

def classify(state: Any) -> Dict[str, Any]:
    try:
        # Get both subject and description
        subject = (_get(state, "subject", "") or "").lower()
        description = (_get(state, "description", "") or "").lower()
        
        # Fallback to ticket_text for backward compatibility
        if not description and _get(state, "ticket_text"):
            description = (_get(state, "ticket_text", "") or "").lower()
            
        # Combine subject and description for classification
        combined_text = f"{subject} {description}".lower()
        
        if any(word in combined_text for word in ["invoice", "refund", "payment", "bill", "billing"]):
            category = "Billing"
        elif any(word in combined_text for word in ["server", "error", "bug", "crash", "latency", "api"]):
            category = "Technical"
        elif any(word in combined_text for word in ["hack", "phish", "breach", "password", "2fa", "unauthorized"]):
            category = "Security"
        else:
            category = "General"

        # ensure escalated present (propagate existing or false)
        escalated = bool(_get(state, "escalated", False))
        retries = int(_get(state, "retries", 0))

        return {"category": category, "escalated": escalated, "retries": retries}
    except Exception as e:
        return {"error": {"node": "classify", "message": str(e)}}
