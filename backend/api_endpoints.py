#!/usr/bin/env python3
"""
Backend API Endpoints for Frontend Integration

This module provides REST API endpoints that the frontend expects,
connecting to our working A2A agents.
"""

import asyncio
import logging
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent URLs (from our working A2A agents)
AGENT_URLS = {
    'alice': 'http://localhost:10003',
    'bob': 'http://localhost:10004', 
    'charlie': 'http://localhost:10005'
}

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str
    agent_id: Optional[str] = 'alice'

class AgentResponse(BaseModel):
    id: str
    name: str
    type: str
    status: str
    last_activity: str
    capabilities: List[str]
    location: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    text: str
    sender: str
    timestamp: str
    agent_name: Optional[str] = None

class LocationResponse(BaseModel):
    id: str
    name: str
    type: str
    coordinates: Dict[str, float]
    agents: List[str]
    status: str
    description: str

class ActivityResponse(BaseModel):
    id: str
    type: str
    title: str
    description: str
    timestamp: str
    agents: List[str]

class StatsResponse(BaseModel):
    active_agents: int
    total_conversations: int
    total_locations: int
    total_collaborations: int

class AgentSettingsResponse(BaseModel):
    enabled: bool
    permissions: List[str]
    privacy_settings: Dict[str, bool]
    notification_settings: Dict[str, bool]

# Create FastAPI app
app = FastAPI(title="Agent Networking API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:5173", "http://localhost:3000"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
messages_store: List[Dict[str, Any]] = []
agents_store: Dict[str, Dict[str, Any]] = {
    'alice': {
        'id': 'alice',
        'name': 'Alice',
        'type': 'personal',
        'status': 'online',
        'last_activity': datetime.now().isoformat(),
        'capabilities': ['search', 'networking', 'recommendations'],
        'location': 'San Francisco'
    },
    'bob': {
        'id': 'bob',
        'name': 'Bob',
        'type': 'service',
        'status': 'online',
        'last_activity': datetime.now().isoformat(),
        'capabilities': ['cooking', 'restaurant_recommendations'],
        'location': 'New York'
    },
    'charlie': {
        'id': 'charlie',
        'name': 'Charlie',
        'type': 'service',
        'status': 'online',
        'last_activity': datetime.now().isoformat(),
        'capabilities': ['fitness', 'healthy_recommendations'],
        'location': 'Los Angeles'
    }
}

async def send_a2a_message(agent_name: str, message: str) -> Dict[str, Any]:
    """Send a message to an A2A agent and get response."""
    try:
        agent_url = AGENT_URLS.get(agent_name)
        if not agent_url:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
        
        # Create A2A-compatible request
        a2a_request = {
            "message": {
                "messageId": f"frontend-{datetime.now().timestamp()}",
                "role": "user",
                "parts": [{"kind": "text", "text": message}]
            },
            "contextId": f"frontend-context-{datetime.now().timestamp()}"
        }
        
        logger.info(f"[API] Sending message to {agent_name}: {message[:50]}...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{agent_url}/a2a/execute", json=a2a_request)
            
            if response.status_code == 200:
                a2a_response = response.json()
                
                # Extract text from A2A response
                response_text = "I received your message and processed it successfully."
                if "status" in a2a_response and "message" in a2a_response["status"]:
                    message_parts = a2a_response["status"]["message"].get("parts", [])
                    if message_parts and len(message_parts) > 0:
                        response_text = message_parts[0].get("text", response_text)
                
                return {
                    "success": True,
                    "agent_name": agent_name,
                    "response": response_text,
                    "a2a_response": a2a_response
                }
            else:
                logger.error(f"[API] Agent {agent_name} returned status {response.status_code}")
                return {
                    "success": False,
                    "error": f"Agent returned status {response.status_code}",
                    "agent_name": agent_name
                }
                
    except Exception as e:
        logger.error(f"[API] Error sending message to {agent_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "agent_name": agent_name
        }

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Agent Networking API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    active_agents = 0
    for agent_name, agent_url in AGENT_URLS.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{agent_url}/")
                if response.status_code == 200:
                    active_agents += 1
        except:
            pass
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": active_agents,
        "total_agents": len(AGENT_URLS)
    }

@app.get("/api/agents", response_model=List[AgentResponse])
async def get_agents():
    """Get all available agents."""
    return list(agents_store.values())

