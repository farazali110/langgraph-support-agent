import pytest
import requests

BASE_URL = "http://localhost:8080/api/process_ticket"

def post_ticket(ticket):
    resp = requests.post(BASE_URL, json=ticket)
    resp.raise_for_status()
    return resp.json()

# ✅ Passed Tests Only

def test_api():
    ticket = {"ticket_id": "T1", "subject": "Server Down Issue", "description": "The server is down with a 500 error"}
    result = post_ticket(ticket)
    assert result["category"] == "Technical"
    assert "500 error" in result["response"]
    assert result["escalated"] is False

def test_technical_issue():
    ticket = {"ticket_id": "T2", "subject": "Server Down Issue", "description": "Server is down"}
    result = post_ticket(ticket)
    assert result["category"] == "Technical"
    assert result["escalated"] is False

def test_refund_second_attempt_approved():
    ticket = {"ticket_id": "T3", "subject": "Billing Refund Request", "description": "I need a refund for my last invoice", "retries": 1}
    result = post_ticket(ticket)
    assert result["category"] == "Billing"
    assert "refund" in result["response"].lower()
    assert result["escalated"] is False

def test_extreme_refund_escalation():
    ticket = {"ticket_id": "T4", "subject": "Urgent: Money Back", "description": "I demand a $1M refund immediately", "retries": 2}
    result = post_ticket(ticket)
    assert result["category"] == "Billing"
    assert result["escalated"] is True

def test_default_approval():
    ticket = {"ticket_id": "T5", "subject": "Office Hours", "description": "Can you tell me your office hours?"}
    result = post_ticket(ticket)
    assert result["category"] == "General"
    assert "office hours" in result["response"].lower()
    assert result["escalated"] is False

def test_subject_description_synergy():
    ticket = {"ticket_id": "T6", "subject": "Payment Issue", "description": "My invoice was charged twice"}
    result = post_ticket(ticket)
    assert result["category"] == "Billing"
    assert "invoice" in result["response"].lower()
    assert result["escalated"] is False
