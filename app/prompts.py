# app/prompts.py

CLASSIFIER_PROMPT = """
Classify the following ticket into one of the categories:
- Billing
- Technical
- Security
- General

Ticket: {ticket_text}
"""

RETRIEVAL_PROMPT = """
Retrieve the most relevant documents for this ticket category.
Category: {category}
"""

DRAFT_PROMPT = """
You are an AI assistant. Generate a polite, helpful draft reply to the customer.
Use the retrieved context if available.
Ticket: {ticket_text}
Context: {context}
"""

REVIEW_PROMPT = """
You are a reviewer ensuring policy compliance.

Rules:
- No refunds or financial guarantees
- No sensitive/personal info
- Must be polite and clear

Draft:
{draft}

Return JSON:
{"status": "approved", "final_reply": "..."} OR {"status": "rejected", "feedback": "..."}
"""
