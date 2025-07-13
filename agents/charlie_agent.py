#!/usr/bin/env python3
"""
Charlie's Personal A2A Agent

Charlie is a music enthusiast and artist who loves playing guitar, going to concerts, and creative expression.
His agent specializes in music networking, event recommendations, and artistic collaborations.
"""

import uvicorn
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from user_agent_template import UserProfile, create_user_agent

# Charlie's profile
charlie_profile = UserProfile(
    name="Charlie",
    preferences="I'm a musician and artist who loves playing guitar, going to concerts, and creative expression. I enjoy indie music, live performances, and collaborating with other artists. I'm also interested in art and painting.",
    location="Los Angeles",
    budget="medium",
    dietary_restrictions=["vegan"],
    cuisine_preferences=["Mexican", "Thai", "Mediterranean", "Ethiopian"],
    interests=["music", "guitar", "concerts", "art", "painting", "indie music", "live performances", "creative collaboration"],
    agent_port=10005
)

# Create Charlie's agent
app = create_user_agent(charlie_profile)

if __name__ == "__main__":
    print("Starting Charlie's A2A Agent...")
    print(f"Agent: {charlie_profile.name}")
    print(f"Location: {charlie_profile.location}")
    print(f"Interests: {', '.join(charlie_profile.interests)}")
    print(f"Port: {charlie_profile.agent_port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=charlie_profile.agent_port,
        log_level="info"
    ) 