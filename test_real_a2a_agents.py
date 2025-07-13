#!/usr/bin/env python3
"""
Real A2A Multi-Agent System Test

This script tests the real A2A protocol by communicating with actual user agents,
demonstrating agent-to-agent communication, Exa API integration, and wandb tracking.
"""

import asyncio
import json
import httpx
import logging
from typing import Dict, List, Any
from dataclasses import dataclass
import time
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentEndpoint:
    """Represents an A2A agent endpoint."""
    name: str
    url: str
    port: int

class RealA2ATestClient:
    """Test client for real A2A agent communication."""
    
    def __init__(self):
        self.agents = {
            "alice": AgentEndpoint("Alice", "http://localhost:10003", 10003),
            "bob": AgentEndpoint("Bob", "http://localhost:10004", 10004),
            "charlie": AgentEndpoint("Charlie", "http://localhost:10005", 10005)
        }
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def get_agent_card(self, agent_name: str) -> Dict[str, Any]:
        """Get the agent card for a specific agent."""
        agent = self.agents[agent_name]
        try:
            response = await self.session.get(f"{agent.url}/.well-known/agent.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting agent card for {agent_name}: {e}")
            return {}
    
    async def send_a2a_message(self, agent_name: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to an A2A agent using the proper protocol."""
        agent = self.agents[agent_name]
        
        # Proper A2A message format
        a2a_message = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": message
            },
            "id": str(int(time.time() * 1000))
        }
        
        try:
            response = await self.session.post(
                f"{agent.url}/",
                json=a2a_message,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error sending message to {agent_name}: {e}")
            return {"error": str(e)}
    
    def build_a2a_message(self, text: str, role: str = "user") -> dict:
        """Build a fully A2A-compliant message payload."""
        return {
            "messageId": str(uuid.uuid4()),
            "role": role,
            "parts": [{"text": text}]
        }

    async def send_search_request(self, agent_name: str, query: str) -> Dict[str, Any]:
        """Send a search request to an agent."""
        message = self.build_a2a_message(f"search: {query}")
        return await self.send_a2a_message(agent_name, message)
    
    async def send_networking_request(self, agent_name: str, people_data: Dict[str, str]) -> Dict[str, Any]:
        """Send a networking request to an agent."""
        # Serialize people_data as a string for the message
        people_str = ", ".join([f"{k}: {v}" for k, v in people_data.items()])
        message = self.build_a2a_message(f"networking: {people_str}")
        return await self.send_a2a_message(agent_name, message)
    
    async def send_recommendation_request(self, agent_name: str, recommendation_type: str = "general") -> Dict[str, Any]:
        """Send a recommendation request to an agent."""
        message = self.build_a2a_message(f"recommendation: {recommendation_type}")
        return await self.send_a2a_message(agent_name, message)
    
    async def test_agent_discovery(self):
        """Test agent discovery by getting agent cards."""
        print("\n=== Testing Agent Discovery ===")
        
        for agent_name in self.agents:
            print(f"\nGetting agent card for {agent_name}...")
            agent_card = await self.get_agent_card(agent_name)
            
            if agent_card:
                print(f"✅ {agent_name}'s agent card:")
                print(f"   Name: {agent_card.get('name', 'Unknown')}")
                print(f"   Description: {agent_card.get('description', 'No description')}")
                
                capabilities = agent_card.get('capabilities', {})
                skills = capabilities.get('skills', [])
                print(f"   Skills: {len(skills)} skills available")
                for skill in skills:
                    print(f"     - {skill.get('name', 'Unknown')}: {skill.get('description', 'No description')}")
            else:
                print(f"❌ Failed to get agent card for {agent_name}")
    
    async def test_search_functionality(self):
        """Test search functionality using Exa API."""
        print("\n=== Testing Search Functionality (Exa API) ===")
        
        search_queries = {
            "alice": "best hiking trails in San Francisco",
            "bob": "top fine dining restaurants in New York City",
            "charlie": "indie music venues in Los Angeles"
        }
        
        for agent_name, query in search_queries.items():
            print(f"\n🔍 Testing search for {agent_name}: '{query}'")
            result = await self.send_search_request(agent_name, query)
            
            if "error" not in result:
                print(f"✅ Search successful for {agent_name}")
                if "result" in result:
                    results_data = result["result"]
                    if "results" in results_data:
                        search_results = results_data["results"]
                        print(f"   Found {len(search_results)} results")
                        for i, result_item in enumerate(search_results[:2]):  # Show first 2 results
                            title = result_item.get('title', 'No title')
                            url = result_item.get('url', 'No URL')
                            print(f"     {i+1}. {title}")
                            print(f"        URL: {url}")
            else:
                print(f"❌ Search failed for {agent_name}: {result.get('error', 'Unknown error')}")
    
    async def test_networking_functionality(self):
        """Test networking functionality between agents."""
        print("\n=== Testing Networking Functionality ===")
        
        # Create sample people data for networking
        people_data = {
            "Alice": "I love technology, programming, and outdoor activities. I'm passionate about AI and machine learning.",
            "Bob": "I'm passionate about food, cooking, and entrepreneurship. I love trying new restaurants and building business connections.",
            "Charlie": "I'm a musician and artist who loves playing guitar, going to concerts, and creative expression.",
            "Diana": "I enjoy fitness, yoga, and healthy living. I love nature walks and meditation.",
            "Eve": "I'm interested in technology, artificial intelligence, and machine learning. I enjoy coding and building projects."
        }
        
        for agent_name in self.agents:
            print(f"\n🤝 Testing networking for {agent_name}...")
            result = await self.send_networking_request(agent_name, people_data)
            
            if "error" not in result:
                print(f"✅ Networking successful for {agent_name}")
                if "result" in result:
                    networking_data = result["result"]
                    user = networking_data.get("user", "Unknown")
                    similar_people = networking_data.get("similar_people", [])
                    clusters = networking_data.get("clusters", {})
                    
                    print(f"   User: {user}")
                    print(f"   Similar people found: {len(similar_people)}")
                    for person, score in similar_people[:3]:  # Show top 3
                        print(f"     - {person}: {score:.3f}")
                    print(f"   Clusters created: {len(set(clusters.values()))}")
            else:
                print(f"❌ Networking failed for {agent_name}: {result.get('error', 'Unknown error')}")
    
    async def test_recommendation_functionality(self):
        """Test recommendation functionality."""
        print("\n=== Testing Recommendation Functionality ===")
        
        recommendation_types = {
            "alice": "general",  # General recommendations based on interests
            "bob": "restaurant",  # Restaurant recommendations
            "charlie": "general"  # General recommendations
        }
        
        for agent_name, rec_type in recommendation_types.items():
            print(f"\n🎯 Testing {rec_type} recommendations for {agent_name}...")
            result = await self.send_recommendation_request(agent_name, rec_type)
            
            if "error" not in result:
                print(f"✅ Recommendations successful for {agent_name}")
                if "result" in result:
                    rec_data = result["result"]
                    user = rec_data.get("user", "Unknown")
                    rec_type_result = rec_data.get("recommendation_type", "Unknown")
                    recommendations = rec_data.get("recommendations", [])
                    
                    print(f"   User: {user}")
                    print(f"   Type: {rec_type_result}")
                    print(f"   Recommendations found: {len(recommendations)}")
                    for i, rec in enumerate(recommendations[:2]):  # Show first 2
                        title = rec.get('title', 'No title')
                        url = rec.get('url', 'No URL')
                        print(f"     {i+1}. {title}")
                        print(f"        URL: {url}")
            else:
                print(f"❌ Recommendations failed for {agent_name}: {result.get('error', 'Unknown error')}")
    
    async def test_agent_to_agent_communication(self):
        """Test agent-to-agent communication."""
        print("\n=== Testing Agent-to-Agent Communication ===")
        
        # Test Alice asking Bob for restaurant recommendations
        print("\n🍽️ Alice asking Bob for restaurant recommendations...")
        alice_to_bob = await self.send_a2a_message("bob", self.build_a2a_message(
            "recommendation: restaurant. Hi Bob! I'm looking for some great restaurant recommendations in your area.",
            role="user"
        ))
        
        if "error" not in alice_to_bob:
            print("✅ Alice successfully communicated with Bob")
        else:
            print(f"❌ Alice-Bob communication failed: {alice_to_bob.get('error')}")
        
        # Test Charlie asking Alice for tech networking
        print("\n🎸 Charlie asking Alice for tech networking...")
        charlie_to_alice = await self.send_a2a_message("alice", self.build_a2a_message(
            "networking: Hi Alice! I'm interested in connecting with tech professionals in your network.",
            role="user"
        ))
        
        if "error" not in charlie_to_alice:
            print("✅ Charlie successfully communicated with Alice")
        else:
            print(f"❌ Charlie-Alice communication failed: {charlie_to_alice.get('error')}")
    
    async def run_comprehensive_test(self):
        """Run all tests."""
        print("🚀 Starting Real A2A Multi-Agent System Test")
        print("=" * 60)
        
        # Test 1: Agent Discovery
        await self.test_agent_discovery()
        
        # Test 2: Search Functionality (Exa API)
        await self.test_search_functionality()
        
        # Test 3: Networking Functionality
        await self.test_networking_functionality()
        
        # Test 4: Recommendation Functionality
        await self.test_recommendation_functionality()
        
        # Test 5: Agent-to-Agent Communication
        await self.test_agent_to_agent_communication()
        
        print("\n" + "=" * 60)
        print("✅ Real A2A Multi-Agent System Test Complete!")
        print("\n📊 Check your Weights & Biases dashboard for tracking data:")
        print("   Project: agent-networking")
        print("   Runs: user-agent-alice, user-agent-bob, user-agent-charlie")
    
    async def close(self):
        """Close the HTTP session."""
        await self.session.aclose()

async def main():
    """Main test function."""
    client = RealA2ATestClient()
    
    try:
        await client.run_comprehensive_test()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main()) 