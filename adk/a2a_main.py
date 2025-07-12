"""
Main A2A Agent Networking System

Entry point for the complete A2A agent networking system that combines
people clustering, restaurant recommendations, and collaborative planning.
"""

import asyncio
import os
import json
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from adk.a2a_gateway import A2ANetworkingGateway
from adk.redis_vector_store import setup_vector_store_with_preferences
from adk.exa_client import ExaSearchClient
from networking.networking import demo_example
import wandb

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class A2ANetworkingSystem:
    """
    Complete A2A Agent Networking System that orchestrates all components.
    """
    
    def __init__(self):
        """Initialize the A2A networking system."""
        self.gateway = None
        self.vector_store = None
        self.exa_client = None
        self.is_initialized = False
        
        # Load environment variables
        load_dotenv()
        
        # Initialize W&B if API key is available
        try:
            if os.getenv("WANDB_API_KEY"):
                wandb.init(
                    project="agent-networking-a2a",
                    name="a2a-system",
                    config={
                        "system": "A2A Agent Networking",
                        "components": ["gateway", "vector_store", "exa_client"],
                        "protocols": ["A2A", "HTTP/3", "gRPC"]
                    }
                )
                logger.info("W&B monitoring initialized")
        except Exception as e:
            logger.warning(f"W&B initialization failed: {e}")
    
    async def initialize(self, sample_data: Optional[Dict[str, str]] = None):
        """
        Initialize the A2A networking system.
        
        Args:
            sample_data: Optional dictionary of sample user preferences
        """
        try:
            logger.info("Initializing A2A Agent Networking System...")
            
            # Use sample data or default
            if sample_data is None:
                sample_data = self._get_default_sample_data()
            
            # Initialize components
            self.gateway = A2ANetworkingGateway()
            self.vector_store = await setup_vector_store_with_preferences(sample_data)
            self.exa_client = ExaSearchClient()
            
            # Initialize gateway with sample data
            await self.gateway.initialize_networking_data(sample_data)
            
            self.is_initialized = True
            logger.info(f"A2A system initialized with {len(sample_data)} users")
            
            # Log metrics to W&B
            if wandb.run:
                wandb.log({
                    "system_initialized": True,
                    "total_users": len(sample_data),
                    "components_active": 3
                })
            
        except Exception as e:
            logger.error(f"Error initializing A2A system: {e}")
            raise
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 10002):
        """
        Start the A2A server.
        
        Args:
            host: Server host
            port: Server port
        """
        if not self.is_initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        
        logger.info(f"Starting A2A server on {host}:{port}")
        
        try:
            # Start the gateway server
            await self.gateway.start_server()
            
        except Exception as e:
            logger.error(f"Error starting A2A server: {e}")
            raise
    
    async def stop_server(self):
        """Stop the A2A server."""
        if self.gateway:
            await self.gateway.stop_server()
            logger.info("A2A server stopped")
    
    async def test_system(self):
        """Test the A2A system with sample interactions."""
        if not self.is_initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        
        logger.info("Testing A2A system...")
        
        test_results = {}
        
        # Test 1: Vector store similarity search
        try:
            search_results = await self.vector_store.knn_search("vegetarian Italian restaurants", k=3)
            test_results["vector_search"] = {
                "success": True,
                "results_count": len(search_results),
                "users_found": [r.id for r in search_results]
            }
            logger.info(f"Vector search test: Found {len(search_results)} similar users")
        except Exception as e:
            test_results["vector_search"] = {"success": False, "error": str(e)}
            logger.error(f"Vector search test failed: {e}")
        
        # Test 2: Exa restaurant search
        try:
            restaurant_results = await self.exa_client.search_restaurants(
                "Italian vegetarian restaurants", 
                location="New York City", 
                num_results=3
            )
            test_results["restaurant_search"] = {
                "success": True,
                "results_count": len(restaurant_results),
                "restaurants": [r.title for r in restaurant_results]
            }
            logger.info(f"Restaurant search test: Found {len(restaurant_results)} restaurants")
        except Exception as e:
            test_results["restaurant_search"] = {"success": False, "error": str(e)}
            logger.error(f"Restaurant search test failed: {e}")
        
        # Test 3: Networking statistics
        try:
            networking_stats = self.gateway.get_networking_stats()
            test_results["networking_stats"] = {
                "success": True,
                "stats": networking_stats
            }
            logger.info(f"Networking stats test: {networking_stats}")
        except Exception as e:
            test_results["networking_stats"] = {"success": False, "error": str(e)}
            logger.error(f"Networking stats test failed: {e}")
        
        # Log test results to W&B
        if wandb.run:
            wandb.log({
                "test_results": test_results,
                "system_health": all(result.get("success", False) for result in test_results.values())
            })
        
        return test_results
    
    def _get_default_sample_data(self) -> Dict[str, str]:
        """Get default sample data for testing."""
        return {
            "alice": "I love Italian food, especially vegetarian options. I enjoy quiet restaurants for business meetings and prefer places under $30.",
            "bob": "I'm a big fan of sushi and Japanese cuisine. I like trendy places with good atmosphere and don't mind spending up to $50.",
            "charlie": "I prefer healthy food, salads, and Mediterranean cuisine. I'm vegetarian and like casual dining experiences.",
            "diana": "I love trying new cuisines, especially Thai and Vietnamese. I prefer authentic places with good reviews.",
            "eve": "I enjoy comfort food, American cuisine, and family-friendly restaurants. Budget-conscious, prefer under $25.",
            "frank": "I'm into fine dining, French cuisine, and wine pairings. I appreciate excellent service and ambiance.",
            "grace": "I love Mexican food, especially authentic tacos and fresh ingredients. I prefer casual, lively atmospheres.",
            "henry": "I'm a foodie who loves experimenting with fusion cuisine. I enjoy innovative restaurants with creative menus.",
            "ivy": "I prefer Asian cuisine, especially Korean and Chinese food. I like spicy food and informal dining settings.",
            "jack": "I'm a meat lover who enjoys BBQ and steakhouses. I prefer hearty meals and don't mind spending for good quality."
        }
    
    async def collaborate_users(self, user_ids: List[str], task: str, location: str = "New York City") -> Dict[str, Any]:
        """
        Facilitate collaboration between users.
        
        Args:
            user_ids: List of user IDs to collaborate
            task: Collaboration task description
            location: Location for the collaboration
            
        Returns:
            Collaboration results
        """
        if not self.is_initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        
        logger.info(f"Facilitating collaboration between {user_ids} for task: {task}")
        
        try:
            # Get user preferences
            user_preferences = []
            for user_id in user_ids:
                user_data = await self.vector_store.get_user_preferences(user_id)
                if user_data:
                    user_preferences.append(user_data)
            
            if not user_preferences:
                return {"error": "No user preferences found for collaboration"}
            
            # Combine preferences for restaurant search
            combined_preferences = " ".join([u.get("preferences", "") for u in user_preferences])
            
            # Search for restaurants
            restaurant_results = await self.exa_client.search_restaurants(
                combined_preferences,
                location=location,
                num_results=8
            )
            
            # Calculate compatibility scores
            compatibility_scores = []
            for result in restaurant_results:
                score = self._calculate_restaurant_compatibility(result.text, user_preferences)
                compatibility_scores.append({
                    "restaurant": result.title,
                    "url": result.url,
                    "description": result.text[:200] + "..." if len(result.text) > 200 else result.text,
                    "relevance_score": result.score,
                    "compatibility_score": score,
                    "combined_score": (result.score + score) / 2
                })
            
            # Sort by combined score
            compatibility_scores.sort(key=lambda x: x["combined_score"], reverse=True)
            
            collaboration_result = {
                "task": task,
                "location": location,
                "users": user_ids,
                "user_preferences": user_preferences,
                "recommended_restaurants": compatibility_scores[:5],
                "collaboration_success": True,
                "total_restaurants_found": len(restaurant_results)
            }
            
            # Log collaboration to W&B
            if wandb.run:
                wandb.log({
                    "collaboration_task": task,
                    "users_count": len(user_ids),
                    "restaurants_found": len(restaurant_results),
                    "collaboration_success": True
                })
            
            return collaboration_result
            
        except Exception as e:
            logger.error(f"Error in user collaboration: {e}")
            
            # Log error to W&B
            if wandb.run:
                wandb.log({
                    "collaboration_error": str(e),
                    "collaboration_success": False
                })
            
            return {"error": str(e), "collaboration_success": False}
    
    def _calculate_restaurant_compatibility(self, restaurant_text: str, user_preferences: List[Dict[str, Any]]) -> float:
        """Calculate how well a restaurant matches group preferences."""
        restaurant_text = restaurant_text.lower()
        total_score = 0.0
        
        for user_data in user_preferences:
            preferences = user_data.get("preferences", "").lower()
            preference_words = preferences.split()
            
            matches = sum(1 for word in preference_words if word in restaurant_text)
            user_score = matches / len(preference_words) if preference_words else 0
            total_score += user_score
        
        return total_score / len(user_preferences) if user_preferences else 0.0
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        status = {
            "initialized": self.is_initialized,
            "components": {
                "gateway": self.gateway is not None,
                "vector_store": self.vector_store is not None,
                "exa_client": self.exa_client is not None
            },
            "networking_stats": {},
            "vector_store_stats": {}
        }
        
        if self.gateway:
            status["networking_stats"] = self.gateway.get_networking_stats()
        
        if self.vector_store:
            status["vector_store_stats"] = await self.vector_store.get_stats()
        
        return status


