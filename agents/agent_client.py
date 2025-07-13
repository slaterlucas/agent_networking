#!/usr/bin/env python3
"""
A2A Agent Client for Agent-to-Agent Communication

This module provides functionality for agents to communicate with each other
using the official A2A protocol and SDK patterns.
"""

import asyncio
import uuid
import httpx
from typing import Dict, Any, List, Optional
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import (
    AgentCard,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
    MessageSendParams,
    Part
)
import logging

logger = logging.getLogger(__name__)

class AgentClient:
    """Client for communicating with other A2A agents."""
    
    def __init__(self, agent_url: str):
        self.agent_url = agent_url
        self._httpx_client = httpx.AsyncClient(timeout=30)
        self.agent_card = None
        self.agent_client = None
    
    async def initialize(self):
        """Initialize the client by fetching the agent card."""
        try:
            card_resolver = A2ACardResolver(self._httpx_client, self.agent_url)
            self.agent_card = await card_resolver.get_agent_card()
            self.agent_client = A2AClient(
                self._httpx_client, 
                self.agent_card
            )
            logger.info(f"Initialized client for agent: {self.agent_card.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize client for {self.agent_url}: {e}")
            return False
    
    async def send_message(
        self, 
        text: str, 
        task_id: Optional[str] = None,
        context_id: Optional[str] = None
    ) -> Optional[Task]:
        """Send a message to the agent and return the task response."""
        if not self.agent_client:
            logger.error("Agent client not initialized")
            return None
        
        try:
            message_id = str(uuid.uuid4())
            
            # Create message parts
            parts = [Part(type="text", text=text)]
            
            # Create message payload
            message_payload = {
                "message": {
                    "role": "user",
                    "parts": [part.model_dump() for part in parts],
                    "messageId": message_id,
                }
            }
            
            if task_id:
                message_payload["message"]["taskId"] = task_id
            
            if context_id:
                message_payload["message"]["contextId"] = context_id
            
            # Create send message request
            message_request = SendMessageRequest(
                id=message_id,
                params=MessageSendParams.model_validate(message_payload)
            )
            
            # Send the message using correct API
            send_response: SendMessageResponse = await self.agent_client.send_message(
                message_request
            )
            
            logger.info(f"Sent message to {self.agent_card.name}: {text}")
            
            # Check if response is successful
            if not isinstance(send_response.root, SendMessageSuccessResponse):
                logger.error(f"Received non-success response from {self.agent_card.name}")
                return None
            
            if not isinstance(send_response.root.result, Task):
                logger.error(f"Received non-task response from {self.agent_card.name}")
                return None
            
            return send_response.root.result
            
        except Exception as e:
            logger.error(f"Error sending message to {self.agent_url}: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client."""
        await self._httpx_client.aclose()

class MultiAgentOrchestrator:
    """Orchestrator for managing multiple agent connections."""
    
    def __init__(self):
        self.agent_clients: Dict[str, AgentClient] = {}
        self.agent_cards: Dict[str, AgentCard] = {}
    
    async def add_agent(self, name: str, agent_url: str) -> bool:
        """Add an agent to the orchestrator."""
        client = AgentClient(agent_url)
        if await client.initialize():
            self.agent_clients[name] = client
            self.agent_cards[name] = client.agent_card
            logger.info(f"Added agent: {name} at {agent_url}")
            return True
        return False
    
    async def send_message_to_agent(
        self, 
        agent_name: str, 
        text: str,
        task_id: Optional[str] = None,
        context_id: Optional[str] = None
    ) -> Optional[Task]:
        """Send a message to a specific agent."""
        if agent_name not in self.agent_clients:
            logger.error(f"Agent {agent_name} not found")
            return None
        
        return await self.agent_clients[agent_name].send_message(text, task_id, context_id)
    
    def list_agents(self) -> List[Dict[str, str]]:
        """List all available agents."""
        agent_info = []
        for name, card in self.agent_cards.items():
            agent_info.append({
                "name": name,
                "description": card.description,
                "url": card.url
            })
        return agent_info
    
    async def close_all(self):
        """Close all agent connections."""
        for client in self.agent_clients.values():
            await client.close()

# Example usage and testing
async def test_agent_communication():
    """Test function for agent-to-agent communication."""
    orchestrator = MultiAgentOrchestrator()
    
    # Add agents (these would be the actual agent URLs)
    agents = {
        "Alice": "http://localhost:10003",
        "Bob": "http://localhost:10004", 
        "Charlie": "http://localhost:10005"
    }
    
    for name, url in agents.items():
        await orchestrator.add_agent(name, url)
    
    # List available agents
    print("Available agents:")
    for agent in orchestrator.list_agents():
        print(f"- {agent['name']}: {agent['description']}")
    
    # Test sending a message
    if "Alice" in orchestrator.agent_clients:
        task = await orchestrator.send_message_to_agent(
            "Alice", 
            "Hello! Can you help me with a search query?"
        )
        if task:
            print(f"Received task from Alice: {task.id}")
    
    await orchestrator.close_all()

if __name__ == "__main__":
    asyncio.run(test_agent_communication()) 