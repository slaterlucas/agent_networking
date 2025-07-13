# ── a2a_wrapper.py ──────────────────────────────────────────────────────────
# Standard FastAPI server
from fastapi import FastAPI, Header, HTTPException, status

# Python-A2A SDK 
from python_a2a import A2AServer, AgentCard, AgentSkill
from python_a2a.discovery import AgentRegistry

# Business logic
from adk.restaurant_selector.main import suggest_restaurant

import os
# Optional: Google ID-token auth (commented out until needed)
# from google.oauth2 import id_token
# from google.auth.transport import requests as grequests

import json
from python_a2a.models import Message  # type: ignore

# region: WEAVE
import weave
weave.init("weavehack")
# endregion: WEAVE

skill = AgentSkill(
    id="restaurant-selector",
    name="restaurant-selector",
    description="LLM-driven restaurant picker using Exa + Gemini-2.5",
    tags=["restaurant", "picker"],
    examples=[
        "I'm looking for a Mexican restaurant in San Francisco on Friday at 7pm, moderate budget, want date night vibes",
    ]
)

# 1) Typed I/O so callers can introspect
from pydantic import BaseModel, Field


class Inputs(BaseModel):
    # Support both structured and text-based queries
    text_query: str | None = Field(None, description="Natural language restaurant query")
    
    # Optional structured fields
    location: str | None = None
    cuisines: list[str] = []
    diet: list[str] = []
    time_window: list[str] = []           # ["2025-07-15T18:00", "2025-07-15T21:00"]
    budget: str | None = None
    
    # Additional optional fields for flexibility
    meal_type: str | None = None
    atmosphere_preferences: list[str] = []
    dietary_restrictions: list[str] = []
    budget_level: str | None = None


class Outputs(BaseModel):
    recommendation: str = Field(..., description="Plain-text restaurant recommendation")

# 2) Agent-card published at /.well-known/agent.json
CARD = AgentCard(
    name="Restaurant Selector",
    description="LLM-driven restaurant picker using Exa + Gemini-2.5",
    url=os.getenv("SERVICE_URL", "http://localhost:8080/"),
    version="0.1.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities={"streaming": False},
    skills=[skill],
)


# 3) Optional ID-token auth (comment out for local dev)
# AUDIENCE = os.getenv("SERVICE_URL")  # e.g. https://selector-xyz.a.run.app
#
# def verify_id_token(auth: str = Header(...)):
#     if not auth.startswith("Bearer "):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#     token = auth.split(" ", 1)[1]
#     try:
#         id_token.verify_oauth2_token(token, grequests.Request(), AUDIENCE)
#     except ValueError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

def verify_id_token():
    """No-op auth for local development."""
    return

# 4) Bridge Inputs → ADK → Outputs


# The A2AServer passes the raw request body to this function – it could be
# a python_a2a `Message` object (most common) or a plain `dict` if the caller
# hit `/invoke` directly.  We normalise it into our `Inputs` model.


