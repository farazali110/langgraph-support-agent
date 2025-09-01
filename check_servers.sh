#!/bin/bash
# Script to check the status of the servers and run a simple test

echo "==================================================="
echo "CHECKING SERVER STATUS"
echo "==================================================="

# Check if FastAPI server is running
echo -n "FastAPI Server (port 8000): "
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "RUNNING"
else
    echo "NOT RUNNING"
fi

# Check if LangGraph server is running
echo -n "LangGraph Server (port 2024): "
if curl -s http://localhost:2024 > /dev/null 2>&1; then
    echo "RUNNING"
else
    echo "NOT RUNNING"
fi

echo
echo "==================================================="
echo "TESTING API ENDPOINT"
echo "==================================================="

# Test the API endpoint
echo "Sending test request to /resolve_ticket..."
curl -s -X POST http://localhost:8000/resolve_ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id": "12345", "subject": "Test", "description": "Test"}' \
  | python -m json.tool

echo
echo "==================================================="
echo "If you see a JSON response above, the API is working!"
echo "==================================================="
