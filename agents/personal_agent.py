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
from fastapi.middleware.cors import CORSMiddleware
from python_a2a import A2AServer, AgentCard, AgentSkill
import json, os, textwrap, argparse, asyncio  # ensure json imported earlier
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google import genai
from google.genai import types
import requests
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import weave
import wandb

# Initialize Weave with proper error handling
weave_enabled = False
try:
    # Try to login to wandb first with environment variable
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


# Configure genai client for Vertex AI
try:
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    if project:
        genai_client = genai.Client(
            vertexai=True, 
            project=project, 
            location=location
        )
        print(f"[INFO] Configured genai client for project: {project}, location: {location}")
    else:
        genai_client = None
        print("[WARNING] GOOGLE_CLOUD_PROJECT not set - genai client not configured")
except Exception as e:
    genai_client = None
    print(f"[ERROR] Failed to configure genai client: {e}")

# Global ADK session service
adk_session_service = InMemorySessionService()

# Apply weave decorator conditionally
def _create_adk_agent(name: str, preferences: dict, system_prompt: str):
    """Create an ADK agent instance for chat."""
    chat_system_prompt = f"""You are {name}'s personal AI assistant. You have access to their preferences and can help with various tasks.

{system_prompt}

## Special Instructions:
- For collaborative requests (involving other users), you should recognize them and route to the collaborative middleware
- Collaborative requests include phrases like: "with Bob", "and Alice", "Bob and I", "me and Charlie", etc.
- Look for patterns like: "dinner with [name]", "go to [event] with [name]", "[name] and I want to [activity]"
- When you detect a collaborative request, respond with: "COLLABORATIVE_REQUEST: [extracted details]"

- For restaurant/dining requests, you should recognize them and route to the restaurant selector
- Restaurant requests include: finding restaurants, dinner plans, lunch suggestions, food recommendations, etc.
- Look for keywords like: restaurant, dinner, lunch, food, eat, cuisine, reservation, etc.
- When you detect a restaurant request, respond with: "RESTAURANT_REQUEST: [extracted details]"

- For concert/music requests, you should recognize them and route to the concert selector
- Concert requests include: finding concerts, live music, shows, bands, artists, music events, etc.
- Look for keywords like: concert, music, show, band, artist, gig, live music, venue, tickets, etc.
- When you detect a concert request, respond with: "CONCERT_REQUEST: [extracted details]"

- For all other queries, provide helpful, personalized responses based on the user's preferences
- Be conversational and friendly
- Remember the user's preferences when giving advice

## Your User's Preferences:
{json.dumps(preferences, indent=2) if preferences else "No preferences set yet"}
    """
    
    try:
        # Configure for Vertex AI
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        if not project:
            print("[ERROR] GOOGLE_CLOUD_PROJECT not set - ADK agent creation failed")
            return None
            
        print(f"[INFO] Creating ADK agent with project: {project}, location: {location}")
        
        agent = Agent(
            name=f"{name.lower().replace(' ', '_').replace('-', '_')}_chat_agent",
            model="gemini-2.0-flash-exp",
            description=f"Personal AI assistant for {name}",
            instruction=chat_system_prompt,
            tools=[]
        )
        print(f"[INFO] Created ADK agent: {agent.name}")
        return agent
    except Exception as e:
        print(f"[ERROR] Failed to create ADK agent: {e}")
        return None

# Apply weave decorator conditionally
if weave_enabled:
    create_adk_agent = weave.op()(_create_adk_agent)
else:
    create_adk_agent = _create_adk_agent

async def get_adk_runner(agent_instance, app_name: str, user_id: str, session_id: str):
    """Get or create an ADK runner for the session."""
    try:
        # Try to get existing session first
        existing_session = await adk_session_service.get_session(
            app_name=app_name, 
            user_id=user_id, 
            session_id=session_id
        )
        
        if existing_session is None:
            # Create new session
            await adk_session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
        
        return Runner(agent=agent_instance, app_name=app_name, session_service=adk_session_service)
        
    except Exception as e:
        print(f"[ERROR] Failed to create ADK runner: {e}")
        return None

