Support Ticket Resolution Agent (LangGraph)

This project implements a Support Ticket Resolution Agent using the LangGraph
 framework. The agent simulates a real-world support workflow with classification, review, refinement, and escalation steps.

It demonstrates how to orchestrate multi-step reasoning loops and apply business rules in an AI-powered support assistant.

🚀 Features

Automatic Classification → Classifies tickets into categories (Technical, Billing, etc.).

Review Loop → Applies business rules and may reject, approve, or request refinement.

Multi-Step Retry Handling → Supports retries before making a final decision.

Sensitive Info Blocking → Immediately rejects tickets containing sensitive data.

Escalation Handling → Extreme or unresolvable requests are escalated to a human manager.

Final Response Generation → Returns structured results with category, decision, reply, and escalation flag.

⚙️ Setup Instructions
1. Clone Repository
git clone https://github.com/farazali110/langgraph-support-agent.git
cd langgraph-support-agent

2. Create Virtual Environment
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows

3. Install Dependencies
pip install -r requirements.txt


Requirements include:

langgraph (workflow engine)

langchain-core

fastapi (for REST API)

uvicorn (server runner)

pytest (testing)

4. Run Development Server
uvicorn server:app --reload --port 8080


API is available at:

http://localhost:8080/api/process_ticket

▶️ Running the Agent

You can send tickets via PowerShell, curl, or Postman.

Example (PowerShell):

Invoke-RestMethod -Uri "http://localhost:8080/api/process_ticket" `
  -Method POST `
  -Body '{"ticket_id":"T1","subject":"Server Down Issue","description":"The server is down with a 500 error"}' `
  -ContentType "application/json"


Example response:

{
  "ticket_id": "T1",
  "category": "Technical",
  "review_decision": "approved",
  "final_reply": "We acknowledge the server issue and are working on it.",
  "escalated": false
}

🧪 Running Tests

We use pytest for automated workflow validation.

Run all tests:

pytest -v


Tests are located in tests/test_graph.py and cover:

Technical issue approval

Refund request rejection → approval on retry

Extreme refund escalation

Sensitive info rejection

Default approval (non-critical requests)

Subject + description synergy

🏗️ Design & Architectural Decisions
1. LangGraph Workflow

The workflow is defined in app/graph.py. Key nodes:

Classification Node → Categorizes ticket.

Review Node → Applies decision rules.

Refine Node → Allows retry after rejection.

Escalation Node → Handles extreme refund or unresolved cases.

2. Stopping Conditions

Recursion limit prevents infinite review loops.

Sensitive information triggers immediate rejection.

Extreme refund requests trigger escalation.

3. Retry Logic

On first attempt, refunds may be rejected.

On second attempt (retries=1), same ticket may be approved.

After maximum retries, unresolved cases are escalated.

4. FastAPI Integration

Exposes a REST endpoint at /api/process_ticket.

Accepts JSON with ticket_id, subject, description, retries.

Returns structured JSON with category, decision, reply, escalation status.

5. Testing Strategy

Automated tests validate each path: approval, rejection, escalation, blocking.

Manual scenarios can be run with curl/PowerShell for demo purposes.

📹 Demo Scenarios

You can run these live in a demo video:

Technical Issue – Approved.

Refund Request – Rejected first, approved on retry.

Extreme Refund – Escalated to human.