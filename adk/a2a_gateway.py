"""
A2A Gateway for Agent Networking System

This module provides the HTTP/3 + gRPC gateway for agent-to-agent communication,
integrating with the existing people networking clustering system.
"""

import asyncio
import os
from typing import Dict, Any, List
from google_a2a.server import A2AServer
from google_a2a.common.types import AgentCard
from adk.personal_agent_a2a import PersonalTaskManager, personal_card
from adk.restaurant_agent_a2a import RestaurantTaskManager, restaurant_card
from adk.networking_agent_a2a import NetworkingTaskManager, networking_card
from networking.networking import PeopleNetworking
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class A2ANetworkingGateway:
    """
    A2A Gateway that integrates with the existing people networking system.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 10002):
        self.host = host
        self.port = port
        self.people_network = PeopleNetworking(max_features=1000)
        
        # Initialize agent cards and task managers
        self.cards = [personal_card, restaurant_card, networking_card]
        self.task_managers = {
            personal_card.id: PersonalTaskManager(people_network=self.people_network),
            restaurant_card.id: RestaurantTaskManager(),
            networking_card.id: NetworkingTaskManager(people_network=self.people_network),
        }
        
        # A2A Server instance
        self.server = None
        
    async def initialize_networking_data(self, people_preferences: Dict[str, str]):
        """Initialize the networking system with people preferences."""
        logger.info(f"Initializing networking data for {len(people_preferences)} people")
        self.people_network.add_people(people_preferences)
        
        # Cluster people for better networking
        clusters = self.people_network.cluster_people(n_clusters=min(5, len(people_preferences)))
        logger.info(f"Created {len(set(clusters.values()))} clusters")
        
    async def start_server(self):
        """Start the A2A server with HTTP/3 support."""
        logger.info(f"Starting A2A Gateway on {self.host}:{self.port}")
        
        self.server = A2AServer(
            agent_cards=self.cards,
            task_managers=self.task_managers,
            host=self.host,
            port=self.port,
            http3=True,        # Enable QUIC/HTTP-3
            uvloop=True,       # High-performance event loop
        )
        
        await self.server.start()
        
    async def stop_server(self):
        """Stop the A2A server."""
        if self.server:
            await self.server.stop()
            logger.info("A2A Gateway stopped")
    
    def get_networking_stats(self) -> Dict[str, Any]:
        """Get current networking statistics."""
        if self.people_network.people_data is None:
            return {"status": "not_initialized"}
        
        return {
            "total_people": len(self.people_network.people_data),
            "clusters_created": len(set(self.people_network.cluster_labels)) if self.people_network.cluster_labels is not None else 0,
            "similarity_matrix_size": self.people_network.similarity_matrix.shape if self.people_network.similarity_matrix is not None else None,
            "status": "initialized"
        }


async def serve_with_sample_data(host: str = "0.0.0.0", port: int = 10002):
    """
    Start the A2A gateway with sample networking data.
    """
    gateway = A2ANetworkingGateway(host, port)
    
    # Sample people preferences for demonstration
    sample_preferences = {
        "alice": "I love Italian food, especially vegetarian options. I enjoy quiet restaurants for business meetings and prefer places under $30.",
        "bob": "I'm a big fan of sushi and Japanese cuisine. I like trendy places with good atmosphere and don't mind spending up to $50.",
        "charlie": "I prefer healthy food, salads, and Mediterranean cuisine. I'm vegetarian and like casual dining experiences.",
        "diana": "I love trying new cuisines, especially Thai and Vietnamese. I prefer authentic places with good reviews.",
        "eve": "I enjoy comfort food, American cuisine, and family-friendly restaurants. Budget-conscious, prefer under $25.",
        "frank": "I'm into fine dining, French cuisine, and wine pairings. I appreciate excellent service and ambiance.",
        "grace": "I love Mexican food, especially authentic tacos and fresh ingredients. I prefer casual, lively atmospheres.",
        "henry": "I'm a foodie who loves experimenting with fusion cuisine. I enjoy innovative restaurants with creative menus."
    }
    
    # Initialize networking data
    await gateway.initialize_networking_data(sample_preferences)
    
    # Start the server
    await gateway.start_server()


if __name__ == "__main__":
    asyncio.run(serve_with_sample_data()) 