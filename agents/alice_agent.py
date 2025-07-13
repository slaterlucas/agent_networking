#!/usr/bin/env python3
"""
Alice's Personal A2A Agent

Alice is a tech enthusiast who loves programming, outdoor activities, and healthy living.
Her agent specializes in technology networking, outdoor activity recommendations, and healthy lifestyle tips.
"""

import uvicorn
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from user_agent_template import UserProfile, create_user_agent

# Alice's profile
alice_profile = UserProfile(
    name="Alice",
    preferences="I love technology, programming, and outdoor activities. I'm passionate about AI, machine learning, and building innovative solutions. I enjoy hiking, rock climbing, and healthy living.",
    location="San Francisco",
    budget="medium",
    dietary_restrictions=["vegetarian"],
    cuisine_preferences=["Italian", "Asian", "Mediterranean"],
    interests=["technology", "programming", "AI", "machine learning", "hiking", "rock climbing", "healthy living"],
    agent_port=10003
)

# Create Alice's agent
app = create_user_agent(alice_profile)

if __name__ == "__main__":
    print("Starting Alice's A2A Agent...")
    print(f"Agent: {alice_profile.name}")
    print(f"Location: {alice_profile.location}")
    print(f"Interests: {', '.join(alice_profile.interests)}")
    print(f"Port: {alice_profile.agent_port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=alice_profile.agent_port,
        log_level="info"
    ) 