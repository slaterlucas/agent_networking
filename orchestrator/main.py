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

    # When running in demo mode, ensure a demo user exists
    if DEMO_MODE:
        demo_user = await database.fetch_one(users.select().where(users.c.email == "demo@example.com"))
        if not demo_user:
            demo_id = str(uuid.uuid4())
            await database.execute(users.insert().values(
                id=demo_id,
                google_sub="demo_sub",
                email="demo@example.com",
                name="Demo User",
                refresh_token=None,
                preferences={},
            ))

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

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
    """Exchange OAuth code for Google tokens."""
    import httpx
    
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
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
            
            # Generate JWT
            jwt_payload = {"user_id": user_id}
            jwt_token = jwt.encode(jwt_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            
            # Fetch updated user data
            user = await database.fetch_one(
                users.select().where(users.c.id == user_id)
            )
            
            return GoogleCallbackResponse(
                jwt=jwt_token,
                user={
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "preferences": user["preferences"]
                }
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Authentication failed: {str(e)}"
            )

@app.get("/auth/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "preferences": user["preferences"]
    }

@app.get("/preferences")
async def get_preferences(user: dict = Depends(get_current_user)):
    """Get user preferences."""
    return user["preferences"]

@app.put("/preferences")
async def update_preferences(
    request: PreferencesUpdate,
    user: dict = Depends(get_current_user)
):
    """Update user preferences."""
    await database.execute(
        users.update()
        .where(users.c.id == user["id"])
        .values(preferences=request.preferences)
    )
    return {"message": "Preferences updated successfully"}

# Interview endpoints
@app.get("/interview/steps")
async def get_interview_steps():
    """Get the list of interview steps."""
    return {"steps": INTERVIEW_STEPS}

@app.post("/interview/step")
async def submit_interview_step(
    request: InterviewStepRequest,
    user: dict = Depends(get_current_user)
):
    """Submit a single interview step."""
    # Get current preferences
    current_prefs = user.get("preferences", {})
    
    # Update the specific step data
    current_prefs[request.step_id] = request.data
    
    # Save back to database
    await database.execute(
        users.update()
        .where(users.c.id == user["id"])
        .values(preferences=current_prefs)
    )
    
    return {"message": f"Step {request.step_id} saved successfully"}

@app.get("/interview/status")
async def get_interview_status(user: dict = Depends(get_current_user)):
    """Get the current interview completion status."""
    prefs = user.get("preferences", {})
    completed_steps = []
    
    for step in INTERVIEW_STEPS:
        if step["id"] in prefs and prefs[step["id"]]:
            completed_steps.append(step["id"])
    
    return {
        "completed_steps": completed_steps,
        "total_steps": len(INTERVIEW_STEPS),
        "is_complete": len(completed_steps) == len(INTERVIEW_STEPS)
    }

@app.post("/interview/complete")
async def complete_interview(user: dict = Depends(get_current_user)):
    """Mark interview as complete and generate system prompt."""
    prefs = user.get("preferences", {})
    
    # Validate that all steps are completed
    for step in INTERVIEW_STEPS:
        if step["id"] not in prefs:
            raise HTTPException(
                status_code=400,
                detail=f"Interview step '{step['id']}' is not completed"
            )
    
    # Parse preferences into structured format
    try:
        user_preferences = UserPreferences.parse_obj(prefs)
        system_prompt = generate_system_prompt(user_preferences)
        
        # Store the generated system prompt
        await database.execute(
            users.update()
            .where(users.c.id == user["id"])
            .values(preferences={**prefs, "_system_prompt": system_prompt})
        )
        
        return {
            "message": "Interview completed successfully",
            "system_prompt": system_prompt
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process preferences: {str(e)}"
        )

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
        env = {
            **os.environ,
            "PREFERENCES_JSON": json.dumps(prefs),
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
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 