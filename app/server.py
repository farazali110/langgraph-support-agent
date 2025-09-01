from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.graph import build_graph
from app.state import GraphState
import logging
import sys
import json
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("support_agent.log")],
)
logger = logging.getLogger("support-agent")

app = FastAPI(
    title="LangGraph Support Agent API",
    description="API for processing support tickets using LangGraph",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Build graph once
try:
    logger.info("Building LangGraph workflow")
    graph = build_graph()
    logger.info("Graph compiled successfully")
except Exception as e:
    logger.critical(f"Failed to build LangGraph workflow: {e}")
    logger.critical(traceback.format_exc())
    graph = None


# Utility
def get_result_attr(result, attr_name, default=None):
    if hasattr(result, attr_name):
        return getattr(result, attr_name)
    elif isinstance(result, dict) and attr_name in result:
        return result[attr_name]
    return default


@app.get("/")
async def root():
    return {
        "message": "LangGraph Support Agent API is running",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "resolve_ticket": "/resolve_ticket",
            "process_ticket": "/api/process_ticket",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    if not graph:
        return {"status": "error", "message": "LangGraph not initialized"}
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


class TicketRequest(BaseModel):
    ticket_id: str
    subject: str
    description: str
    text: Optional[str] = None


class EnhancedTicketRequest(BaseModel):
    ticket_id: str
    subject: str
    description: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@app.post("/resolve_ticket")
async def resolve_ticket(request: TicketRequest):
    if not graph:
        raise HTTPException(status_code=500, detail="LangGraph not initialized")

    state = GraphState(
        ticket_id=request.ticket_id,
        subject=request.subject,
        description=request.description,
        ticket_text=request.text if request.text else request.description,
    )

    try:
        start = datetime.now()
        result = graph.invoke(state, config={"recursion_limit": 50})
        elapsed = (datetime.now() - start).total_seconds()

        return {
            "ticket_id": request.ticket_id,
            "output": get_result_attr(result, "final_reply", "No response generated"),
            "category": get_result_attr(result, "category", "Unknown"),
            "escalated": get_result_attr(result, "escalated", False),
            "timestamp": datetime.now().isoformat(),
            "processing_time": elapsed,
        }
    except Exception as e:
        logger.exception("Error processing ticket")
        return {
            "ticket_id": request.ticket_id,
            "error": str(e),
            "category": "Unknown",
            "escalated": False,
            "response": "We encountered an issue while processing your ticket.",
            "timestamp": datetime.now().isoformat(),
        }


@app.post("/api/process_ticket")
async def process_ticket(request: Request):
    try:
        body = await request.json()
        if not graph:
            return {"error": "LangGraph not initialized", "status": "error"}

        ticket_id = body.get("ticket_id", f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        subject = body.get("subject", "")
        description = next((body.get(f) for f in ["description", "content", "text", "body", "message"] if body.get(f)), None)

        if not description:
            return {"error": "Missing ticket description", "status": "error", "ticket_id": ticket_id}

        if not subject:
            subject = description.split("\n", 1)[0][:100]

        state = GraphState(
            ticket_id=ticket_id,
            subject=subject,
            description=description,
            ticket_text=description,
        )

        start = datetime.now()
        result = graph.invoke(state, config={"recursion_limit": 50})
        elapsed = (datetime.now() - start).total_seconds()

        return {
            "ticket_id": ticket_id,
            "category": get_result_attr(result, "category", "Unknown"),
            "response": get_result_attr(result, "final_reply", "No response generated"),
            "escalated": get_result_attr(result, "escalated", False),
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": elapsed,
        }

    except Exception as e:
        logger.exception("Top-level error")
        return {
            "error": str(e),
            "status": "error",
            "ticket_id": body.get("ticket_id", "UNKNOWN"),
            "category": "Unknown",
            "escalated": False,
            "response": "We encountered an issue while processing your ticket.",
            "timestamp": datetime.now().isoformat(),
        }
