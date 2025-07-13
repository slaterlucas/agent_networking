"""
Collaborative middleware for multi-user agent interactions.

Handles:
- Detecting collaborative requests (e.g., "dinner with Bob")
- Looking up users by name
- Merging preferences from multiple users
- Routing to appropriate selectors with combined preferences

Run with:
    uv run uvicorn orchestrator.collaborative_middleware:app --reload --port 8002
"""

from __future__ import annotations

import json
import re
import os
from typing import Dict, List, Optional, Any

import databases
import sqlalchemy
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from datetime import datetime, timedelta

from .preferences_schema import UserPreferences, generate_system_prompt

# Database setup (same as main orchestrator)
DATABASE_URL = "sqlite:///./orchestrator/orchestrator.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Users table (same schema as main orchestrator)
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

# FastAPI app
app = FastAPI(title="Collaborative Agent Middleware")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request/Response models
class CollaborativeRequest(BaseModel):
    user_id: str
    request_text: str
    location: Optional[str] = "San Francisco"
    time_window: Optional[List[str]] = None

class CollaborativeResponse(BaseModel):
    success: bool
    message: str
    recommendation: Optional[str] = None
    users_involved: List[str] = []
    merged_preferences: Optional[Dict] = None

# Startup/shutdown events
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Helper functions
def extract_collaborators(request_text: str) -> List[str]:
    """Extract collaborator names from request text."""
    patterns = [
        r"with\s+([A-Za-z\s]+?)(?:\s+and\s+([A-Za-z\s]+?))*(?:\s|$|[,.])",
        r"and\s+([A-Za-z\s]+?)(?:\s+and\s+([A-Za-z\s]+?))*(?:\s|$|[,.])",
        r"([A-Za-z\s]+?)\s+and\s+I",
        r"([A-Za-z\s]+?)\s+and\s+me",
    ]
    
    collaborators = []
    for pattern in patterns:
        matches = re.findall(pattern, request_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                for name in match:
                    if name and name.strip():
                        collaborators.append(name.strip().title())
            else:
                if match and match.strip():
                    collaborators.append(match.strip().title())
    
    # Clean up common false positives
    false_positives = {"I", "Me", "Us", "We", "To", "Go", "Want", "Like", "For", "A", "An", "The"}
    collaborators = [name for name in collaborators if name not in false_positives and len(name) > 1]
    
    return list(set(collaborators))  # Remove duplicates

def detect_request_type(request_text: str) -> str:
    """Detect the type of request (restaurant, concert, etc.)."""
    restaurant_keywords = ["dinner", "lunch", "breakfast", "restaurant", "food", "eat", "meal", "cuisine", "dine"]
    concert_keywords = ["concert", "music", "show", "band", "artist", "gig", "live music", "venue", "tickets"]
    
    text_lower = request_text.lower()
    
    for keyword in restaurant_keywords:
        if keyword in text_lower:
            return "restaurant"
    
    for keyword in concert_keywords:
        if keyword in text_lower:
            return "concert"
    
    return "unknown"

async def find_user_by_name(name: str) -> Optional[Dict]:
    """Find a user by their name (case-insensitive)."""
    user = await database.fetch_one(
        users.select().where(users.c.name.ilike(f"%{name}%"))
    )
    return dict(user) if user else None

async def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get a user by their ID."""
    user = await database.fetch_one(
        users.select().where(users.c.id == user_id)
    )
    return dict(user) if user else None

def merge_food_preferences(user_prefs_list: List[Dict]) -> Dict:
    """Merge food preferences from multiple users."""
    merged = {
        "cuisines": [],
        "dietary_restrictions": [],
        "budget_level": "medium",
        "atmosphere_preferences": [],
        "text_query": "",
        "location": "San Francisco"
    }
    
    all_cuisines = set()
    all_dietary_restrictions = set()
    all_atmosphere_prefs = set()
    budget_levels = []
    
    for user_prefs in user_prefs_list:
        food_prefs = user_prefs.get("food", {})
        
        # Collect cuisines
        if food_prefs.get("cuisines"):
            all_cuisines.update(food_prefs["cuisines"])
        
        # Collect dietary restrictions (intersection - must satisfy all)
        if food_prefs.get("dietary_restrictions"):
            if isinstance(food_prefs["dietary_restrictions"], list):
                all_dietary_restrictions.update(food_prefs["dietary_restrictions"])
            else:
                all_dietary_restrictions.add(food_prefs["dietary_restrictions"])
        
        # Collect atmosphere preferences
        if food_prefs.get("atmosphere_preferences"):
            all_atmosphere_prefs.update(food_prefs["atmosphere_preferences"])
        
        # Collect budget levels
        if food_prefs.get("budget_level"):
            budget_levels.append(food_prefs["budget_level"])
    
    # Set merged preferences
    merged["cuisines"] = list(all_cuisines)
    merged["dietary_restrictions"] = list(all_dietary_restrictions)
    merged["atmosphere_preferences"] = list(all_atmosphere_prefs)
    
    # For budget, take the most conservative (lowest)
    if budget_levels:
        budget_order = {"low": 1, "medium": 2, "high": 3}
        merged["budget_level"] = min(budget_levels, key=lambda x: budget_order.get(x, 2))
    
    return merged

def merge_music_preferences(user_prefs_list: List[Dict]) -> Dict:
    """Merge music preferences from multiple users."""
    merged = {
        "genres": [],
        "artist_preferences": [],
        "budget_level": "medium",
        "atmosphere_preferences": [],
        "text_query": "",
        "location": "San Francisco"
    }
    
    all_genres = set()
    all_artists = set()
    all_atmosphere_prefs = set()
    budget_levels = []
    
    for user_prefs in user_prefs_list:
        music_prefs = user_prefs.get("music", {})
        
        # Collect genres
        if music_prefs.get("genres"):
            all_genres.update(music_prefs["genres"])
        
        # Collect artists
        if music_prefs.get("artists"):
            all_artists.update(music_prefs["artists"])
        
        # Collect atmosphere preferences
        if music_prefs.get("concert_preferences"):
            all_atmosphere_prefs.update(music_prefs["concert_preferences"])
        
        # Collect budget levels
        food_prefs = user_prefs.get("food", {})
        if food_prefs.get("budget_level"):
            budget_levels.append(food_prefs["budget_level"])
    
    # Set merged preferences
    merged["genres"] = list(all_genres)
    merged["artist_preferences"] = list(all_artists)
    merged["atmosphere_preferences"] = list(all_atmosphere_prefs)
    
    # For budget, take the most conservative (lowest)
    if budget_levels:
        budget_order = {"low": 1, "medium": 2, "high": 3}
        merged["budget_level"] = min(budget_levels, key=lambda x: budget_order.get(x, 2))
    
    return merged

async def call_selector(selector_type: str, merged_prefs: Dict, port: int) -> Dict:
    """Call the appropriate selector service with merged preferences."""
    try:
        selector_url = f"http://localhost:{port}/invoke"
        
        response = requests.post(
            selector_url,
            headers={"Content-Type": "application/json"},
            json=merged_prefs,
            timeout=180,
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Selector returned status {response.status_code}"}
            
    except Exception as e:
        return {"error": f"Failed to call {selector_type} selector: {str(e)}"}

# API endpoints
@app.post("/collaborative-request", response_model=CollaborativeResponse)
async def handle_collaborative_request(request: CollaborativeRequest):
    """Handle a collaborative request involving multiple users."""
    
    # Get the requesting user
    requesting_user = await get_user_by_id(request.user_id)
    if not requesting_user:
        raise HTTPException(status_code=404, detail="Requesting user not found")
    
    # Extract collaborators from the request text
    collaborator_names = extract_collaborators(request.request_text)
    
    if not collaborator_names:
        return CollaborativeResponse(
            success=False,
            message="No collaborators detected in the request. Try phrasing like 'I want to go to dinner with Bob'",
            users_involved=[requesting_user["name"]]
        )
    
    # Find collaborator users
    collaborator_users = []
    found_names = []
    missing_names = []
    
    for name in collaborator_names:
        user = await find_user_by_name(name)
        if user:
            collaborator_users.append(user)
            found_names.append(user["name"])
        else:
            missing_names.append(name)
    
    if missing_names:
        return CollaborativeResponse(
            success=False,
            message=f"Could not find users: {', '.join(missing_names)}. Make sure they have accounts and their names are spelled correctly.",
            users_involved=[requesting_user["name"]] + found_names
        )
    
    # Detect request type
    request_type = detect_request_type(request.request_text)
    
    if request_type == "unknown":
        return CollaborativeResponse(
            success=False,
            message="Could not determine request type. Try mentioning 'dinner', 'restaurant', 'concert', or 'music'.",
            users_involved=[requesting_user["name"]] + found_names
        )
    
    # Collect all user preferences
    all_users = [requesting_user] + collaborator_users
    all_user_prefs = []
    
    for user in all_users:
        user_prefs = user.get("preferences", {})
        if user_prefs:
            all_user_prefs.append(user_prefs)
    
    if not all_user_prefs:
        return CollaborativeResponse(
            success=False,
            message="None of the users have completed their preferences. Please complete the preferences interview first.",
            users_involved=[user["name"] for user in all_users]
        )
    
    # Merge preferences based on request type
    if request_type == "restaurant":
        merged_prefs = merge_food_preferences(all_user_prefs)
        merged_prefs["text_query"] = request.request_text
        merged_prefs["location"] = request.location or "San Francisco"
        
        # Call restaurant selector
        selector_result = await call_selector("restaurant", merged_prefs, 8080)
        
    elif request_type == "concert":
        merged_prefs = merge_music_preferences(all_user_prefs)
        merged_prefs["text_query"] = request.request_text
        merged_prefs["location"] = request.location or "San Francisco"
        
        if request.time_window:
            merged_prefs["time_window"] = request.time_window
        
        # Call concert selector
        selector_result = await call_selector("concert", merged_prefs, 8081)
    
    else:
        return CollaborativeResponse(
            success=False,
            message=f"Request type '{request_type}' is not yet supported.",
            users_involved=[user["name"] for user in all_users]
        )
    
    # Process selector result
    if "error" in selector_result:
        return CollaborativeResponse(
            success=False,
            message=f"Error from {request_type} selector: {selector_result['error']}",
            users_involved=[user["name"] for user in all_users],
            merged_preferences=merged_prefs
        )
    
    # Extract recommendation from selector result
    recommendation = None
    if "recommendation" in selector_result:
        recommendation = selector_result["recommendation"]
    elif "artifacts" in selector_result and selector_result["artifacts"]:
        # Handle task format
        artifact = selector_result["artifacts"][0]
        if "parts" in artifact and artifact["parts"]:
            recommendation = artifact["parts"][0].get("text", "")
    
    if not recommendation:
        recommendation = str(selector_result)
    
    # Add collaborative context to the recommendation
    user_names = [user["name"] for user in all_users]
    collaborative_message = f"Here's a {request_type} recommendation for {', '.join(user_names[:-1])} and {user_names[-1]}:\n\n{recommendation}"
    
    if len(all_user_prefs) > 1:
        collaborative_message += f"\n\nThis recommendation considers the preferences of all {len(all_users)} users."
    
    return CollaborativeResponse(
        success=True,
        message="Successfully generated collaborative recommendation",
        recommendation=collaborative_message,
        users_involved=user_names,
        merged_preferences=merged_prefs
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "collaborative-middleware"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 