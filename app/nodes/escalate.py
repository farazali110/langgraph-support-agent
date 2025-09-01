# app/nodes/escalate.py
from typing import Any, Dict, List
import csv
import os
import json
from datetime import datetime

ESCALATION_FILE = "data/escalations.csv"

def _get(state: Any, key: str, default=None):
    try:
        return getattr(state, key)
    except Exception:
        return state.get(key, default)

def escalate(state: Any) -> Dict[str, Any]:
    try:
        os.makedirs("data", exist_ok=True)
        
        # Get all information for the escalation log
        subject = _get(state, "subject", "")
        description = _get(state, "description", "")
        ticket_text = _get(state, "ticket_text", "")
        category = _get(state, "category", "")
        context = _get(state, "context", []) or []
        
        # Get all drafts and feedback for comprehensive logging
        all_drafts = _get(state, "all_drafts", []) or []
        all_feedback = _get(state, "all_feedback", []) or []
        
        # Fallback to the current draft if all_drafts is empty
        if not all_drafts and _get(state, "draft_reply"):
            all_drafts.append(_get(state, "draft_reply"))
            
        # Fallback to the current feedback if all_feedback is empty
        if not all_feedback and _get(state, "review_feedback"):
            all_feedback.append(_get(state, "review_feedback"))
        
        retries = str(_get(state, "retries", 0))
        timestamp = datetime.now().isoformat()
        
        # Create a detailed escalation record
        row = [
            subject,
            description or ticket_text,
            category,
            "; ".join(context),
            json.dumps(all_drafts),  # Store all drafts as JSON string
            json.dumps(all_feedback),  # Store all feedback as JSON string
            retries,
            timestamp
        ]
        
        # Check if the file exists to decide whether to write headers
        write_header = not os.path.exists(ESCALATION_FILE)
        
        # Write to CSV
        with open(ESCALATION_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow([
                    "subject", 
                    "description", 
                    "category", 
                    "context", 
                    "all_drafts", 
                    "all_feedback", 
                    "retries",
                    "timestamp"
                ])
            writer.writerow(row)

        return {"final_reply": "Escalated to human agent", "escalated": True}
    except Exception as e:
        return {"error": {"node": "escalate", "message": str(e)}, "final_reply": "Error occurred during escalation", "escalated": True}
