# app/state.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict
@dataclass
class GraphState:
    # Input
    ticket_id: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    ticket_text: Optional[str] = None  # For backward compatibility

    # Pipeline state
    category: Optional[str] = None
    context: List[str] = field(default_factory=list)   # retrieved docs / context snippets
    draft_reply: Optional[str] = None
    
    # Track all drafts and feedback for logging
    all_drafts: List[str] = field(default_factory=list)
    all_feedback: List[str] = field(default_factory=list)

    # Review & control
    review_decision: Optional[str] = None   # "approved" / "rejected"
    review_feedback: Optional[str] = None
    final_reply: Optional[str] = None
    retries: int = 0
    escalated: bool = False
    error: Optional[Dict[str, str]] = None  # To capture any errors during processing

    # ✅ Add this
    done: bool = False  # Marks workflow completion so graph exits cleanly
