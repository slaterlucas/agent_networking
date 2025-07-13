"""
Orchestrator service for agent networking platform.

Handles:
- Google OAuth authentication
- User preferences storage
- Personal agent lifecycle management

Run with:
    uv run uvicorn orchestrator.main:app --reload --port 8000
"""

from __future__ import annotations

import json
import os
import uuid
import subprocess
import signal
from typing import Any

import databases
import sqlalchemy
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from jose import JWTError, jwt
from pydantic import BaseModel

from .preferences_schema import UserPreferences, generate_system_prompt, INTERVIEW_STEPS

# Database setup
DATABASE_URL = "sqlite:///./orchestrator/orchestrator.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Users table
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("google_sub", sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column("email", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("refresh_token", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("preferences", sqlalchemy.JSON, default={}),
)

# Create SQLite database and tables
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

# FastAPI app
app = FastAPI(title="Agent Networking Orchestrator")

# Serve static HTML in demo mode for quick prototyping
static_dir = Path(__file__).parent
app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="ui")

# Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"

# Enable demo mode (no Google login) if client ID isn't provided
DEMO_MODE = GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_ID == ""

# Security – in demo mode we allow missing auth header without raising
security = HTTPBearer(auto_error=not DEMO_MODE)

if not DEMO_MODE and not GOOGLE_CLIENT_ID:
    raise ValueError("GOOGLE_CLIENT_ID environment variable is required")

# Agent management
running_agents = {}  # user_id -> {"process": subprocess.Popen, "port": int}
BASE_AGENT_PORT = 12000

# Pydantic models
class GoogleCallbackRequest(BaseModel):
    code: str
    redirect_uri: str

class GoogleCallbackResponse(BaseModel):
    jwt: str
    user: dict

class PreferencesUpdate(BaseModel):
    preferences: dict

class InterviewStepRequest(BaseModel):
    step_id: str
    data: dict

class CreateAgentRequest(BaseModel):
    name: str = "Personal Agent"

# Startup/shutdown events
@app.on_event("startup")
async def startup():
    await database.connect()

    # When running in demo mode, ensure demo users exist
    if DEMO_MODE:
        # Demo User (existing)
        demo_user = await database.fetch_one(users.select().where(users.c.email == "demo@example.com"))
        if not demo_user:
            demo_id = str(uuid.uuid4())
            await database.execute(users.insert().values(
                id=demo_id,
                google_sub="demo_sub",
                email="demo@example.com",
                name="Demo User",
                refresh_token=None,
                preferences={
                    "food": {
                        "cuisines": ["japanese", "thai", "american"],
                        "dietary_restrictions": ["pescatarian"],
                        "budget_level": "medium",
                        "atmosphere_preferences": ["cozy", "quiet"]
                    },
                    "music": {
                        "genres": ["indie", "electronic", "jazz"],
                        "artists": ["Thom Yorke", "Bonobo", "Nils Frahm"],
                        "discovery_openness": 8
                    },
                    "social": {
                        "group_size_preference": "small",
                        "communication_style": "casual",
                        "social_energy": "moderate"
                    },
                    "location": {
                        "home_location": "San Francisco",
                        "preferred_areas": ["Mission", "Castro", "Hayes Valley"]
                    },
                    "_system_prompt": "You are Demo User's personal assistant. Demo User enjoys pescatarian Japanese, Thai, and American cuisine with a medium budget, preferring cozy and quiet atmospheres. They love indie, electronic, and jazz music and are quite open to discovering new artists. They prefer small group social settings with casual communication.",
                    "_user_id": demo_id
                },
            ))

        # Bob (existing)
        bob_user = await database.fetch_one(users.select().where(users.c.email == "bob@example.com"))
        if not bob_user:
            bob_id = "bob-test-id"
            await database.execute(users.insert().values(
                id=bob_id,
                google_sub="bob_sub",
                email="bob@example.com",
                name="Bob",
                refresh_token=None,
                preferences={
                    "food": {
                        "cuisines": ["italian", "mexican", "mediterranean"],
                        "dietary_restrictions": ["vegetarian"],
                        "budget_level": "medium",
                        "atmosphere_preferences": ["casual", "outdoor"]
                    },
                    "music": {
                        "genres": ["rock", "folk", "world"],
                        "artists": ["Pearl Jam", "Bon Iver", "Tinariwen"],
                        "discovery_openness": 6
                    },
                    "social": {
                        "group_size_preference": "medium",
                        "communication_style": "friendly",
                        "social_energy": "high"
                    },
                    "location": {
                        "home_location": "San Francisco",
                        "preferred_areas": ["North Beach", "Marina", "Sunset"]
                    },
                    "_system_prompt": "You are Bob's personal assistant. Bob loves vegetarian Italian, Mexican, and Mediterranean food and prefers casual, outdoor dining. He enjoys rock, folk, and world music and is moderately open to new discoveries. He's energetic and friendly in social settings.",
                    "_user_id": bob_id
                },
            ))

        # Alice - Tech professional with sophisticated tastes
        alice_user = await database.fetch_one(users.select().where(users.c.email == "alice@example.com"))
        if not alice_user:
            alice_id = str(uuid.uuid4())
            await database.execute(users.insert().values(
                id=alice_id,
                google_sub="alice_sub",
                email="alice@example.com",
                name="Alice",
                refresh_token=None,
                preferences={
                    "food": {
                        "cuisines": ["french", "korean", "modern_american"],
                        "dietary_restrictions": [],
                        "budget_level": "high",
                        "atmosphere_preferences": ["upscale", "innovative", "romantic"]
                    },
                    "music": {
                        "genres": ["classical", "ambient", "experimental"],
                        "artists": ["Max Richter", "Ólafur Arnalds", "Kiasmos"],
                        "discovery_openness": 9
                    },
                    "social": {
                        "group_size_preference": "small",
                        "communication_style": "professional",
                        "social_energy": "moderate"
                    },
                    "location": {
                        "home_location": "San Francisco",
                        "preferred_areas": ["SOMA", "Financial District", "Nob Hill"]
                    },
                    "professional": {
                        "industry": "technology",
                        "career_stage": "senior",
                        "interests": ["AI", "product design", "startups"]
                    },
                    "_system_prompt": "You are Alice's personal assistant. Alice has sophisticated tastes, enjoying French, Korean, and modern American cuisine with a high budget for upscale, innovative dining. She loves classical, ambient, and experimental music and is very open to new discoveries. She's a senior tech professional who prefers small group settings with professional communication.",
                    "_user_id": alice_id
                },
            ))

        # Charlie - Creative artist with eclectic preferences
        charlie_user = await database.fetch_one(users.select().where(users.c.email == "charlie@example.com"))
        if not charlie_user:
            charlie_id = str(uuid.uuid4())
            await database.execute(users.insert().values(
                id=charlie_id,
                google_sub="charlie_sub",
                email="charlie@example.com",
                name="Charlie",
                refresh_token=None,
                preferences={
                    "food": {
                        "cuisines": ["ethiopian", "vietnamese", "peruvian"],
                        "dietary_restrictions": ["vegan"],
                        "budget_level": "low",
                        "atmosphere_preferences": ["authentic", "hole-in-the-wall", "cultural"]
                    },
                    "music": {
                        "genres": ["afrobeat", "reggae", "hip-hop"],
                        "artists": ["Fela Kuti", "Burna Boy", "Kendrick Lamar"],
                        "discovery_openness": 10
                    },
                    "social": {
                        "group_size_preference": "large",
                        "communication_style": "casual",
                        "social_energy": "very_high"
                    },
                    "location": {
                        "home_location": "San Francisco",
                        "preferred_areas": ["Mission", "Haight", "Chinatown"]
                    },
                    "professional": {
                        "industry": "arts",
                        "career_stage": "early_career",
                        "interests": ["street art", "community organizing", "music production"]
                    },
                    "_system_prompt": "You are Charlie's personal assistant. Charlie loves authentic Ethiopian, Vietnamese, and Peruvian vegan cuisine on a budget, preferring hole-in-the-wall spots with cultural atmosphere. They're passionate about Afrobeat, reggae, and hip-hop music and are extremely open to new discoveries. Charlie is a creative artist who thrives in large group settings with high energy and casual communication.",
                    "_user_id": charlie_id
                },
            ))

        # Diana - Health-conscious fitness enthusiast
        diana_user = await database.fetch_one(users.select().where(users.c.email == "diana@example.com"))
        if not diana_user:
            diana_id = str(uuid.uuid4())
            await database.execute(users.insert().values(
                id=diana_id,
                google_sub="diana_sub",
                email="diana@example.com",
                name="Diana",
                refresh_token=None,
                preferences={
                    "food": {
                        "cuisines": ["mediterranean", "healthy", "salads"],
                        "dietary_restrictions": ["gluten_free", "dairy_free"],
                        "budget_level": "medium",
                        "atmosphere_preferences": ["bright", "health-conscious", "outdoor"]
                    },
                    "music": {
                        "genres": ["pop", "dance", "latin"],
                        "artists": ["Dua Lipa", "Bad Bunny", "Rosalía"],
                        "discovery_openness": 7
                    },
                    "social": {
                        "group_size_preference": "medium",
                        "communication_style": "energetic",
                        "social_energy": "high"
                    },
                    "location": {
                        "home_location": "San Francisco",
                        "preferred_areas": ["Marina", "Presidio", "Embarcadero"]
                    },
                    "professional": {
                        "industry": "fitness",
                        "career_stage": "mid_career",
                        "interests": ["nutrition", "wellness", "outdoor activities"]
                    },
                    "sports": {
                        "sports_to_play": ["running", "yoga", "cycling"],
                        "activity_level": "high",
                        "outdoor_vs_indoor": "outdoor"
                    },
                    "_system_prompt": "You are Diana's personal assistant. Diana is health-conscious, preferring Mediterranean and healthy cuisine that's gluten-free and dairy-free, with bright, outdoor dining atmospheres. She enjoys pop, dance, and Latin music and is fairly open to new discoveries. Diana is a fitness enthusiast who loves outdoor activities and prefers energetic, medium-sized social groups.",
                    "_user_id": diana_id
                },
            ))

        # AUTO-SPAWN DEMO AGENTS FOR TRUE A2A COMMUNICATION
        print("[INFO] Auto-spawning demo agents for agent-to-agent communication...")
        
        # Get all demo users that should have agents
        demo_users = [
            ("Demo User", "demo@example.com", 12000),
            ("Bob", "bob@example.com", 12001),
            ("Alice", "alice@example.com", 12002),
            ("Charlie", "charlie@example.com", 12003),
            ("Diana", "diana@example.com", 12004)
        ]
        
        for name, email, port in demo_users:
            user = await database.fetch_one(users.select().where(users.c.email == email))
            if user and user.get("preferences", {}).get("_system_prompt"):
                user_id = user["id"]
                
                # Check if agent is already running
                if user_id not in running_agents:
                    try:
                        # Prepare preferences with user ID
                        prefs = dict(user["preferences"])
                        prefs["_user_id"] = user_id
                        
                        env = {
                            **os.environ,
                            "PREFERENCES_JSON": json.dumps(prefs),
                            "A2A_REGISTRY": os.getenv("A2A_REGISTRY", "http://localhost:9000"),
                        }
                        
                        # Spawn agent process
                        import sys
                        process = subprocess.Popen([
                            sys.executable,
                            "-m",
                            "agents.personal_agent",
                            "--name", name,
                            "--port", str(port),
                        ], env=env)
                        
                        # Track the running agent
                        running_agents[user_id] = {
                            "process": process,
                            "port": port,
                            "name": name
                        }
                        
                        print(f"[INFO] ✅ Spawned {name}'s agent on port {port}")
                        
                    except Exception as e:
                        print(f"[ERROR] ❌ Failed to spawn {name}'s agent: {e}")
                else:
                    print(f"[INFO] ⏭️ {name}'s agent already running on port {running_agents[user_id]['port']}")
            else:
                print(f"[WARNING] ⚠️ {name} has no preferences or system prompt - skipping agent spawn")
        
        print(f"[INFO] 🎉 Auto-spawning complete! {len(running_agents)} agents running")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    
    # Clean up all running agents
    print("[INFO] Shutting down all running agents...")
    for user_id, agent_info in running_agents.items():
        try:
            process = agent_info["process"]
            process.terminate()
            process.wait(timeout=5)
            print(f"[INFO] ✅ Stopped {agent_info['name']}'s agent")
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"[INFO] 🔥 Force-killed {agent_info['name']}'s agent")
        except Exception as e:
            print(f"[ERROR] ❌ Error stopping {agent_info['name']}'s agent: {e}")
    
    running_agents.clear()
    print("[INFO] 🎉 All agents stopped")