async def main():
    """Main entry point for the A2A networking system."""
    system = A2ANetworkingSystem()
    
    try:
        # Initialize the system
        await system.initialize()
        
        # Run system tests
        test_results = await system.test_system()
        print("System Test Results:")
        print(json.dumps(test_results, indent=2))
        
        # Test collaboration
        collaboration_result = await system.collaborate_users(
            ["alice", "bob", "charlie"],
            "Find a restaurant for lunch",
            "New York City"
        )
        print("\nCollaboration Test Results:")
        print(json.dumps(collaboration_result, indent=2))
        
        # Get system status
        status = await system.get_system_status()
        print("\nSystem Status:")
        print(json.dumps(status, indent=2))
        
        # Start server (in production, this would run indefinitely)
        print("\nStarting A2A server...")
        print("Server would run indefinitely. In demo mode, stopping after initialization.")
        
        # In production, you would:
        # await system.start_server()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise
    finally:
        await system.stop_server()


async def start_production_server():
    """Start the A2A system in production mode."""
    system = A2ANetworkingSystem()
    
    try:
        # Initialize with custom data if available
        custom_data = None
        if os.path.exists("user_preferences.json"):
            with open("user_preferences.json", "r") as f:
                custom_data = json.load(f)
        
        await system.initialize(custom_data)
        
        # Start server
        host = os.getenv("A2A_HOST", "0.0.0.0")
        port = int(os.getenv("A2A_PORT", "10002"))
        
        logger.info(f"Starting A2A production server on {host}:{port}")
        await system.start_server(host, port)
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Production server error: {e}")
        raise
    finally:
        await system.stop_server()


if __name__ == "__main__":
    # Check if running in production mode
    if os.getenv("A2A_PRODUCTION", "false").lower() == "true":
        asyncio.run(start_production_server())
    else:
        # Run in demo mode
        asyncio.run(main()) 