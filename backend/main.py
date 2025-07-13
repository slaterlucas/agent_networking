#!/usr/bin/env python3
"""
Backend API Server for Agent Networking Frontend

Provides REST API endpoints and WebSocket connections for the frontend
to communicate with the A2A agents.
"""

import os
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Networking API configuration
NETWORKING_API_URL = "http://localhost:8001"

# Pydantic models for API
class AgentInfo(BaseModel):
    id: str
    name: str
    type: str = Field(..., description="personal or service")
    status: str = Field(..., description="online, offline, or busy")
    last_activity: str
    avatar: str
    capabilities: List[str] = []
    location: Optional[str] = None

class Message(BaseModel):
    id: str
    text: str
    sender: str = Field(..., description="user or agent")
    timestamp: str
    agent_name: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    agent_id: Optional[str] = None

class Location(BaseModel):
    id: str
    name: str
    type: str
    coordinates: Dict[str, float]
    agents: List[str]
    status: str
    description: str

class AgentSettings(BaseModel):
    enabled: bool
    permissions: List[str]
    privacy_settings: Dict[str, bool]
    notification_settings: Dict[str, bool]

# Networking models
class NetworkingRequest(BaseModel):
    target_person: str
    k: int = 5

class ClusteringRequest(BaseModel):
    n_clusters: int = 3
    method: str = "kmeans"

class PersonProfile(BaseModel):
    name: str
    preferences: str
    interests: Optional[List[str]] = None
    location: Optional[str] = None

