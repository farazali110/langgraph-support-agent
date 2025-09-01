# app/nodes/draft.py
from typing import Any, Dict, List

def _get(state: Any, key: str, default=None):
    try:
        return getattr(state, key)
    except Exception:
        return state.get(key, default)

def draft(state: Any) -> Dict[str, Any]:
    try:
        # Get input fields
        subject = _get(state, "subject", "") or ""
        description = _get(state, "description", "") or ""
        # Fallback to ticket_text for backward compatibility
        if not description and _get(state, "ticket_text"):
            description = _get(state, "ticket_text") or ""
            
        context = _get(state, "context", []) or []
        category = _get(state, "category", "General") or "General"
        escalated = bool(_get(state, "escalated", False))
        retries = int(_get(state, "retries", 0))
        review_feedback = _get(state, "review_feedback", "")
        
        # Get existing drafts and feedback for history tracking
        all_drafts = _get(state, "all_drafts", []) or []
        all_feedback = _get(state, "all_feedback", []) or []

        ctx_text = "\n".join(context) if context else "No context available."

        # If escalated, draft a short escalation placeholder
        if escalated:
            reply = "This ticket has been escalated to a human agent."
        else:
            # Create a more personalized response using subject and description
            reply = f"Hello! Thank you for contacting our support team about: '{subject}'.\n\n"
            
            if retries > 0 and review_feedback:
                # Incorporate reviewer feedback in the new draft
                reply += f"I've reviewed your issue further: '{description}'.\n\n"
            else:
                reply += f"I understand your concern: '{description}'.\n\n"
            
            # Add category-specific intro
            if category == "Billing":
                reply += "Regarding your billing inquiry, I've found the following information:\n"
            elif category == "Technical":
                reply += "Regarding your technical issue, here's what I found that might help:\n"
            elif category == "Security":
                reply += "Regarding your security concern, here's some important information:\n"
            else:
                reply += "Here's some information that may help:\n"
                
            reply += f"{ctx_text}\n\n"
            reply += "Please let me know if you need any further assistance.\n"
            reply += "Best regards,\nSupport Team"
        
        # Track all drafts and feedback for logging
        all_drafts.append(reply)
        if review_feedback:
            all_feedback.append(review_feedback)

        return {
            "draft_reply": reply,
            "escalated": escalated,
            "retries": retries,
            "all_drafts": all_drafts,
            "all_feedback": all_feedback
        }
    except Exception as e:
        return {"error": {"node": "draft", "message": str(e)}}
