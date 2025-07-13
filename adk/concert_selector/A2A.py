# ── a2a_wrapper.py ──────────────────────────────────────────────────────────
# Standard FastAPI server
from fastapi import FastAPI, Header, HTTPException, status

# Python-A2A SDK 
from python_a2a import A2AServer, AgentCard, AgentSkill
from python_a2a.discovery import AgentRegistry

# Business logic
from adk.concert_selector.main import suggest_concert

import os
# Optional: Google ID-token auth (commented out until needed)
# from google.oauth2 import id_token
# from google.auth.transport import requests as grequests

import json
from python_a2a.models import Message  # type: ignore

# region: WEAVE
import weave
import wandb

# Initialize Weave with proper error handling
weave_enabled = False
try:
    # Try to login to wandb first with hardcoded API key
    wandb_api_key = "525921409bd3f7f9eec996750d671d5db66dc74a"
    if wandb_api_key:
        wandb.login(key=wandb_api_key)
        print("[INFO] W&B login successful with API key")
    else:
        print("[INFO] No WANDB_API_KEY found, trying default login")
        wandb.login()
    
    # Try to initialize Weave
    weave.init("weavehack")
    weave_enabled = True
    print("[INFO] Weave initialized successfully")
except Exception as e:
    print(f"[WARNING] Failed to initialize Weave: {e}")
    print("[INFO] Continuing without Weave tracking")
    weave_enabled = False
    
    # Create a dummy weave module for when it's not available
    class DummyWeave:
        def op(self):
            def decorator(func):
                return func
            return decorator
    
    if not weave_enabled:
        weave = DummyWeave()
# endregion: WEAVE

skill = AgentSkill(
    id="concert-selector",
    name="concert-selector",
    description="LLM-driven concert picker using Exa + Gemini-2.5",
    tags=["concert", "music", "picker"],
    examples=[
        "I'm looking for an indie rock concert in San Francisco this weekend, moderate budget, want good vibes",
    ]
)

# 1) Typed I/O so callers can introspect
from pydantic import BaseModel, Field


class Inputs(BaseModel):
    # Support both structured and text-based queries
    text_query: str | None = Field(None, description="Natural language concert query")
    
    # Optional structured fields
    location: str | None = None
    genres: list[str] = []
    artist_preferences: list[str] = []
    time_window: list[str] = []           # ["2025-07-15T18:00", "2025-07-15T23:00"]
    budget: str | None = None
    
    # Additional optional fields for flexibility
    venue_type: str | None = None
    atmosphere_preferences: list[str] = []
    age_restrictions: list[str] = []
    budget_level: str | None = None


class Outputs(BaseModel):
    recommendation: str = Field(..., description="Plain-text concert recommendation")


# 2) Agent-card published at /.well-known/agent.json
CARD = AgentCard(
    name="Concert Selector",
    description="LLM-driven concert picker using Exa + Gemini-2.5",
    url=os.getenv("SERVICE_URL", "http://localhost:8081/"),
    version="0.1.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities={"streaming": False},
    skills=[skill],
)

# 3) Main server
app = FastAPI()


# 4) Optional: Google ID-token auth
def verify_id_token():
    """
    Placeholder for Google ID-token verification.
    If you need auth, uncomment the imports above and implement this.
    """
    pass