@app.get("/api/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get a specific agent."""
    if agent_id not in agents_store:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_store[agent_id]

@app.get("/api/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get agent status."""
    if agent_id not in agents_store:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check if agent is actually online
    agent_url = AGENT_URLS.get(agent_id)
    status = "offline"
    if agent_url:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{agent_url}/")
                if response.status_code == 200:
                    status = "online"
        except:
            pass
    
    return {"status": status}

@app.get("/api/messages", response_model=List[MessageResponse])
async def get_messages(limit: int = 50):
    """Get recent messages."""
    return messages_store[-limit:] if messages_store else []

@app.post("/api/chat")
async def send_message(request: ChatRequest):
    """Send a message to an agent and get response."""
    try:
        # Add user message to store
        user_message = {
            "id": f"msg-{datetime.now().timestamp()}",
            "text": request.message,
            "sender": "user",
            "timestamp": datetime.now().isoformat(),
            "agent_name": None
        }
        messages_store.append(user_message)
        
        # Send to A2A agent
        agent_id = request.agent_id or 'alice'
        result = await send_a2a_message(agent_id, request.message)
        
        if result["success"]:
            # Add agent response to store
            agent_message = {
                "id": f"agent-{datetime.now().timestamp()}",
                "text": result["response"],
                "sender": "agent",
                "timestamp": datetime.now().isoformat(),
                "agent_name": result["agent_name"].title()
            }
            messages_store.append(agent_message)
            
            # Update agent last activity
            if agent_id in agents_store:
                agents_store[agent_id]["last_activity"] = datetime.now().isoformat()
            
            return {
                "message": "Message sent successfully",
                "response": agent_message
            }
        else:
            error_message = {
                "id": f"error-{datetime.now().timestamp()}",
                "text": f"Sorry, I encountered an error: {result.get('error', 'Unknown error')}",
                "sender": "agent",
                "timestamp": datetime.now().isoformat(),
                "agent_name": result.get("agent_name", "System").title()
            }
            messages_store.append(error_message)
            
            return {
                "message": "Message sent but agent encountered an error",
                "response": error_message
            }
            
    except Exception as e:
        logger.error(f"[API] Error in send_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/locations", response_model=List[LocationResponse])
async def get_locations():
    """Get available locations."""
    return [
        {
            "id": "sf",
            "name": "San Francisco",
            "type": "city",
            "coordinates": {"lat": 37.7749, "lng": -122.4194},
            "agents": ["alice"],
            "status": "active",
            "description": "Tech hub with great restaurants"
        },
        {
            "id": "nyc",
            "name": "New York",
            "type": "city", 
            "coordinates": {"lat": 40.7128, "lng": -74.0060},
            "agents": ["bob"],
            "status": "active",
            "description": "Culinary capital with diverse cuisine"
        },
        {
            "id": "la",
            "name": "Los Angeles",
            "type": "city",
            "coordinates": {"lat": 34.0522, "lng": -118.2437},
            "agents": ["charlie"],
            "status": "active",
            "description": "Health and fitness focused city"
        }
    ]

@app.get("/api/activities", response_model=List[ActivityResponse])
async def get_activities():
    """Get recent activities."""
    return [
        {
            "id": "activity-1",
            "type": "restaurant_recommendation",
            "title": "Italian Restaurant Found",
            "description": "Alice found a great Italian restaurant in San Francisco",
            "timestamp": datetime.now().isoformat(),
            "agents": ["alice", "bob"]
        },
        {
            "id": "activity-2", 
            "type": "networking",
            "title": "Similar People Found",
            "description": "Charlie found people with similar fitness interests",
            "timestamp": datetime.now().isoformat(),
            "agents": ["charlie"]
        }
    ]

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics."""
    active_agents = 0
    for agent_url in AGENT_URLS.values():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{agent_url}/")
                if response.status_code == 200:
                    active_agents += 1
        except:
            pass
    
    return {
        "active_agents": active_agents,
        "total_conversations": len(messages_store),
        "total_locations": 3,
        "total_collaborations": len([m for m in messages_store if m["sender"] == "agent"])
    }

@app.get("/api/settings/{agent_id}", response_model=AgentSettingsResponse)
async def get_agent_settings(agent_id: str):
    """Get agent settings."""
    if agent_id not in agents_store:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "enabled": True,
        "permissions": ["read", "write", "search", "networking"],
        "privacy_settings": {
            "share_location": True,
            "share_preferences": True,
            "share_activity": False
        },
        "notification_settings": {
            "new_messages": True,
            "agent_updates": True,
            "system_alerts": False
        }
    }

@app.put("/api/settings/{agent_id}")
async def update_agent_settings(agent_id: str, settings: AgentSettingsResponse):
    """Update agent settings."""
    if agent_id not in agents_store:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # In a real app, you'd save these settings
    return {"message": "Settings updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 