async def call_adk_agent(query: str, runner: Runner, user_id: str, session_id: str):
    """Call the ADK agent and get response."""
    try:
        content = types.Content(role='user', parts=[types.Part(text=query)])
        final_text = ""
        
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if event.is_final_response():
                final_text = event.content.parts[0].text if event.content else ""
                break
                
        return final_text
        
    except Exception as e:
        print(f"[ERROR] ADK agent call failed: {e}")
        return None


def build_app(name: str = "Demo", port: int = 10001) -> FastAPI:  # noqa: D401
    """Return an ASGI app for a very small personal agent.

    • Publishes a single *echo* skill so we have something callable.
    • Uses the same python-a2a SDK as the discovery registry & restaurant agent.
    • Loads user preferences from environment variables to personalize behavior.
    """
    
    # Load preferences from environment
    preferences_json = os.getenv("PREFERENCES_JSON", "{}")
    system_prompt = ""
    preferences = {}
    
    try:
        preferences = json.loads(preferences_json)
        system_prompt = preferences.get("_system_prompt", "")
    except json.JSONDecodeError:
        system_prompt = ""
        preferences = {}

    # Create ADK agent for enhanced chat
    adk_agent = create_adk_agent(name, preferences, system_prompt)
    
    # Create enhanced system prompt for chat agent (fallback)
    chat_system_prompt = f"""You are {name}'s personal AI assistant. You have access to their preferences and can help with various tasks.

{system_prompt}

## Special Instructions:
- For collaborative requests (involving other users), you should recognize them and route to the collaborative middleware
- Collaborative requests include phrases like: "with Bob", "and Alice", "Bob and I", "me and Charlie", etc.
- Look for patterns like: "dinner with [name]", "go to [event] with [name]", "[name] and I want to [activity]"
- When you detect a collaborative request, respond with: "COLLABORATIVE_REQUEST: [extracted details]"

- For restaurant/dining requests, you should recognize them and route to the restaurant selector
- Restaurant requests include: finding restaurants, dinner plans, lunch suggestions, food recommendations, etc.
- Look for keywords like: restaurant, dinner, lunch, food, eat, cuisine, reservation, etc.
- When you detect a restaurant request, respond with: "RESTAURANT_REQUEST: [extracted details]"

- For concert/music requests, you should recognize them and route to the concert selector
- Concert requests include: finding concerts, live music, shows, bands, artists, music events, etc.
- Look for keywords like: concert, music, show, band, artist, gig, live music, venue, tickets, etc.
- When you detect a concert request, respond with: "CONCERT_REQUEST: [extracted details]"

- For all other queries, provide helpful, personalized responses based on the user's preferences
- Be conversational and friendly
- Remember the user's preferences when giving advice

## Your User's Preferences:
{json.dumps(preferences, indent=2) if preferences else "No preferences set yet"}
    """

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

    # Add CORS middleware to allow frontend connections
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

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

    # Create a simple Gemini client for chat (fallback from ADK for now)
    try:
        chat_client = genai.Client()
        chat_model = "gemini-2.5-flash"
    except Exception:
        chat_client = None
        chat_model = None

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

    # Simple conversation history (in-memory for demo)
    conversation_history = {}

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
        user_id = body.get("user_id", "demo_user")
        session_id = body.get("session_id", "demo_session")

        def _call_llm() -> dict:
            try:
                if chat_client is None:
                    return {"reply": "Chat functionality is not available right now."}
                
                # Get conversation history for this session
                if session_id not in conversation_history:
                    conversation_history[session_id] = []
                
                # Build conversation context
                messages = []
                
                # Add system prompt
                if chat_system_prompt:
                    messages.append({"role": "system", "parts": [{"text": chat_system_prompt}]})
                
                # Add conversation history
                for msg in conversation_history[session_id][-10:]:  # Keep last 10 messages
                    messages.append(msg)
                
                # Add current user message
                messages.append({"role": "user", "parts": [{"text": user_input}]})
                
                # Call Gemini
                response = chat_client.models.generate_content(
                    model=chat_model,
                    contents=messages
                )
                
                response_text = response.text
                
                # Update conversation history
                conversation_history[session_id].append({"role": "user", "parts": [{"text": user_input}]})
                conversation_history[session_id].append({"role": "model", "parts": [{"text": response_text}]})
                
                # Check if this is a collaborative request first
                if "COLLABORATIVE_REQUEST:" in response_text:
                    # Extract the details and route to collaborative middleware
                    collaborative_details = response_text.split("COLLABORATIVE_REQUEST:", 1)[1].strip()
                    
                    # Get user ID from preferences or use a default
                    user_id = preferences.get("_user_id", "demo_user_id")  # We'll need to set this when creating the agent
                    
                    # Create collaborative request
                    collaborative_input = {
                        "user_id": user_id,
                        "request_text": collaborative_details,
                        "location": "San Francisco"
                    }
                    
                    # Call collaborative middleware
                    try:
                        resp = requests.post(
                            "http://localhost:8002/collaborative-request",
                            headers={"Content-Type": "application/json"},
                            json=collaborative_input,
                            timeout=180,
                        )
                        if resp.status_code == 200:
                            collaborative_result = resp.json()
                            
                            if collaborative_result.get("success"):
                                final_response = collaborative_result.get("recommendation", "Successfully processed collaborative request")
                                conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": final_response}]}
                                return {"reply": final_response}
                            else:
                                error_message = collaborative_result.get("message", "Unknown error")
                                fallback_response = f"I had trouble processing your collaborative request: {error_message}"
                                conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                                return {"reply": fallback_response}
                        else:
                            fallback_response = f"I tried to process your collaborative request, but the collaborative service had an issue. Let me help you in another way: {response_text.replace('COLLABORATIVE_REQUEST:', '').strip()}"
                            conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                            return {"reply": fallback_response}
                    except Exception as e:
                        fallback_response = f"I'd love to help you with your collaborative request, but I'm having trouble connecting to the collaborative service right now. Can you try again in a moment?"
                        conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                        return {"reply": fallback_response}
                
                # Check if this is a restaurant request
                if "RESTAURANT_REQUEST:" in response_text:
                    # Extract the details and route to restaurant selector
                    restaurant_details = response_text.split("RESTAURANT_REQUEST:", 1)[1].strip()
                    
                    # Create restaurant request with user preferences
                    restaurant_input = {
                        "text_query": restaurant_details,
                        "location": "San Francisco",  # Default, could be extracted from query
                    }
                    
                    # Merge user preferences
                    if preferences:
                        food_prefs = preferences.get("food", {})
                        if food_prefs.get("dietary_restrictions"):
                            restaurant_input["dietary_restrictions"] = food_prefs["dietary_restrictions"]
                        if food_prefs.get("budget_level"):
                            restaurant_input["budget_level"] = food_prefs["budget_level"]
                        if food_prefs.get("cuisines"):
                            restaurant_input["cuisines"] = food_prefs["cuisines"]
                        if food_prefs.get("atmosphere_preferences"):
                            restaurant_input["atmosphere_preferences"] = food_prefs["atmosphere_preferences"]
                    
                    # Call restaurant selector
                    try:
                        resp = requests.post(
                            "http://localhost:8080/invoke",
                            headers={"Content-Type": "application/json"},
                            json=restaurant_input,
                            timeout=180,
                        )
                        if resp.status_code == 200:
                            restaurant_result = resp.json()
                            if "recommendation" in restaurant_result:
                                final_response = f"I found a great restaurant recommendation for you!\n\n{restaurant_result['recommendation']}"
                                # Update conversation history with the final response
                                conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": final_response}]}
                                return {"reply": final_response}
                            else:
                                final_response = f"Here's what I found:\n\n{restaurant_result}"
                                conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": final_response}]}
                                return {"reply": final_response}
                        else:
                            fallback_response = f"I tried to find a restaurant for you, but the restaurant service had an issue. Let me help you in another way: {response_text.replace('RESTAURANT_REQUEST:', '').strip()}"
                            conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                            return {"reply": fallback_response}
                    except Exception as e:
                        fallback_response = f"I'd love to help you find a restaurant, but I'm having trouble connecting to the restaurant service right now. Can you try again in a moment?"
                        conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                        return {"reply": fallback_response}
                
                # Check if this is a concert request
                if "CONCERT_REQUEST:" in response_text:
                    # Extract the details and route to concert selector
                    concert_details = response_text.split("CONCERT_REQUEST:", 1)[1].strip()
                    
                    # Create concert request with user preferences
                    concert_input = {
                        "text_query": concert_details,
                        "location": "San Francisco",  # Default, could be extracted from query
                    }
                    
                    # Merge user preferences
                    if preferences:
                        music_prefs = preferences.get("music", {})
                        if music_prefs.get("genres"):
                            concert_input["genres"] = music_prefs["genres"]
                        if music_prefs.get("budget_level"):
                            concert_input["budget_level"] = music_prefs["budget_level"]
                        if music_prefs.get("artist_preferences"):
                            concert_input["artist_preferences"] = music_prefs["artist_preferences"]
                        if music_prefs.get("atmosphere_preferences"):
                            concert_input["atmosphere_preferences"] = music_prefs["atmosphere_preferences"]
                    
                    # Call concert selector
                    try:
                        resp = requests.post(
                            "http://localhost:8081/invoke",
                            headers={"Content-Type": "application/json"},
                            json=concert_input,
                            timeout=180,
                        )
                        if resp.status_code == 200:
                            concert_result = resp.json()
                            if "recommendation" in concert_result:
                                final_response = f"I found a great concert recommendation for you!\n\n{concert_result['recommendation']}"
                                # Update conversation history with the final response
                                conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": final_response}]}
                                return {"reply": final_response}
                            else:
                                final_response = f"Here's what I found:\n\n{concert_result}"
                                conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": final_response}]}
                                return {"reply": final_response}
                        else:
                            fallback_response = f"I tried to find a concert for you, but the concert service had an issue. Let me help you in another way: {response_text.replace('CONCERT_REQUEST:', '').strip()}"
                            conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                            return {"reply": fallback_response}
                    except Exception as e:
                        fallback_response = f"I'd love to help you find a concert, but I'm having trouble connecting to the concert service right now. Can you try again in a moment?"
                        conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                        return {"reply": fallback_response}
                
                return {"reply": response_text}
                
            except Exception as e:
                return {"reply": f"I'm having trouble processing your request right now. Error: {str(e)}"}

        llm_reply = await anyio.to_thread.run_sync(_call_llm)
        return llm_reply

    @app.post("/chat")
    async def chat_endpoint(body: dict):
        """Dedicated chat endpoint for frontend integration with ADK support."""
        user_input = body.get("message", "")
        user_id = body.get("user_id", "demo_user")
        session_id = body.get("session_id", "demo_session")
        
        if not user_input:
            return {"reply": "Please provide a message."}
        
        try:
            response_text = None
            
            # Try ADK first
            if adk_agent is not None:
                try:
                    app_name = f"personal_agent_{name.lower().replace(' ', '_')}"
                    runner = await get_adk_runner(adk_agent, app_name, user_id, session_id)
                    
                    if runner is not None:
                        response_text = await call_adk_agent(user_input, runner, user_id, session_id)
                        print(f"[INFO] ADK response: {response_text[:100]}..." if response_text else "[INFO] ADK response: None")
                        
                except Exception as e:
                    print(f"[WARNING] ADK failed, falling back to Gemini client: {e}")
                    response_text = None
            
            # Fallback to original Gemini client if ADK fails
            if response_text is None:
                if chat_client is None:
                    return {"reply": "Chat functionality is not available right now."}
                
                # Get conversation history for this session
                if session_id not in conversation_history:
                    conversation_history[session_id] = []
                
                # Build conversation context
                messages = []
                
                # Add system prompt
                if chat_system_prompt:
                    messages.append({"role": "system", "parts": [{"text": chat_system_prompt}]})
                
                # Add conversation history
                for msg in conversation_history[session_id][-10:]:  # Keep last 10 messages
                    messages.append(msg)
                
                # Add current user message
                messages.append({"role": "user", "parts": [{"text": user_input}]})
                
                # Call Gemini
                response = chat_client.models.generate_content(
                    model=chat_model,
                    contents=messages
                )
                
                response_text = response.text
                
                # Update conversation history
                conversation_history[session_id].append({"role": "user", "parts": [{"text": user_input}]})
                conversation_history[session_id].append({"role": "model", "parts": [{"text": response_text}]})
            
            # Check if this is a collaborative request first
            if response_text and "COLLABORATIVE_REQUEST:" in response_text:
                # Extract the details and route to collaborative middleware
                collaborative_details = response_text.split("COLLABORATIVE_REQUEST:", 1)[1].strip()
                
                # Get user ID from preferences or use a default
                user_id = preferences.get("_user_id", "demo_user_id")  # We'll need to set this when creating the agent
                
                # Create collaborative request
                collaborative_input = {
                    "user_id": user_id,
                    "request_text": collaborative_details,
                    "location": "San Francisco"
                }
                
                # Call collaborative middleware
                try:
                    resp = requests.post(
                        "http://localhost:8002/collaborative-request",
                        headers={"Content-Type": "application/json"},
                        json=collaborative_input,
                        timeout=180,
                    )
                    if resp.status_code == 200:
                        collaborative_result = resp.json()
                        
                        if collaborative_result.get("success"):
                            final_response = collaborative_result.get("recommendation", "Successfully processed collaborative request")
                            # Update conversation history with the final response (only if using fallback client)
                            if session_id in conversation_history and conversation_history[session_id]:
                                conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": final_response}]}
                            return {"reply": final_response}
                        else:
                            error_message = collaborative_result.get("message", "Unknown error")
                            fallback_response = f"I had trouble processing your collaborative request: {error_message}"
                            # Update conversation history with the final response (only if using fallback client)
                            if session_id in conversation_history and conversation_history[session_id]:
                                conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                            return {"reply": fallback_response}
                    else:
                        fallback_response = f"I tried to process your collaborative request, but the collaborative service had an issue. Let me help you in another way: {response_text.replace('COLLABORATIVE_REQUEST:', '').strip()}"
                        # Update conversation history with the final response (only if using fallback client)
                        if session_id in conversation_history and conversation_history[session_id]:
                            conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                        return {"reply": fallback_response}
                except Exception as e:
                    fallback_response = f"I'd love to help you with your collaborative request, but I'm having trouble connecting to the collaborative service right now. Can you try again in a moment?"
                    # Update conversation history with the final response (only if using fallback client)
                    if session_id in conversation_history and conversation_history[session_id]:
                        conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                    return {"reply": fallback_response}
            
            # Check if this is a restaurant request
            if response_text and "RESTAURANT_REQUEST:" in response_text:
                # Extract the details and route to restaurant selector
                restaurant_details = response_text.split("RESTAURANT_REQUEST:", 1)[1].strip()
                
                # Create restaurant request with user preferences
                restaurant_input = {
                    "text_query": restaurant_details,
                    "location": "San Francisco",  # Default, could be extracted from query
                }
                
                # Merge user preferences
                if preferences:
                    food_prefs = preferences.get("food", {})
                    if food_prefs.get("dietary_restrictions"):
                        restaurant_input["dietary_restrictions"] = food_prefs["dietary_restrictions"]
                    if food_prefs.get("budget_level"):
                        restaurant_input["budget_level"] = food_prefs["budget_level"]
                    if food_prefs.get("cuisines"):
                        restaurant_input["cuisines"] = food_prefs["cuisines"]
                    if food_prefs.get("atmosphere_preferences"):
                        restaurant_input["atmosphere_preferences"] = food_prefs["atmosphere_preferences"]
                
                # Call restaurant selector
                try:
                    resp = requests.post(
                        "http://localhost:8080/invoke",
                        headers={"Content-Type": "application/json"},
                        json=restaurant_input,
                        timeout=180,
                    )
                    if resp.status_code == 200:
                        restaurant_result = resp.json()
                        
                        # Handle both task format and direct recommendation format
                        recommendation_text = None
                        if "recommendation" in restaurant_result:
                            recommendation_text = restaurant_result["recommendation"]
                        elif "artifacts" in restaurant_result and restaurant_result["artifacts"]:
                            # Extract from task format
                            artifact = restaurant_result["artifacts"][0]
                            if "parts" in artifact and artifact["parts"]:
                                recommendation_text = artifact["parts"][0].get("text", "")
                        
                        if recommendation_text:
                            final_response = f"I found a great restaurant recommendation for you!\n\n{recommendation_text}"
                            # Update conversation history with the final response (only if using fallback client)
                            if session_id in conversation_history and conversation_history[session_id]:
                                conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": final_response}]}
                            return {"reply": final_response}
                        else:
                            final_response = f"Here's what I found:\n\n{restaurant_result}"
                            # Update conversation history with the final response (only if using fallback client)
                            if session_id in conversation_history and conversation_history[session_id]:
                                conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": final_response}]}
                            return {"reply": final_response}
                    else:
                        fallback_response = f"I tried to find a restaurant for you, but the restaurant service had an issue. Let me help you in another way: {response_text.replace('RESTAURANT_REQUEST:', '').strip()}"
                        # Update conversation history with the final response (only if using fallback client)
                        if session_id in conversation_history and conversation_history[session_id]:
                            conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                        return {"reply": fallback_response}
                except Exception as e:
                    fallback_response = f"I'd love to help you find a restaurant, but I'm having trouble connecting to the restaurant service right now. Can you try again in a moment?"
                    # Update conversation history with the final response (only if using fallback client)
                    if session_id in conversation_history and conversation_history[session_id]:
                        conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                    return {"reply": fallback_response}
            
            # Check if this is a concert request
            if response_text and "CONCERT_REQUEST:" in response_text:
                # Extract the details and route to concert selector
                concert_details = response_text.split("CONCERT_REQUEST:", 1)[1].strip()
                
                # Create concert request with user preferences
                concert_input = {
                    "text_query": concert_details,
                    "location": "San Francisco",  # Default, could be extracted from query
                }
                
                # Merge user preferences
                if preferences:
                    music_prefs = preferences.get("music", {})
                    if music_prefs.get("genres"):
                        concert_input["genres"] = music_prefs["genres"]
                    if music_prefs.get("budget_level"):
                        concert_input["budget_level"] = music_prefs["budget_level"]
                    if music_prefs.get("artist_preferences"):
                        concert_input["artist_preferences"] = music_prefs["artist_preferences"]
                    if music_prefs.get("atmosphere_preferences"):
                        concert_input["atmosphere_preferences"] = music_prefs["atmosphere_preferences"]
                
                # Call concert selector
                try:
                    resp = requests.post(
                        "http://localhost:8081/invoke",
                        headers={"Content-Type": "application/json"},
                        json=concert_input,
                        timeout=180,
                    )
                    if resp.status_code == 200:
                        concert_result = resp.json()
                        
                        # Handle both task format and direct recommendation format
                        recommendation_text = None
                        if "recommendation" in concert_result:
                            recommendation_text = concert_result["recommendation"]
                        elif "artifacts" in concert_result and concert_result["artifacts"]:
                            # Extract from task format
                            artifact = concert_result["artifacts"][0]
                            if "parts" in artifact and artifact["parts"]:
                                recommendation_text = artifact["parts"][0].get("text", "")
                        
                        if recommendation_text:
                            final_response = f"I found a great concert recommendation for you!\n\n{recommendation_text}"
                            # Update conversation history with the final response (only if using fallback client)
                            if session_id in conversation_history and conversation_history[session_id]:
                                conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": final_response}]}
                            return {"reply": final_response}
                        else:
                            final_response = f"Here's what I found:\n\n{concert_result}"
                            # Update conversation history with the final response (only if using fallback client)
                            if session_id in conversation_history and conversation_history[session_id]:
                                conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": final_response}]}
                            return {"reply": final_response}
                    else:
                        fallback_response = f"I tried to find a concert for you, but the concert service had an issue. Let me help you in another way: {response_text.replace('CONCERT_REQUEST:', '').strip()}"
                        # Update conversation history with the final response (only if using fallback client)
                        if session_id in conversation_history and conversation_history[session_id]:
                            conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                        return {"reply": fallback_response}
                except Exception as e:
                    fallback_response = f"I'd love to help you find a concert, but I'm having trouble connecting to the concert service right now. Can you try again in a moment?"
                    # Update conversation history with the final response (only if using fallback client)
                    if session_id in conversation_history and conversation_history[session_id]:
                        conversation_history[session_id][-1] = {"role": "model", "parts": [{"text": fallback_response}]}
                    return {"reply": fallback_response}
            
            return {"reply": response_text}
            
        except Exception as e:
            return {"reply": f"I'm having trouble processing your request right now. Error: {str(e)}"}

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