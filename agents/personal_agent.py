"""Minimal personal agent based on python-a2a.

This keeps the demo running without the legacy `a2a` SDK.  Each instance
registers itself with the discovery registry pointed to by the
`A2A_REGISTRY` env-var.

Run one agent:

    uv run uvicorn agents.personal_agent:build_app --factory \
           --host 0.0.0.0 --port 10001 --name Alice --port-arg 10001

Run another:

    uv run uvicorn agents.personal_agent:build_app --factory \
           --host 0.0.0.0 --port 10002 --name Bob --port-arg 10002
"""

from __future__ import annotations

import argparse
import os
import textwrap
from fastapi import FastAPI
from python_a2a import A2AServer, AgentCard, AgentSkill
import json, os, textwrap, argparse  # ensure json imported earlier
from google import genai  # NEW import for Gemini LLM


def build_app(name: str = "Demo", port: int = 10001) -> FastAPI:  # noqa: D401
    """Return an ASGI app for a very small personal agent.

    • Publishes a single *echo* skill so we have something callable.
    • Uses the same python-a2a SDK as the discovery registry & restaurant agent.
    • Loads user preferences from environment variables to personalize behavior.
    """
    
    # Load preferences from environment
    preferences_json = os.getenv("PREFERENCES_JSON", "{}")
    system_prompt = ""
    
    try:
        preferences = json.loads(preferences_json)
        system_prompt = preferences.get("_system_prompt", "")
    except json.JSONDecodeError:
        system_prompt = ""

    echo_skill = AgentSkill(
        id="echo",
        name="Echo",
        description="Echoes back whatever the user says.",
    )

    card = AgentCard(
        name=f"{name}'s Agent",
        description="Minimal personal agent (python-a2a demo) with LLM chat",
        url=f"http://localhost:{port}/",
        version="0.1.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        skills=[echo_skill],
    )

    # Add chat skill powered by Gemini
    chat_skill = AgentSkill(
        id="chat",
        name="Chat",
        description="General conversational skill backed by Gemini LLM.",
    )
    card.skills.append(chat_skill)

    app = FastAPI()

    # Very small business-logic function: just echo the input object.
    from python_a2a.discovery import enable_discovery  # local import to avoid startup cost if unused

    server = A2AServer(app, fn=lambda body: body, card=card)

    # Work around a quirk in the current python-a2a release where
    # `server.agent_card` is initialised to the underlying ASGI app instead
    # of the actual AgentCard.  Overwriting it ensures the discovery helper
    # receives the right object and avoids the `'FastAPI' object has no
    # attribute 'to_dict'` error.
    server.agent_card = card  # type: ignore[attr-defined]

    # Additional skill: forward restaurant prefs to Restaurant-Selector

    selector_skill = AgentSkill(
        id="restaurant_recommendation",
        name="Restaurant Recommendation",
        description="Forwards preference JSON to the Restaurant-Selector agent and returns its reply.",
    )

    # Attach the extra skill to the card
    card.skills.append(selector_skill)

    # ------------------------------------------------------------------
    # Minimal HTTP routes so `/tasks/send` works out-of-the-box with
    # FastAPI (python_a2a currently registers Flask routes only).
    # ------------------------------------------------------------------

    from fastapi import HTTPException
    import anyio

    def _echo_impl(body: dict):  # noqa: ANN001
        """Purely synchronous echo helper run in a worker thread."""
        # If we have a system prompt, enhance the response with personality
        if system_prompt and body.get("input"):
            # Simple enhancement - in a real implementation, you'd use an LLM here
            enhanced_response = {
                "original_input": body.get("input"),
                "personalized_response": f"Based on your preferences, I understand you're asking about: {body.get('input')}",
                "system_context": "I'm using your preferences to provide personalized responses.",
                "preferences_loaded": bool(system_prompt)
            }
            return enhanced_response
        return body

    @app.post("/tasks/send")
    async def tasks_send(body: dict):  # noqa: ANN001
        try:
            output = await anyio.to_thread.run_sync(_echo_impl, body)
            return {
                "id": body.get("id", "task-1"),
                "status": {"state": "completed"},
                "artifacts": [
                    {
                        "parts": [
                            {"type": "text", "text": str(output)}
                        ]
                    }
                ],
            }
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=400, detail=str(exc))

    import requests

    # Initialise Gemini model once
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception:
        model = None  # Fallback if credentials not set

    @app.post("/invoke")
    async def invoke(body: dict):  # noqa: ANN001
        """Entry point that supports skills:

        • chat (default)
        • restaurant_recommendation – forwards to selector
        """

        skill = body.get("skill", "chat")

        if skill == "restaurant_recommendation":
            prefs = body.get("input", {})
            
            # Enhance with user's stored preferences
            if system_prompt:
                try:
                    stored_prefs = json.loads(preferences_json)
                    food_prefs = stored_prefs.get("food", {})
                    
                    # Merge stored preferences with request
                    if "cuisines" not in prefs and food_prefs.get("cuisines"):
                        prefs["cuisines"] = food_prefs["cuisines"]
                    if "dietary_restrictions" not in prefs and food_prefs.get("dietary_restrictions"):
                        prefs["dietary_restrictions"] = food_prefs["dietary_restrictions"]
                    if "budget_level" not in prefs and food_prefs.get("budget_level"):
                        prefs["budget_level"] = food_prefs["budget_level"]
                    if "atmosphere_preferences" not in prefs and food_prefs.get("atmosphere_preferences"):
                        prefs["atmosphere_preferences"] = food_prefs["atmosphere_preferences"]
                        
                except (json.JSONDecodeError, KeyError):
                    pass  # Use original prefs if parsing fails

            def _call_selector() -> dict:
                try:
                    resp = requests.post(
                        "http://localhost:8080/invoke",
                        headers={"Content-Type": "application/json"},
                        json=prefs,
                        timeout=180,
                    )
                except requests.exceptions.ReadTimeout:
                    return {"error": "Selector timed out"}
                resp.raise_for_status()
                return resp.json()

            selector_reply = await anyio.to_thread.run_sync(_call_selector)
            return selector_reply

        # Fallback to chat LLM
        user_input = body.get("input", "")

        async def _call_llm() -> dict:
            if model is None:
                return {"reply": "LLM not configured."}
            message_list = []
            if system_prompt:
                message_list.append({"role": "system", "parts": [system_prompt]})
            message_list.append({"role": "user", "parts": [user_input]})
            resp = model.generate_content(message_list)
            return {"reply": resp.text}

        llm_reply = await anyio.to_thread.run_sync(_call_llm)
        return llm_reply

    # Automatically register this agent with the discovery registry (if available).
    # Falls back to http://localhost:9000 which is the demo default.
    registry_url = os.getenv("A2A_REGISTRY", "http://localhost:9000")
    try:
        enable_discovery(server, registry_url=registry_url)
    except Exception as exc:  # pragma: no cover – best-effort
        # Registration failures shouldn't crash the agent – just log and continue.
        import logging

        logging.getLogger(__name__).warning("[personal_agent] Failed to register with A2A registry %s: %s", registry_url, exc)

    return app


# ---------------------------------------------------------------------------
# Convenience CLI entry-point so we can run:  `python -m agents.personal_agent …`
# ---------------------------------------------------------------------------

def _cli() -> None:  # pragma: no cover – manual runner
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            Start a minimal personal agent that registers with the
            python-a2a discovery registry.

            Example:

              python -m agents.personal_agent --name Alice --port 10001
            """
        ),
    )
    parser.add_argument("--name", required=True, help="Human name (for the agent card)")
    parser.add_argument("--port", type=int, required=True, help="Port to listen on")
    args = parser.parse_args()

    os.environ.setdefault("A2A_REGISTRY", "http://localhost:9000")

    import uvicorn

    uvicorn.run(
        build_app(args.name, args.port),
        host="0.0.0.0",
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    _cli() 