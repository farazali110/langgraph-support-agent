LangGraph Support Agent

A support ticket resolution agent built with LangGraph
 that helps resolve support tickets through a multi-step review process.

Overview

This agent processes support tickets through a structured workflow:

Classification: Categorizes tickets into Billing, Technical, Security, or General

Retrieval: Fetches relevant documentation based on the ticket category and content

Draft Generation: Creates a response using retrieved context

Review: Checks response quality and policy compliance

Refinement Loop: If review fails, improves response with feedback (maximum 2 retries)

Escalation: If refinement fails after 2 retries, logs ticket for human review

Review Loop Design

The review loop is strictly capped at 2 retries to prevent infinite recursion:

First Attempt → Draft → Review → If rejected → Refine

Second Attempt → Draft → Review → If rejected → Refine

Final Attempt → Draft → Review → If rejected → Escalate

This ensures no more than 3 total drafts are created for any ticket (initial + 2 retries).