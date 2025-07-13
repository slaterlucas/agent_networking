#!/usr/bin/env python3
"""
Comprehensive A2A Agent Communication Test

This script demonstrates proper agent-to-agent communication using the official A2A SDK.
It follows the patterns from the official samples and ensures agents can communicate effectively.
"""

import asyncio
import time
import logging
from typing import Dict, Any
import uvicorn
from agents.agent_client import MultiAgentOrchestrator
from agents.user_agent_template import UserProfile, create_user_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress uvicorn cancellation errors during shutdown
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# User profiles for our agents
USER_PROFILES = {
    "Alice": UserProfile(
        name="Alice",
        preferences="I love technology, programming, and outdoor activities",
        location="San Francisco",
        budget="medium",
        dietary_restrictions=["vegetarian"],
        cuisine_preferences=["Italian", "Asian"],
        interests=["technology", "programming", "hiking"],
        agent_port=10003
    ),
    "Bob": UserProfile(
        name="Bob",
        preferences="I enjoy cooking, trying new recipes, and exploring different cuisines",
        location="New York",
        budget="high",
        dietary_restrictions=[],
        cuisine_preferences=["French", "Mediterranean"],
        interests=["cooking", "traveling", "photography"],
        agent_port=10004
    ),
    "Charlie": UserProfile(
        name="Charlie",
        preferences="I'm into fitness, yoga, and healthy living",
        location="Los Angeles",
        budget="low",
        dietary_restrictions=["vegan"],
        cuisine_preferences=["Healthy", "Organic"],
        interests=["fitness", "yoga", "meditation"],
        agent_port=10005
    )
}

async def start_agent_server(user_name: str, user_profile: UserProfile):
    """Start an agent server for a specific user."""
    try:
        app = create_user_agent(user_profile)
        logger.info(f"Starting {user_name}'s agent on port {user_profile.agent_port}")
        
        # Run the server
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=user_profile.agent_port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except asyncio.CancelledError:
        logger.info(f"{user_name}'s agent server cancelled gracefully")
    except Exception as e:
        logger.error(f"Error starting {user_name}'s agent: {e}")

async def test_agent_communication():
    """Test agent-to-agent communication."""
    logger.info("Starting A2A Agent Communication Test")
    
    # Create orchestrator
    orchestrator = MultiAgentOrchestrator()
    
    # Wait for agents to start
    logger.info("Waiting for agents to start...")
    await asyncio.sleep(5)
    
    # Add agents to orchestrator
    agent_urls = {
        name: f"http://localhost:{profile.agent_port}"
        for name, profile in USER_PROFILES.items()
    }
    
    logger.info("Connecting to agents...")
    for name, url in agent_urls.items():
        success = await orchestrator.add_agent(name, url)
        if success:
            logger.info(f"✓ Connected to {name}'s agent")
        else:
            logger.error(f"✗ Failed to connect to {name}'s agent")
    
    # List available agents
    logger.info("\nAvailable agents:")
    for agent in orchestrator.list_agents():
        logger.info(f"- {agent['name']}: {agent['description']}")
    
    # Test 1: Simple greeting
    logger.info("\n=== Test 1: Simple Greeting ===")
    for name in USER_PROFILES.keys():
        if name in orchestrator.agent_clients:
            task = await orchestrator.send_message_to_agent(
                name, 
                "Hello! How are you today?"
            )
            if task:
                logger.info(f"✓ {name} responded with task ID: {task.id}")
            else:
                logger.error(f"✗ {name} failed to respond")
    
    # Test 2: Search functionality
    logger.info("\n=== Test 2: Search Functionality ===")
    search_tests = [
        ("Alice", "search for machine learning tutorials"),
        ("Bob", "search for French restaurants in New York"),
        ("Charlie", "search for yoga studios near me")
    ]
    
    for name, query in search_tests:
        if name in orchestrator.agent_clients:
            task = await orchestrator.send_message_to_agent(name, query)
            if task:
                logger.info(f"✓ {name} processed search: {query}")
            else:
                logger.error(f"✗ {name} failed to process search")
    
    # Test 3: Networking functionality
    logger.info("\n=== Test 3: Networking Functionality ===")
    for name in USER_PROFILES.keys():
        if name in orchestrator.agent_clients:
            task = await orchestrator.send_message_to_agent(
                name, 
                "Can you help me with networking opportunities?"
            )
            if task:
                logger.info(f"✓ {name} responded to networking request")
            else:
                logger.error(f"✗ {name} failed to respond to networking request")
    
    # Test 4: Recommendations
    logger.info("\n=== Test 4: Recommendations ===")
    recommendation_tests = [
        ("Alice", "recommendation restaurant"),
        ("Bob", "recommendation activities"),
        ("Charlie", "recommendation restaurant")
    ]
    
    for name, query in recommendation_tests:
        if name in orchestrator.agent_clients:
            task = await orchestrator.send_message_to_agent(name, query)
            if task:
                logger.info(f"✓ {name} provided recommendations")
            else:
                logger.error(f"✗ {name} failed to provide recommendations")
    
    # Test 5: Cross-agent communication
    logger.info("\n=== Test 5: Cross-Agent Communication ===")
    if "Alice" in orchestrator.agent_clients and "Bob" in orchestrator.agent_clients:
        # Alice asks Bob about cooking
        task = await orchestrator.send_message_to_agent(
            "Alice", 
            "I'm interested in learning to cook. Can you help me find cooking resources?"
        )
        if task:
            logger.info("✓ Alice successfully communicated with Bob about cooking")
        else:
            logger.error("✗ Alice failed to communicate with Bob")
    
    # Cleanup
    await orchestrator.close_all()
    logger.info("✓ Agent communication test completed")

async def main():
    """Main function to run the agent communication test."""
    logger.info("Starting A2A Agent Communication System")
    
    # Start all agent servers in the background
    server_tasks = []
    for name, profile in USER_PROFILES.items():
        task = asyncio.create_task(start_agent_server(name, profile))
        server_tasks.append(task)
    
    # Wait a bit for servers to start
    await asyncio.sleep(3)
    
    # Run the communication test
    await test_agent_communication()
    
    # Graceful shutdown
    logger.info("Shutting down agent servers...")
    for task in server_tasks:
        task.cancel()
    
    # Wait for tasks to complete cancellation
    try:
        await asyncio.gather(*server_tasks, return_exceptions=True)
    except Exception as e:
        logger.debug(f"Expected cancellation during shutdown: {e}")
    
    logger.info("A2A Agent Communication System completed")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System interrupted by user")
    except Exception as e:
        logger.error(f"System error: {e}") 