# Helper functions
async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    """Extract JWT to get current user. In demo mode we fall back to default user."""
    if DEMO_MODE:
        # Always return the demo user, ignore JWT
        user = await database.fetch_one(users.select().where(users.c.email == "demo@example.com"))
        return dict(user)

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Fetch user from database
        user = await database.fetch_one(
            users.select().where(users.c.id == user_id)
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return dict(user)
    
    except JWTError:
        if DEMO_MODE:
            user = await database.fetch_one(users.select().where(users.c.email == "demo@example.com"))
            return dict(user)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def exchange_code_for_tokens(code: str, redirect_uri: str) -> dict:
    """Exchange authorization code for tokens."""
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    response = google_requests.post(token_url, data=data)
    response.raise_for_status()
    
    return response.json()

# Routes
@app.get("/")
async def root():
    return {"message": "Agent Networking Orchestrator"}

# Only register Google OAuth callback endpoint if not in demo mode
if not DEMO_MODE:
    @app.post("/auth/google/callback", response_model=GoogleCallbackResponse)
    async def google_callback(request: GoogleCallbackRequest):
        """Handle Google OAuth callback and create/login user."""
        
        try:
            # Exchange code for tokens
            token_data = await exchange_code_for_tokens(request.code, request.redirect_uri)
            
            # Verify ID token
            idinfo = id_token.verify_oauth2_token(
                token_data["id_token"], 
                google_requests.Request(), 
                GOOGLE_CLIENT_ID
            )
            
            google_sub = idinfo["sub"]
            email = idinfo["email"]
            name = idinfo.get("name", email)
            refresh_token = token_data.get("refresh_token")
            
            # Check if user exists
            existing_user = await database.fetch_one(
                users.select().where(users.c.google_sub == google_sub)
            )
            
            if existing_user:
                # Update existing user
                user_id = existing_user["id"]
                await database.execute(
                    users.update()
                    .where(users.c.id == user_id)
                    .values(
                        email=email,
                        name=name,
                        refresh_token=refresh_token or existing_user["refresh_token"]
                    )
                )
            else:
                # Create new user
                user_id = str(uuid.uuid4())
                await database.execute(
                    users.insert().values(
                        id=user_id,
                        google_sub=google_sub,
                        email=email,
                        name=name,
                        refresh_token=refresh_token,
                        preferences={}
                    )
                )
            
            # Create JWT token
            jwt_payload = {
                "user_id": user_id,
                "email": email,
                "name": name
            }
            jwt_token = jwt.encode(jwt_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            
            # Return user info
            user_info = {
                "id": user_id,
                "email": email,
                "name": name,
                "preferences": existing_user.get("preferences", {}) if existing_user else {}
            }
            
            return GoogleCallbackResponse(jwt=jwt_token, user=user_info)
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"OAuth callback failed: {str(e)}"
            )

@app.get("/auth/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "preferences": user.get("preferences", {})
    }

@app.get("/preferences")
async def get_preferences(user: dict = Depends(get_current_user)):
    """Get user preferences."""
    return user.get("preferences", {})

@app.put("/preferences")
async def update_preferences(
    request: PreferencesUpdate,
    user: dict = Depends(get_current_user)
):
    """Update user preferences."""
    # Generate system prompt from preferences
    system_prompt = generate_system_prompt(request.preferences, user["name"])
    
    # Add system prompt to preferences
    prefs = {**request.preferences, "_system_prompt": system_prompt}
    
    # Update in database
    await database.execute(
        users.update()
        .where(users.c.id == user["id"])
        .values(preferences={**prefs, "_system_prompt": system_prompt})
    )
    
    return {"message": "Preferences updated successfully", "system_prompt": system_prompt}

@app.get("/interview/steps")
async def get_interview_steps():
    """Get interview steps configuration."""
    return {"steps": INTERVIEW_STEPS}

@app.post("/interview/step")
async def submit_interview_step(
    request: InterviewStepRequest,
    user: dict = Depends(get_current_user)
):
    """Submit a single interview step."""
    # Get current preferences
    current_prefs = user.get("preferences", {})
    
    # Update with new step data
    current_prefs.update(request.data)
    
    # Save to database
    await database.execute(
        users.update()
        .where(users.c.id == user["id"])
        .values(preferences=current_prefs)
    )
    
    return {"message": "Step submitted successfully", "preferences": current_prefs}

@app.get("/interview/status")
async def get_interview_status(user: dict = Depends(get_current_user)):
    """Get interview completion status."""
    prefs = user.get("preferences", {})
    
    # Check if interview is complete (has system prompt)
    is_complete = "_system_prompt" in prefs and prefs["_system_prompt"]
    
    return {
        "is_complete": is_complete,
        "preferences": prefs,
        "system_prompt": prefs.get("_system_prompt", "")
    }

@app.post("/interview/complete")
async def complete_interview(user: dict = Depends(get_current_user)):
    """Mark interview as complete and generate system prompt."""
    prefs = user.get("preferences", {})
    
    if not prefs:
        raise HTTPException(
            status_code=400,
            detail="No preferences found. Please complete the interview first."
        )
    
    # Generate system prompt
    system_prompt = generate_system_prompt(prefs, user["name"])
    
    # Update preferences with system prompt
    prefs["_system_prompt"] = system_prompt
    
    # Save to database
    await database.execute(
        users.update()
        .where(users.c.id == user["id"])
        .values(preferences={**prefs, "_system_prompt": system_prompt})
    )
    
    return {
        "message": "Interview completed successfully",
        "system_prompt": system_prompt,
        "preferences": prefs
    }

# Agent management
@app.post("/agents/create")
async def create_personal_agent(
    request: CreateAgentRequest,
    user: dict = Depends(get_current_user)
):
    """Create a personal agent with user preferences."""
    prefs = user.get("preferences", {})
    
    # Check if interview is complete
    if "_system_prompt" not in prefs:
        raise HTTPException(
            status_code=400,
            detail="Please complete the preferences interview first"
        )
    
    # Check if user already has a running agent
    if user["id"] in running_agents:
        existing_agent = running_agents[user["id"]]
        # Check if process is still running
        if existing_agent["process"].poll() is None:
            return {
                "message": "Agent already running",
                "user_name": user["name"],
                "agent_url": f"http://localhost:{existing_agent['port']}",
                "status": "existing"
            }
        else:
            # Process died, remove from tracking
            del running_agents[user["id"]]
    
    # Find available port
    port = BASE_AGENT_PORT + len(running_agents)
    
    # Spawn personal agent process
    try:
        # Add user ID to preferences for collaborative requests
        prefs_with_user_id = {**prefs, "_user_id": user["id"]}
        
        env = {
            **os.environ,
            "PREFERENCES_JSON": json.dumps(prefs_with_user_id),
            "A2A_REGISTRY": os.getenv("A2A_REGISTRY", "http://localhost:9000"),
        }
        
        # Use the personal_agent's CLI entrypoint which accepts --name and --port
        import sys
        process = subprocess.Popen([
            sys.executable,
            "-m",
            "agents.personal_agent",
            "--name", user["name"],
            "--port", str(port),
        ], env=env)
        
        # Track the running agent
        running_agents[user["id"]] = {
            "process": process,
            "port": port,
            "name": request.name
        }
        
        return {
            "message": "Agent created successfully",
            "user_name": user["name"],
            "agent_url": f"http://localhost:{port}",
            "port": port,
            "status": "created"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to spawn agent: {str(e)}"
        )

# Health check
@app.get("/agents/status")
async def get_agent_status(user: dict = Depends(get_current_user)):
    """Get the status of the user's personal agent."""
    if user["id"] not in running_agents:
        return {"status": "not_running"}
    
    agent = running_agents[user["id"]]
    if agent["process"].poll() is None:
        return {
            "status": "running",
            "port": agent["port"],
            "agent_url": f"http://localhost:{agent['port']}",
            "name": agent["name"]
        }
    else:
        # Process died, clean up
        del running_agents[user["id"]]
        return {"status": "stopped"}

@app.delete("/agents")
async def stop_agent(user: dict = Depends(get_current_user)):
    """Stop the user's personal agent."""
    if user["id"] not in running_agents:
        raise HTTPException(status_code=404, detail="No agent running")
    
    agent = running_agents[user["id"]]
    try:
        agent["process"].terminate()
        agent["process"].wait(timeout=5)
    except subprocess.TimeoutExpired:
        agent["process"].kill()
    
    del running_agents[user["id"]]
    return {"message": "Agent stopped successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "running_agents": len(running_agents)} 