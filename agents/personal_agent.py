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


def build_app(name: str = "Demo", port: int = 10001) -> FastAPI:  # noqa: D401
    """Return an ASGI app for a very small personal agent.

    • Publishes a single *echo* skill so we have something callable.
    • Uses the same python-a2a SDK as the discovery registry & restaurant agent.
    """

    skill = AgentSkill(
        id="echo",
        name="Echo",
        description="Echoes back whatever the user says.",
    )

    card = AgentCard(
        name=f"{name}'s Agent",
        description="Minimal personal agent (python-a2a demo)",
        url=f"http://localhost:{port}/",
        version="0.1.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        skills=[skill],
    )

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