def _impl(body) -> Outputs:  # noqa: ANN001
    """Bridge A2A message → `Inputs` → `suggest_restaurant`.

    Returns an `Outputs` instance with the recommendation text.
    """

    # 1. Extract the JSON payload that represents `Inputs`.
    data: dict | None = None

    if isinstance(body, Inputs):
        data = body.model_dump()
    elif isinstance(body, dict):
        # Could be the plain Inputs dict *or* a full A2A Task/Message wrapper.
        if "message" in body:  # A2A wrapper style
            try:
                msg = body["message"]
                txt = None
                if isinstance(msg, dict):
                    # python_a2a style
                    txt = (
                        msg.get("content", {}) or {}
                    ).get("text")
                    # Google-A2A style fallback
                    if txt is None and "parts" in msg:
                        for part in msg["parts"]:
                            if isinstance(part, dict) and part.get("type") == "text":
                                txt = part.get("text")
                                break
                if txt:
                    data = json.loads(txt)
            except Exception:
                pass
        else:
            # Assume it's directly the Inputs dict
            data = body

    if data is None:
        raise ValueError("Could not parse inputs from request body")

    # Handle text-based queries by converting to structured format
    if isinstance(data, str):
        # If data is just a string, treat it as a text query
        data = {"text_query": data}
    elif "input" in data and isinstance(data["input"], str):
        # Handle personal agent format
        data = {"text_query": data["input"]}
    elif "input" in data and isinstance(data["input"], dict):
        # Handle personal agent format with structured data
        data = data["input"]

    # Parse into Inputs model with error handling
    try:
        prefs = Inputs.model_validate(data)
    except Exception as e:
        # If parsing fails, try to extract as text query
        if isinstance(data, dict) and any(key in data for key in ["text", "query", "message"]):
            text_content = data.get("text") or data.get("query") or data.get("message")
            prefs = Inputs(text_query=str(text_content))
        else:
            raise ValueError(f"Could not parse inputs: {e}")

    # Convert to format expected by suggest_restaurant
    restaurant_data = prefs.model_dump()
    
    # If we have a text query, parse it into structured fields
    if prefs.text_query and not prefs.location:
        # Simple text parsing - in a real app you'd use an LLM for this
        query_lower = prefs.text_query.lower()
        
        # Extract location if not provided
        if "san francisco" in query_lower or "sf" in query_lower:
            restaurant_data["location"] = "San Francisco"
        elif "new york" in query_lower or "nyc" in query_lower:
            restaurant_data["location"] = "New York"
        else:
            restaurant_data["location"] = "San Francisco"  # Default
            
        # Extract cuisines if not provided
        if not prefs.cuisines:
            if "italian" in query_lower:
                restaurant_data["cuisines"] = ["Italian"]
            elif "chinese" in query_lower:
                restaurant_data["cuisines"] = ["Chinese"]
            elif "mexican" in query_lower:
                restaurant_data["cuisines"] = ["Mexican"]
            else:
                restaurant_data["cuisines"] = ["Any"]
                
        # Extract time window if not provided
        if not prefs.time_window:
            if "lunch" in query_lower:
                restaurant_data["time_window"] = ["12:00", "14:00"]
            elif "dinner" in query_lower:
                restaurant_data["time_window"] = ["18:00", "21:00"]
            else:
                restaurant_data["time_window"] = ["18:00", "21:00"]  # Default to dinner

    # Ensure required fields have defaults
    if not restaurant_data.get("location"):
        restaurant_data["location"] = "San Francisco"
    if not restaurant_data.get("cuisines"):
        restaurant_data["cuisines"] = ["Any"]
    if not restaurant_data.get("time_window"):
        restaurant_data["time_window"] = ["18:00", "21:00"]

    # 2. Run the business-logic agent.
    recommendation = suggest_restaurant(restaurant_data)

    # 3. Wrap in Outputs so the caller gets JSON back.
    return Outputs(recommendation=recommendation)

# 5) Spin up FastAPI with the A2A helper
app = FastAPI()

# Create the A2A server and register with discovery
from python_a2a.discovery import enable_discovery

server = A2AServer(
    app,
    fn=_impl,                    # or agent=_impl for streaming
    card=CARD,
    auth_dependency=verify_id_token,
)

# Work-around similar to personal_agent: ensure agent_card is correct
server.agent_card = CARD  # type: ignore[attr-defined]

# ---------------------------------------------------------------------------
# Minimal HTTP surface so callers can talk to this service without relying on
# the more complex (and currently missing) python_a2a HTTP adapters.
# ---------------------------------------------------------------------------

from fastapi import HTTPException
import anyio

@weave.op()
@app.post("/tasks/send")
async def tasks_send(body: dict):
    """A2A-compatible endpoint (subset).

    Expects a JSON object with at least `message.content.text` containing the
    restaurant-preference JSON.  Returns a Task-like dict with the
    recommendation in `artifacts[0].parts[0].text`.
    """

    try:
        # Run blocking logic in a worker thread so we don't clash with the
        # FastAPI/Uvicorn event loop.
        output = await anyio.to_thread.run_sync(_impl, body)
        return {
            "id": body.get("id", "task-1"),
            "status": {"state": "completed"},
            "artifacts": [
                {
                    "parts": [
                        {"type": "text", "text": output.recommendation}
                    ]
                }
            ],
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# Simple convenience path for manual testing
@app.post("/invoke")
async def invoke(body: dict):
    return await tasks_send(body)

# Auto-register with the local registry (if running)
enable_discovery(server, registry_url=os.getenv("A2A_REGISTRY", "http://localhost:9000"))

# Local dev: `uvicorn a2a_wrapper:app --host 0.0.0.0 --port 8080`