def _impl(body) -> Outputs:  # noqa: ANN001
    """
    Main implementation: parse input, call suggest_concert, return structured output.
    """
    # Parse input
    if isinstance(body, dict):
        inputs = Inputs(**body)
    else:
        inputs = body
    
    # Handle text query by extracting structured data
    if inputs.text_query:
        # Simple text parsing to extract concert preferences
        query_lower = inputs.text_query.lower()
        
        # Extract location
        location = inputs.location
        if not location:
            # Simple location extraction
            for city in ["san francisco", "sf", "new york", "nyc", "los angeles", "la", "chicago", "boston", "seattle", "portland", "austin", "nashville", "denver"]:
                if city in query_lower:
                    location = city
                    break
        
        # Extract genres
        genres = inputs.genres if inputs.genres else []
        genre_keywords = {
            "rock": ["rock", "indie rock", "alternative rock", "punk rock"],
            "pop": ["pop", "pop music"],
            "hip hop": ["hip hop", "rap", "hip-hop"],
            "electronic": ["electronic", "edm", "techno", "house"],
            "jazz": ["jazz"],
            "classical": ["classical", "orchestra"],
            "country": ["country"],
            "folk": ["folk", "acoustic"],
            "metal": ["metal", "heavy metal"],
            "indie": ["indie", "independent"],
            "blues": ["blues"],
            "reggae": ["reggae"],
            "r&b": ["r&b", "rnb", "soul"]
        }
        
        for genre, keywords in genre_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                if genre not in genres:
                    genres.append(genre)
        
        # Extract budget
        budget = inputs.budget
        if not budget:
            if any(word in query_lower for word in ["cheap", "budget", "affordable", "low cost"]):
                budget = "low"
            elif any(word in query_lower for word in ["expensive", "premium", "high end", "luxury"]):
                budget = "high"
            else:
                budget = "medium"
        
        # Extract time preferences
        time_window = inputs.time_window if inputs.time_window else []
        if not time_window:
            if "tonight" in query_lower:
                time_window = ["2025-07-15T18:00", "2025-07-15T23:00"]
            elif "weekend" in query_lower:
                time_window = ["2025-07-19T18:00", "2025-07-20T23:00"]
            elif "this week" in query_lower:
                time_window = ["2025-07-15T18:00", "2025-07-21T23:00"]
        
        # Create structured preferences
        prefs = {
            "location": location or "San Francisco",
            "genres": genres or ["rock"],
            "artist_preferences": inputs.artist_preferences or [],
            "time_window": time_window or ["2025-07-15T18:00", "2025-07-15T23:00"],
            "budget": budget or "medium",
            "venue_type": inputs.venue_type,
            "atmosphere_preferences": inputs.atmosphere_preferences or [],
        }
    else:
        # Use structured input
        prefs = {
            "location": inputs.location or "San Francisco",
            "genres": inputs.genres or ["rock"],
            "artist_preferences": inputs.artist_preferences or [],
            "time_window": inputs.time_window or ["2025-07-15T18:00", "2025-07-15T23:00"],
            "budget": inputs.budget or "medium",
            "venue_type": inputs.venue_type,
            "atmosphere_preferences": inputs.atmosphere_preferences or [],
        }
    
    # Call the main concert selector
    try:
        recommendation = suggest_concert(prefs)
        return Outputs(recommendation=recommendation)
    except Exception as e:
        # Fallback response
        return Outputs(
            recommendation=f"I'm having trouble finding concerts right now. Error: {str(e)}"
        )


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

# 5) A2A-compatible endpoint
@weave.op()
@app.post("/tasks/send")
async def tasks_send(body: dict):
    """A2A-compatible endpoint (subset).

    Expects a JSON object with at least `message.content.text` containing the
    concert-preference JSON.  Returns a Task-like dict with the
    recommendation in `artifacts[0].parts[0].text`.
    """
    try:
        # Extract the message content
        message_content = body.get("message", {}).get("content", {})
        
        # Try to parse as JSON first
        if isinstance(message_content, dict) and "text" in message_content:
            text_content = message_content["text"]
        else:
            text_content = str(message_content)
        
        # Try to parse as JSON, fallback to text query
        try:
            prefs = json.loads(text_content)
            inputs = Inputs(**prefs)
        except (json.JSONDecodeError, TypeError):
            # Treat as text query
            inputs = Inputs(text_query=text_content)
        
        # Call implementation
        result = _impl(inputs)
        
        # Return in A2A Task format
        return {
            "id": "task-1",
            "status": {"state": "completed"},
            "artifacts": [
                {
                    "parts": [
                        {
                            "type": "text",
                            "text": result.recommendation
                        }
                    ]
                }
            ]
        }
        
    except Exception as e:
        return {
            "id": "task-1",
            "status": {"state": "failed"},
            "artifacts": [
                {
                    "parts": [
                        {
                            "type": "text",
                            "text": f"Error processing concert request: {str(e)}"
                        }
                    ]
                }
            ]
        }


# 6) Direct invoke endpoint
@app.post("/invoke")
async def invoke(body: dict):
    return await tasks_send(body)

# Auto-register with the local registry (if running)
enable_discovery(server, registry_url=os.getenv("A2A_REGISTRY", "http://localhost:9000"))

# Local dev: `uvicorn a2a_wrapper:app --host 0.0.0.0 --port 8081` 