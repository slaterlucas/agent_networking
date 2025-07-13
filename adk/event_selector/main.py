"""
event_selector_adk.py
LLM-driven event picker powered by:

  • Exa web-search API                    (function-calling tool)
  • Google ADK Agent (Gemini-2.5-pro)     (Vertex AI / Cloud project)

Setup
-----
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies using uv
uv sync

# Create .env file with your credentials
cp config.example.env .env
# Edit .env with your actual values

# Set up Google Cloud credentials (if using Google ADK)
export GOOGLE_CLOUD_PROJECT=<your-gcp-project>
export GOOGLE_CLOUD_LOCATION=us-central1         # or whatever region hosts Gemini
export EXA_API_KEY=<your-exa-key>
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json   # service-account w/ gen-ai perms

# Run the agent
uv run python main.py
"""

from __future__ import annotations
import json, os, typing as t
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio
from google import genai
# ── 0.  ENV & BOOTSTRAP  ──────────────────────────────────────────────────────
load_dotenv()

USE_VERTEX = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
EXA_API_KEY  = os.getenv("EXA_API_KEY")

client = genai.Client(
    vertexai=True, project=os.getenv("GOOGLE_CLOUD_PROJECT"), location='us-central1'
)
# ── 1.  EXA SEARCH TOOL (imported) ─────────────────────────────────────────────
from adk.utils.exa_search import exa_search


# ── 2.  AGENT DEFINITION  ─────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an Event-Selector. Input is a JSON object with location,
event_types, interests, and time window. Steps:

1. Use `exa_search` to gather information.
   • Prefer reviews from respected sources (Time Out, Eventbrite,
    Ticketmaster, local event calendars, venue websites, Facebook Events,
    Meetup, etc.), but feel free to consult venue websites
    for details or schedules.
2. You will use `exa_search` tool.
   • First call: find ~5 candidate events, based off parameters based off
     user's preferences.
   • For each candidate, call exa_search again to fetch details and reviews.
2. Choose ONE best event.
3. Return a concise plain-text recommendation in this format (no markdown):
Event: <name>
Venue: <venue_name>
Address: <address>
Date/Time: <event_datetime ISO 8601 local>
Vibe: <≤25-word description>
Why: • bullet 1; • bullet 2; • bullet 3
Citations:
  <url1>  – label 1
  <url2>  – label 2
}
"""

agent = Agent(
    name="event_selector",
    model="gemini-2.5-flash",
    tools=[exa_search],
    instruction=SYSTEM_PROMPT,
)

_session_service = InMemorySessionService()

def _get_sync_runner(agent: Agent, app_name: str, user_id: str, session_id: str) -> Runner:
    """
    Create (or reuse) a session and hand back a synchronous Runner.
    """
    async def _setup() -> Runner:
        await _session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        return Runner(agent=agent, app_name=app_name, session_service=_session_service)

    # In worker threads there may be no running event loop; asyncio.run will
    # create one as needed.  It also works fine when called from the main
    # thread (as long as no loop is currently running).

    return asyncio.run(_setup())

def suggest_event(prefs: dict) -> str:
    """
    Call the agent once through ADK and return the plain-text recommendation.
    """
    runner = _get_sync_runner(
        agent=agent,
        app_name="event_selector_app",
        user_id="demo_user",
        session_id="demo_session",
    )

    msg = types.Content(role="user", parts=[types.Part(text=json.dumps(prefs))])

    for event in runner.run(
        user_id="demo_user",
        session_id="demo_session",
        new_message=msg,
    ):
        if event.is_final_response():
            return event.content.parts[0].text

    raise RuntimeError("Agent did not emit a final response")

# ── 4.  DEMO ─────────────────────────────────────────────────────
if __name__ == "__main__":
    prefs_example = {
        "location": "Brooklyn, New York",
        "event_types": ["concert"],
        "interests": ["jazz", "live music"],
        "time_window": ["2025-07-15T18:00", "2025-07-15T21:00"],
        "budget": "moderate",
    }
    print(suggest_event(prefs_example)) 