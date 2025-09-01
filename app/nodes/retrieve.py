# app/nodes/retrieve.py
from typing import Any, Dict, List

# Expanded knowledge base with more specific documents
MOCK_KB = {
    "Billing": [
        "Billing guide: invoices and refunds.",
        "How to update payment method.",
        "Refund policy and processing times.",
        "Subscription management and billing cycles."
    ],
    "Technical": [
        "Technical guide: troubleshooting server 500 errors.",
        "API error handling and logs.",
        "Common connection problems and solutions.",
        "Performance optimization tips.",
        "System requirements and compatibility."
    ],
    "Security": [
        "Security guide: change password and enable 2FA.",
        "Incident response playbook.",
        "Account protection best practices.",
        "Data encryption and privacy policy."
    ],
    "General": [
        "General FAQ and office hours info.",
        "Support contact details.",
        "Product documentation and user guides.",
        "Company policies and service level agreements."
    ]
}

def _get(state: Any, key: str, default=None):
    try:
        return getattr(state, key)
    except Exception:
        return state.get(key, default)

def _filter_docs_by_query(docs: List[str], query: str) -> List[str]:
    """Filter documents based on relevance to query"""
    if not query:
        return docs
    
    # Simple keyword matching - in a real system, this would use vector similarity
    query_terms = query.lower().split()
    scored_docs = []
    
    for doc in docs:
        score = sum(1 for term in query_terms if term in doc.lower())
        scored_docs.append((doc, score))
    
    # Return docs sorted by relevance score, highest first
    return [doc for doc, score in sorted(scored_docs, key=lambda x: x[1], reverse=True)]

def retrieve(state: Any) -> Dict[str, Any]:
    try:
        category = _get(state, "category", "General") or "General"
        subject = _get(state, "subject", "") or ""
        description = _get(state, "description", "") or ""
        # Fallback to ticket_text for backward compatibility
        if not description and _get(state, "ticket_text"):
            description = _get(state, "ticket_text") or ""
            
        review_feedback = _get(state, "review_feedback", "")
        escalated = bool(_get(state, "escalated", False))
        retries = int(_get(state, "retries", 0))
        
        # Get base documents for the category
        docs = MOCK_KB.get(category, [])
        
        # Build search query from subject, description and reviewer feedback if available
        query = f"{subject} {description}"
        if review_feedback and retries > 0:
            # Incorporate feedback into retrieval for refinement
            query += f" {review_feedback}"
            
        # Filter and rank documents based on query relevance
        filtered_docs = _filter_docs_by_query(docs, query)
        
        return {"context": filtered_docs, "escalated": escalated, "retries": retries}
    except Exception as e:
        return {"error": {"node": "retrieve", "message": str(e)}}
