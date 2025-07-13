#!/usr/bin/env python3
"""
Bob's Personal A2A Agent

Bob is a food enthusiast and entrepreneur who loves cooking, trying new restaurants, and networking.
His agent specializes in restaurant recommendations, food networking, and business opportunities.
"""

import uvicorn
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from user_agent_template import UserProfile, create_user_agent

# Bob's profile
bob_profile = UserProfile(
    name="Bob",
    preferences="I'm passionate about food, cooking, and entrepreneurship. I love trying new restaurants, experimenting with recipes, and building business connections. I enjoy fine dining and culinary adventures.",
    location="New York City",
    budget="high",
    dietary_restrictions=[],
    cuisine_preferences=["French", "Japanese", "Italian", "Mexican", "Thai"],
    interests=["cooking", "food", "entrepreneurship", "fine dining", "culinary arts", "business networking"],
    agent_port=10004
)

# Create Bob's agent
app = create_user_agent(bob_profile)

if __name__ == "__main__":
    print("Starting Bob's A2A Agent...")
    print(f"Agent: {bob_profile.name}")
    print(f"Location: {bob_profile.location}")
    print(f"Interests: {', '.join(bob_profile.interests)}")
    print(f"Port: {bob_profile.agent_port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=bob_profile.agent_port,
        log_level="info"
    ) 