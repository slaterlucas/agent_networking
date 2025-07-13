#!/usr/bin/env python3
"""
A2A Protocol Test Client

This script tests the A2A protocol by simulating multiple users with different preferences
and testing agent-to-agent communication using the real A2A protocol.
"""

import asyncio
import json
import httpx
from typing import Dict, List, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    """Represents a user with preferences and networking data."""
    name: str
    preferences: str
    location: str
    budget: str
    dietary_restrictions: List[str]
    cuisine_preferences: List[str]

class A2ATestClient:
    """Test client for A2A protocol communication."""
    
    def __init__(self, base_url: str = "http://localhost:10002"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        
        # Sample users with different preferences
        self.users = {
            "alice": UserProfile(
                name="Alice",
                preferences="I love Italian food, especially vegetarian options. I enjoy quiet restaurants for business meetings and prefer places under $30.",
                location="New York City",
                budget="$20-30",
                dietary_restrictions=["vegetarian"],
                cuisine_preferences=["Italian", "Mediterranean"]
            ),
            "bob": UserProfile(
                name="Bob",
                preferences="I'm a big fan of sushi and Japanese cuisine. I like trendy places with good atmosphere and don't mind spending up to $50.",
                location="San Francisco",
                budget="$30-50",
                dietary_restrictions=[],
                cuisine_preferences=["Japanese", "Sushi", "Asian"]
            ),
            "charlie": UserProfile(
                name="Charlie",
                preferences="I prefer healthy food, salads, and Mediterranean cuisine. I'm vegetarian and like casual dining experiences.",
                location="Los Angeles",
                budget="$15-25",
                dietary_restrictions=["vegetarian", "vegan"],
                cuisine_preferences=["Mediterranean", "Healthy", "Salads"]
            ),
            "diana": UserProfile(
                name="Diana",
                preferences="I love trying new cuisines, especially Thai and Vietnamese. I prefer authentic places with good reviews.",
                location="Chicago",
                budget="$20-40",
                dietary_restrictions=[],
                cuisine_preferences=["Thai", "Vietnamese", "Asian", "Fusion"]
            ),
            "eve": UserProfile(
                name="Eve",
                preferences="I enjoy comfort food, American cuisine, and family-friendly restaurants. Budget-conscious, prefer under $25. I have two kids so need kid-friendly places.",
                location="Austin",
                budget="$15-25",
                dietary_restrictions=[],
                cuisine_preferences=["American", "Comfort Food", "Family-friendly"]
            )
        }
    
    async def test_agent_health(self) -> bool:
        """Test if the A2A agent is running and healthy."""
        try:
            # Check the agent card endpoint
            response = await self.client.get(f"{self.base_url}/.well-known/agent.json")
            if response.status_code == 200:
                agent_card = response.json()
                logger.info("✅ A2A Agent is healthy and running")
                logger.info(f"   Agent: {agent_card.get('name', 'Unknown')}")
                logger.info(f"   Skills: {[skill.get('name', 'Unknown') for skill in agent_card.get('skills', [])]}")
                return True
            else:
                logger.error(f"❌ Agent health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to A2A agent: {e}")
            return False
    
    async def send_a2a_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send a task to the A2A agent using the proper protocol."""
        task_data = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "sendTask",
            "params": {
                "task": {
                    "taskType": task_type,
                    "parameters": parameters
                }
            }
        }
        
        try:
            logger.info(f"📤 Sending A2A task: {task_type}")
            logger.info(f"   Parameters: {parameters}")
            
            response = await self.client.post(
                f"{self.base_url}/",
                json=task_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ A2A task sent successfully")
                logger.info(f"   Response: {result}")
                return result
            else:
                logger.error(f"❌ A2A task failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error sending A2A task: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_find_similar_people(self, user_name: str, target_preferences: str) -> Dict[str, Any]:
        """Test finding similar people using A2A protocol."""
        parameters = {
            "user_name": user_name,
            "target_preferences": target_preferences,
            "k": 3
        }
        
        return await self.send_a2a_task("find_similar_people", parameters)
    
    async def test_cluster_people(self, user_ids: List[str]) -> Dict[str, Any]:
        """Test clustering people using A2A protocol."""
        parameters = {
            "user_ids": user_ids,
            "n_clusters": 2
        }
        
        return await self.send_a2a_task("cluster_people", parameters)
    
    async def test_collaborative_restaurant_finding(self, user_ids: List[str], location: str) -> Dict[str, Any]:
        """Test collaborative restaurant finding using A2A protocol."""
        parameters = {
            "user_ids": user_ids,
            "location": location,
            "budget_range": "$20-40"
        }
        
        return await self.send_a2a_task("collaborative_restaurant_finding", parameters)
    
    async def run_comprehensive_test(self):
        """Run a comprehensive test of the A2A protocol."""
        logger.info("🚀 Starting Comprehensive A2A Protocol Test")
        logger.info("=" * 60)
        
        # Test 1: Agent Health Check
        logger.info("\n📋 Test 1: Agent Health Check")
        health_ok = await self.test_agent_health()
        if not health_ok:
            logger.error("❌ Agent health check failed. Cannot proceed with tests.")
            return
        
        # Test 2: Find Similar People
        logger.info("\n📋 Test 2: Find Similar People")
        alice_prefs = self.users["alice"].preferences
        similar_result = await self.test_find_similar_people("alice", alice_prefs)
        if similar_result.get("success", False):
            logger.info("✅ Find similar people test passed")
        else:
            logger.error(f"❌ Find similar people test failed: {similar_result.get('error')}")
        
        # Test 3: Cluster People
        logger.info("\n📋 Test 3: Cluster People")
        user_ids = ["alice", "bob", "charlie", "diana"]
        cluster_result = await self.test_cluster_people(user_ids)
        if cluster_result.get("success", False):
            logger.info("✅ Cluster people test passed")
        else:
            logger.error(f"❌ Cluster people test failed: {cluster_result.get('error')}")
        
        # Test 4: Collaborative Restaurant Finding
        logger.info("\n📋 Test 4: Collaborative Restaurant Finding")
        collab_result = await self.test_collaborative_restaurant_finding(
            ["alice", "bob", "charlie"], 
            "New York City"
        )
        if collab_result.get("success", False):
            logger.info("✅ Collaborative restaurant finding test passed")
        else:
            logger.error(f"❌ Collaborative restaurant finding test failed: {collab_result.get('error')}")
        
        # Test 5: Multi-user Interaction Simulation
        logger.info("\n📋 Test 5: Multi-user Interaction Simulation")
        await self._simulate_multi_user_interaction()
        
        logger.info("\n🎉 A2A Protocol Test Complete!")
        logger.info("=" * 60)
    
    async def _simulate_multi_user_interaction(self):
        """Simulate multiple users interacting through A2A protocol."""
        logger.info("   🔄 Simulating multi-user A2A interactions...")
        
        # Simulate Alice looking for dining partners
        logger.info("   👤 Alice is looking for dining partners...")
        alice_similar = await self.test_find_similar_people("alice", self.users["alice"].preferences)
        
        if alice_similar.get("success", False):
            logger.info("   🤝 Alice found similar users through A2A protocol")
        
        # Simulate group clustering
        logger.info("   👥 Creating dining groups...")
        all_users = list(self.users.keys())
        cluster_result = await self.test_cluster_people(all_users)
        
        if cluster_result.get("success", False):
            logger.info("   📊 Groups created through A2A protocol")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

async def main():
    """Main test function."""
    client = A2ATestClient()
    try:
        await client.run_comprehensive_test()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main()) 