# FastAPI app
app = FastAPI(
    title="Agent Networking API",
    description="Backend API for Agent Networking frontend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
agents_db: Dict[str, AgentInfo] = {}
messages_db: List[Message] = []
locations_db: List[Location] = []
settings_db: Dict[str, AgentSettings] = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Networking API client
class NetworkingAPIClient:
    def __init__(self, base_url: str = NETWORKING_API_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def find_similar_people(self, target_person: str, k: int = 5):
        """Find similar people using the networking API."""
        try:
            response = await self.client.post(
                f"{self.base_url}/networking/similar",
                json={"target_person": target_person, "k": k}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error calling networking API: {e}")
            return {"target_person": target_person, "similar_people": []}
    
    async def cluster_people(self, n_clusters: int = 3, method: str = "kmeans"):
        """Cluster people using the networking API."""
        try:
            response = await self.client.post(
                f"{self.base_url}/networking/cluster",
                json={"n_clusters": n_clusters, "method": method}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error calling clustering API: {e}")
            return {"clusters": {}, "cluster_members": {}}
    
    async def get_networking_stats(self):
        """Get networking system statistics."""
        try:
            response = await self.client.get(f"{self.base_url}/networking/stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting networking stats: {e}")
            return {"total_people": 0, "has_clusters": False}
    
    async def add_person(self, person: PersonProfile):
        """Add a person to the networking system."""
        try:
            response = await self.client.post(
                f"{self.base_url}/networking/add-person",
                json=person.dict()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error adding person to networking: {e}")
            return {"message": "Failed to add person", "person": person.dict()}

networking_client = NetworkingAPIClient()

# Initialize mock data
def initialize_mock_data():
    """Initialize mock data for development."""
    global agents_db, messages_db, locations_db, settings_db
    
    # Mock agents
    agents_db = {
        "alice": AgentInfo(
            id="alice",
            name="Alice's Agent",
            type="personal",
            status="online",
            last_activity="2 minutes ago",
            avatar="A",
            capabilities=["search", "networking", "recommendations", "clustering"],
            location="San Francisco"
        ),
        "bob": AgentInfo(
            id="bob",
            name="Bob's Agent",
            type="personal",
            status="online",
            last_activity="5 minutes ago",
            avatar="B",
            capabilities=["search", "networking", "recommendations", "clustering"],
            location="San Francisco"
        ),
        "charlie": AgentInfo(
            id="charlie",
            name="Charlie's Agent",
            type="personal",
            status="online",
            last_activity="1 minute ago",
            avatar="C",
            capabilities=["search", "networking", "recommendations", "clustering"],
            location="San Francisco"
        ),
        "restaurant_finder": AgentInfo(
            id="restaurant_finder",
            name="Restaurant Finder",
            type="service",
            status="online",
            last_activity="1 hour ago",
            avatar="R",
            capabilities=["search", "location", "recommendations"],
            location="San Francisco"
        ),
        "event_coordinator": AgentInfo(
            id="event_coordinator",
            name="Event Coordinator",
            type="service",
            status="busy",
            last_activity="30 minutes ago",
            avatar="E",
            capabilities=["calendar", "scheduling"],
            location="San Francisco"
        )
    }
    
    # Mock messages
    messages_db = [
        Message(
            id="1",
            text="Hi! I'm Alice's personal agent. How can I help you today?",
            sender="agent",
            timestamp="10:30 AM",
            agent_name="Alice's Agent"
        ),
        Message(
            id="2",
            text="I'd like to plan lunch with Bob tomorrow. Can you coordinate with his agent?",
            sender="user",
            timestamp="10:31 AM"
        ),
        Message(
            id="3",
            text="I'll reach out to Bob's agent right away. What are your preferences for lunch?",
            sender="agent",
            timestamp="10:31 AM",
            agent_name="Alice's Agent"
        )
    ]
    
    # Mock locations
    locations_db = [
        Location(
            id="1",
            name="Fusion Bistro",
            type="restaurant",
            coordinates={"lat": 37.7749, "lng": -122.4194},
            agents=["Alice's Agent", "Bob's Agent", "Restaurant Finder"],
            status="active",
            description="Italian-Japanese fusion restaurant"
        ),
        Location(
            id="2",
            name="Tech Startup Office",
            type="office",
            coordinates={"lat": 37.7849, "lng": -122.4094},
            agents=["Charlie's Agent"],
            status="planned",
            description="Team meeting location"
        )
    ]
    
    # Mock settings
    settings_db = {
        "alice": AgentSettings(
            enabled=True,
            permissions=["location", "calendar", "preferences", "communication"],
            privacy_settings={
                "share_location": True,
                "share_calendar": True,
                "share_preferences": False
            },
            notification_settings={
                "collaborations": True,
                "recommendations": True,
                "reports": False
            }
        )
    }

# Map agent_id to agent HTTP endpoint
AGENT_ENDPOINTS = {
    'alice': 'http://localhost:10003/a2a/execute',
    'bob': 'http://localhost:10004/a2a/execute',
    'charlie': 'http://localhost:10005/a2a/execute',
}

# API Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Agent Networking API", "version": "1.0.0"}

@app.get("/api/agents", response_model=List[AgentInfo])
async def get_agents():
    """Get all agents."""
    return list(agents_db.values())

@app.get("/api/agents/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str):
    """Get a specific agent."""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]

@app.get("/api/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get agent status."""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": agents_db[agent_id].status}

@app.post("/api/chat")
async def send_message(request: ChatRequest):
    """Send a message to an agent and get response."""
    try:
        # Add user message to database
        user_message = Message(
            id=str(len(messages_db) + 1),
            text=request.message,
            sender="user",
            timestamp=datetime.now().strftime("%I:%M %p"),
        )
        messages_db.append(user_message)
        
        # Determine which agent to send to
        agent_id = request.agent_id or "alice"  # Default to Alice
        
        if agent_id in AGENT_ENDPOINTS:
            # Forward to the actual agent
            agent_url = AGENT_ENDPOINTS[agent_id]
            
            try:
                async with httpx.AsyncClient() as client:
                    # Create A2A-compatible request
                    a2a_request = {
                        "message": {
                            "messageId": str(len(messages_db)),
                            "role": "user",
                            "parts": [{"kind": "text", "text": request.message}]
                        },
                        "contextId": str(len(messages_db))
                    }
                    
                    response = await client.post(agent_url, json=a2a_request, timeout=30.0)
                    
                    if response.status_code == 200:
                        # Parse A2A response
                        a2a_response = response.json()
                        agent_response_text = "I received your message and will process it."
                        
                        # Try to extract text from A2A response
                        if "status" in a2a_response and "message" in a2a_response["status"]:
                            message_parts = a2a_response["status"]["message"].get("parts", [])
                            for part in message_parts:
                                if part.get("kind") == "text" and part.get("text"):
                                    agent_response_text = part["text"]
                                    break
                        
                        # Add agent response to database
                        agent_message = Message(
                            id=str(len(messages_db) + 1),
                            text=agent_response_text,
                            sender="agent",
                            timestamp=datetime.now().strftime("%I:%M %p"),
                            agent_name=agents_db.get(agent_id, AgentInfo(id=agent_id, name=f"{agent_id.title()}'s Agent", type="personal", status="online", last_activity="now", avatar=agent_id[0].upper(), capabilities=[])).name
                        )
                        messages_db.append(agent_message)
                        
                        # Broadcast to WebSocket clients
                        await manager.broadcast(json.dumps({
                            "type": "message",
                            "data": agent_message.dict()
                        }))
                        
                        return {"message": "Message sent successfully", "response": agent_response_text}
                    else:
                        # Fallback response if agent is not available
                        fallback_response = f"Agent {agent_id} is currently unavailable. Please try again later."
                        agent_message = Message(
                            id=str(len(messages_db) + 1),
                            text=fallback_response,
                            sender="agent",
                            timestamp=datetime.now().strftime("%I:%M %p"),
                            agent_name=f"{agent_id.title()}'s Agent"
                        )
                        messages_db.append(agent_message)
                        
                        return {"message": "Agent unavailable", "response": fallback_response}
                        
            except Exception as e:
                logger.error(f"Error communicating with agent {agent_id}: {e}")
                error_response = f"[Agent error: {str(e)}]"
                agent_message = Message(
                    id=str(len(messages_db) + 1),
                    text=error_response,
                    sender="agent",
                    timestamp=datetime.now().strftime("%I:%M %p"),
                    agent_name=f"{agent_id.title()}'s Agent"
                )
                messages_db.append(agent_message)
                
                return {"message": "Error communicating with agent", "response": error_response}
        else:
            # Mock response for unknown agents
            mock_response = f"Hello! I'm {agent_id.title()}'s agent. How can I help you?"
            agent_message = Message(
                id=str(len(messages_db) + 1),
                text=mock_response,
                sender="agent",
                timestamp=datetime.now().strftime("%I:%M %p"),
                agent_name=f"{agent_id.title()}'s Agent"
            )
            messages_db.append(agent_message)
            
            return {"message": "Message sent successfully", "response": mock_response}
            
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages", response_model=List[Message])
async def get_messages(limit: int = 50):
    """Get recent messages."""
    return messages_db[-limit:] if messages_db else []

@app.get("/api/locations", response_model=List[Location])
async def get_locations():
    """Get all locations."""
    return locations_db

@app.get("/api/activities")
async def get_activities():
    """Get recent activities."""
    # Get networking stats to include in activities
    networking_stats = await networking_client.get_networking_stats()
    
    activities = [
        {
            "id": "1",
            "type": "networking",
            "title": "People Clustering Analysis",
            "description": f"Analyzed {networking_stats.get('total_people', 0)} people into {networking_stats.get('n_clusters', 0)} clusters",
            "timestamp": "2 hours ago",
            "agents": ["Alice's Agent", "Bob's Agent", "Charlie's Agent"]
        },
        {
            "id": "2", 
            "type": "collaboration",
            "title": "Lunch Planning",
            "description": "Alice and Bob coordinated lunch plans",
            "timestamp": "1 hour ago",
            "agents": ["Alice's Agent", "Bob's Agent"]
        },
        {
            "id": "3",
            "type": "recommendation",
            "title": "Restaurant Recommendation",
            "description": "Found Italian-Japanese fusion restaurant",
            "timestamp": "30 minutes ago",
            "agents": ["Restaurant Finder"]
        }
    ]
    
    return activities

@app.get("/api/stats")
async def get_stats():
    """Get system statistics."""
    networking_stats = await networking_client.get_networking_stats()
    
    return {
        "total_agents": len(agents_db),
        "online_agents": len([a for a in agents_db.values() if a.status == "online"]),
        "total_messages": len(messages_db),
        "total_locations": len(locations_db),
        "networking": networking_stats
    }

@app.get("/api/settings/{agent_id}", response_model=AgentSettings)
async def get_agent_settings(agent_id: str):
    """Get agent settings."""
    if agent_id not in settings_db:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings_db[agent_id]

@app.put("/api/settings/{agent_id}")
async def update_agent_settings(agent_id: str, settings: AgentSettings):
    """Update agent settings."""
    settings_db[agent_id] = settings
    return {"message": "Settings updated successfully"}

# Networking API endpoints
@app.post("/api/networking/similar")
async def find_similar_people(request: NetworkingRequest):
    """Find similar people using the networking API."""
    result = await networking_client.find_similar_people(request.target_person, request.k)
    return result

@app.post("/api/networking/cluster")
async def cluster_people(request: ClusteringRequest):
    """Cluster people using the networking API."""
    result = await networking_client.cluster_people(request.n_clusters, request.method)
    return result

@app.get("/api/networking/clusters/{cluster_id}")
async def get_cluster_members(cluster_id: int):
    """Get members of a specific cluster."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{NETWORKING_API_URL}/networking/clusters/{cluster_id}")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error getting cluster members: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/networking/add-person")
async def add_person_to_network(person: PersonProfile):
    """Add a person to the networking system."""
    result = await networking_client.add_person(person)
    return result

@app.get("/api/networking/stats")
async def get_networking_stats():
    """Get networking system statistics."""
    result = await networking_client.get_networking_stats()
    return result

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                # Handle different message types
                if message_data.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif message_data.get("type") == "message":
                    # Broadcast message to all connected clients
                    await manager.broadcast(data)
            except json.JSONDecodeError:
                logger.error("Invalid JSON received via WebSocket")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Check networking API health
    networking_health = "unknown"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{NETWORKING_API_URL}/")
            if response.status_code == 200:
                networking_health = "healthy"
            else:
                networking_health = "unhealthy"
    except Exception as e:
        networking_health = "unreachable"
        logger.error(f"Networking API health check failed: {e}")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "main_api": "healthy",
            "networking_api": networking_health
        }
    }

@app.on_event("startup")
async def startup_event():
    """Initialize data on startup."""
    initialize_mock_data()
    logger.info("Backend API server started")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 