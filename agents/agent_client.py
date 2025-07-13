#!/usr/bin/env python3
"""
Multi-Agent Orchestrator for A2A Communication

Simple orchestrator for testing agent-to-agent communication.
"""

import asyncio
import logging
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MultiAgentOrchestrator:
    """Simple orchestrator for managing multiple A2A agents."""
    
    def __init__(self):
        self.agent_clients = {}
        self.agent_urls = {}
    
    async def add_agent(self, name: str, url: str) -> bool:
        """Add an agent to the orchestrator."""
        try:
            # Test the agent endpoint
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{url}/")
                if response.status_code == 200:
                    self.agent_clients[name] = url
                    self.agent_urls[name] = url
                    logger.info(f"Successfully added agent {name} at {url}")
                    return True
                else:
                    logger.error(f"Failed to add agent {name}: status {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Error adding agent {name}: {e}")
            return False
    
    def list_agents(self) -> list:
        """List all registered agents."""
        agents = []
        for name, url in self.agent_urls.items():
            agents.append({
                "name": name,
                "url": url,
                "description": f"A2A agent for {name}"
            })
        return agents
    
    async def send_message_to_agent(self, agent_name: str, message: str) -> Optional[Any]:
        """Send a message to a specific agent."""
        if agent_name not in self.agent_urls:
            logger.error(f"Agent {agent_name} not found")
            return None
        
        try:
            url = self.agent_urls[agent_name]
            a2a_request = {
                "message": {
                    "messageId": f"msg-{int(asyncio.get_event_loop().time())}",
                    "role": "user",
                    "parts": [{"kind": "text", "text": message}]
                },
                "contextId": f"ctx-{int(asyncio.get_event_loop().time())}"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{url}/a2a/execute", json=a2a_request)
                
                if response.status_code == 200:
                    logger.info(f"Successfully sent message to {agent_name}")
                    # Return a simple task object
                    return type('Task', (), {'id': f"task-{int(asyncio.get_event_loop().time())}"})()
                else:
                    logger.error(f"Failed to send message to {agent_name}: status {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error sending message to {agent_name}: {e}")
            return None
    
    async def close_all(self):
        """Close all agent connections."""
        self.agent_clients.clear()
        self.agent_urls.clear()
        logger.info("Closed all agent connections") 