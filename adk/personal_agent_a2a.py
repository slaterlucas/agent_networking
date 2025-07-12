"""
Personal Agent A2A Implementation

Personal agents using A2A protocol that integrate with the existing people networking system.
Each user has their own personal agent that understands their preferences and can collaborate.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from google.adk.agent import LlmAgent
from google.adk.llms import GeminiPro
from google_a2a.common.types import AgentCard, AgentSkill
from google_a2a.common.task_manager import BaseTaskManager
from adk.redis_vector_store import RedisVectorStore
from adk.exa_client import ExaSearchClient
from adk.rag_shield import RAGShield, build_restaurant_recommendation_prompt
from networking.networking import PeopleNetworking
import logging

logger = logging.getLogger(__name__)

# Personal Agent Card Definition
personal_card = AgentCard(
    id="personal-agent",
    name="Personal Networking Agent",
    description="Personalized agent that knows user preferences and collaborates with others for optimal decisions",
    skills=[
        AgentSkill(
            id="preference-matching",
            name="Preference Matching",
            description="Matches user preferences with similar people and restaurants",
            tags=["preferences", "matching", "networking"],
            examples=["Find people with similar food preferences", "Match me with users who like Italian food"],
            inputModes=["text"],
            outputModes=["json"],
        ),
        AgentSkill(
            id="restaurant-recommendation",
            name="Restaurant Recommendation",
            description="Recommends restaurants based on user preferences and constraints",
            tags=["restaurant", "recommendation", "food"],
            examples=["Find vegetarian Italian restaurants under $30", "Recommend quiet restaurants for business meetings"],
            inputModes=["text"],
            outputModes=["json"],
        ),
        AgentSkill(
            id="collaboration-planning",
            name="Collaboration Planning",
            description="Plans activities with other users by finding common preferences",
            tags=["collaboration", "planning", "group"],
            examples=["Plan lunch with Bob", "Find restaurant that works for both Alice and Charlie"],
            inputModes=["text"],
            outputModes=["json"],
        ),
        AgentSkill(
            id="preference-analysis",
            name="Preference Analysis",
            description="Analyzes and understands user preferences from text",
            tags=["analysis", "preferences", "understanding"],
            examples=["Analyze my food preferences", "What kind of restaurants do I like?"],
            inputModes=["text"],
            outputModes=["json"],
        )
    ],
)

class PersonalTaskManager(BaseTaskManager):
    """
    Personal agent task manager that handles user-specific requests and collaborations.
    """
    
    def __init__(self, people_network: Optional[PeopleNetworking] = None):
        """
        Initialize personal task manager.
        
        Args:
            people_network: Existing people networking instance
        """
        # Initialize LLM agent
        self.llm_agent = LlmAgent(llm=GeminiPro(temperature=0.1))
        
        # Initialize components
        self.people_network = people_network or PeopleNetworking()
        self.vector_store = RedisVectorStore("personal_prefs")
        self.exa_client = ExaSearchClient()
        self.rag_shield = RAGShield()
        
        # Initialize vector store
        asyncio.create_task(self._initialize_vector_store())
        
    async def _initialize_vector_store(self):
        """Initialize the vector store with current networking data."""
        try:
            await self.vector_store.create_index()
            
            # If we have networking data, populate vector store
            if self.people_network.people_data is not None:
                for _, row in self.people_network.people_data.iterrows():
                    await self.vector_store.add_user_preferences(
                        row['name'], 
                        row['preferences']
                    )
                logger.info(f"Initialized vector store with {len(self.people_network.people_data)} users")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
    
    async def on_task(self, task):
        """
        Handle incoming A2A tasks.
        
        Args:
            task: A2A task object
            
        Returns:
            Task response
        """
        try:
            skill_id = task.skill_id
            user_input = task.input.text
            
            logger.info(f"Processing task: {skill_id} - {user_input}")
            
            if skill_id == "preference-matching":
                return await self._handle_preference_matching(user_input, task)
            elif skill_id == "restaurant-recommendation":
                return await self._handle_restaurant_recommendation(user_input, task)
            elif skill_id == "collaboration-planning":
                return await self._handle_collaboration_planning(user_input, task)
            elif skill_id == "preference-analysis":
                return await self._handle_preference_analysis(user_input, task)
            else:
                return {"error": f"Unknown skill: {skill_id}"}
                
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            return {"error": str(e)}
    
    async def _handle_preference_matching(self, user_input: str, task) -> Dict[str, Any]:
        """Handle preference matching requests."""
        try:
            # Extract user ID from task context if available
            user_id = task.context.get("user_id") if hasattr(task, 'context') else None
            
            if user_id:
                # Find similar users using vector store
                similar_users = await self.vector_store.find_similar_users(user_id, k=5)
                
                # Also use traditional clustering from networking system
                if self.people_network.people_data is not None:
                    traditional_similar = self.people_network.find_similar_people(user_id, k=5)
                    
                    # Combine results
                    combined_results = {
                        "vector_similar": [
                            {"user_id": result.id, "score": result.score, "preferences": result.text}
                            for result in similar_users
                        ],
                        "clustering_similar": [
                            {"user_id": name, "score": score}
                            for name, score in traditional_similar
                        ]
                    }
                else:
                    combined_results = {
                        "vector_similar": [
                            {"user_id": result.id, "score": result.score, "preferences": result.text}
                            for result in similar_users
                        ],
                        "clustering_similar": []
                    }
                
                return {
                    "user_id": user_id,
                    "similar_users": combined_results,
                    "recommendation": "These users have similar preferences and might enjoy similar restaurants"
                }
            else:
                # General preference matching based on query
                search_results = await self.vector_store.knn_search(user_input, k=5)
                
                return {
                    "query": user_input,
                    "matching_users": [
                        {"user_id": result.id, "score": result.score, "preferences": result.text}
                        for result in search_results
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error in preference matching: {e}")
            return {"error": str(e)}
    
    async def _handle_restaurant_recommendation(self, user_input: str, task) -> Dict[str, Any]:
        """Handle restaurant recommendation requests."""
        try:
            # Get user preferences if user ID is provided
            user_id = task.context.get("user_id") if hasattr(task, 'context') else None
            user_preferences = ""
            
            if user_id:
                user_data = await self.vector_store.get_user_preferences(user_id)
                if user_data:
                    user_preferences = user_data.get("preferences", "")
            
            # Search for restaurants using Exa
            location = task.context.get("location", "New York City") if hasattr(task, 'context') else "New York City"
            
            # Combine user preferences with current request
            search_query = f"{user_preferences} {user_input}".strip()
            
            restaurant_results = await self.exa_client.search_restaurants(
                search_query, 
                location=location, 
                num_results=8
            )
            
            # Use RAG shield to generate safe recommendations
            prompt = build_restaurant_recommendation_prompt(
                user_preferences or user_input,
                [
                    {
                        "title": r.title,
                        "url": r.url,
                        "text": r.text,
                        "score": r.score
                    }
                    for r in restaurant_results
                ]
            )
            
            # Get LLM response
            llm_response = await self.llm_agent(prompt)
            
            # Validate response
            validation = self.rag_shield.validate_response(
                llm_response.text, 
                [r.text for r in restaurant_results]
            )
            
            return {
                "user_id": user_id,
                "query": user_input,
                "user_preferences": user_preferences,
                "restaurants": [
                    {
                        "name": r.title,
                        "url": r.url,
                        "description": r.text[:200] + "..." if len(r.text) > 200 else r.text,
                        "score": r.score
                    }
                    for r in restaurant_results
                ],
                "recommendation": llm_response.text,
                "validation": validation
            }
            
        except Exception as e:
            logger.error(f"Error in restaurant recommendation: {e}")
            return {"error": str(e)}
    
    async def _handle_collaboration_planning(self, user_input: str, task) -> Dict[str, Any]:
        """Handle collaboration planning requests."""
        try:
            # Extract user IDs from input or context
            user_ids = []
            if hasattr(task, 'context') and 'user_ids' in task.context:
                user_ids = task.context['user_ids']
            
            # Get preferences for all users
            users_data = []
            for user_id in user_ids:
                user_data = await self.vector_store.get_user_preferences(user_id)
                if user_data:
                    users_data.append(user_data)
            
            if not users_data:
                return {"error": "No user data found for collaboration"}
            
            # Find restaurants that might work for the group
            combined_preferences = " ".join([u.get("preferences", "") for u in users_data])
            location = task.context.get("location", "New York City") if hasattr(task, 'context') else "New York City"
            
            restaurant_results = await self.exa_client.search_restaurants(
                combined_preferences,
                location=location,
                num_results=10
            )
            
            # Use RAG shield for collaboration prompt
            from adk.rag_shield import build_group_collaboration_prompt
            
            prompt = build_group_collaboration_prompt(
                users_data,
                user_input,
                [
                    {
                        "title": r.title,
                        "url": r.url,
                        "text": r.text,
                        "score": r.score
                    }
                    for r in restaurant_results
                ]
            )
            
            # Get LLM response
            llm_response = await self.llm_agent(prompt)
            
            return {
                "collaboration_task": user_input,
                "users": users_data,
                "restaurants": [
                    {
                        "name": r.title,
                        "url": r.url,
                        "description": r.text[:200] + "..." if len(r.text) > 200 else r.text,
                        "score": r.score
                    }
                    for r in restaurant_results
                ],
                "collaboration_plan": llm_response.text,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in collaboration planning: {e}")
            return {"error": str(e)}
    
    async def _handle_preference_analysis(self, user_input: str, task) -> Dict[str, Any]:
        """Handle preference analysis requests."""
        try:
            # Analyze preferences using the networking system
            user_id = task.context.get("user_id") if hasattr(task, 'context') else None
            
            if user_id:
                # Get user's current preferences
                user_data = await self.vector_store.get_user_preferences(user_id)
                if user_data:
                    preferences = user_data.get("preferences", "")
                    
                    # Find similar users for context
                    similar_users = await self.vector_store.find_similar_users(user_id, k=3)
                    
                    # Use clustering analysis
                    cluster_analysis = {}
                    if self.people_network.people_data is not None:
                        try:
                            clusters = self.people_network.cluster_people(n_clusters=3)
                            user_cluster = clusters.get(user_id)
                            if user_cluster is not None:
                                cluster_members = self.people_network.get_cluster_members(user_cluster)
                                cluster_analysis = {
                                    "cluster_id": user_cluster,
                                    "cluster_members": cluster_members,
                                    "total_clusters": len(set(clusters.values()))
                                }
                        except Exception as e:
                            logger.warning(f"Error in clustering analysis: {e}")
                    
                    return {
                        "user_id": user_id,
                        "preferences": preferences,
                        "similar_users": [
                            {"user_id": r.id, "score": r.score}
                            for r in similar_users
                        ],
                        "cluster_analysis": cluster_analysis,
                        "analysis": f"User {user_id} has preferences that align with {len(similar_users)} similar users"
                    }
                else:
                    return {"error": f"No preferences found for user {user_id}"}
            else:
                # General preference analysis
                search_results = await self.vector_store.knn_search(user_input, k=5)
                
                return {
                    "query": user_input,
                    "matching_preferences": [
                        {"user_id": r.id, "score": r.score, "preferences": r.text}
                        for r in search_results
                    ],
                    "analysis": f"Found {len(search_results)} users with similar preferences"
                }
                
        except Exception as e:
            logger.error(f"Error in preference analysis: {e}")
            return {"error": str(e)}
    
    async def add_user_preferences(self, user_id: str, preferences: str):
        """Add or update user preferences."""
        try:
            # Add to vector store
            await self.vector_store.add_user_preferences(user_id, preferences)
            
            # Update networking system
            current_prefs = {}
            if self.people_network.people_data is not None:
                current_prefs = dict(zip(
                    self.people_network.people_data['name'],
                    self.people_network.people_data['preferences']
                ))
            
            current_prefs[user_id] = preferences
            self.people_network.add_people(current_prefs)
            
            logger.info(f"Added preferences for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error adding user preferences: {e}")
            raise


if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize task manager
        task_manager = PersonalTaskManager()
        
        # Add some sample users
        sample_users = {
            "alice": "I love Italian food, especially vegetarian options. I enjoy quiet restaurants for business meetings.",
            "bob": "I'm a big fan of sushi and Japanese cuisine. I like trendy places with good atmosphere.",
            "charlie": "I prefer healthy food, salads, and Mediterranean cuisine. I'm vegetarian and like casual dining."
        }
        
        for user_id, preferences in sample_users.items():
            await task_manager.add_user_preferences(user_id, preferences)
        
        print("Personal Agent A2A Task Manager initialized with sample users")
        
        # Example task simulation
        class MockTask:
            def __init__(self, skill_id, input_text, context=None):
                self.skill_id = skill_id
                self.input = type('obj', (object,), {'text': input_text})
                self.context = context or {}
        
        # Test preference matching
        task = MockTask("preference-matching", "vegetarian restaurants", {"user_id": "alice"})
        result = await task_manager.on_task(task)
        print(f"Preference matching result: {json.dumps(result, indent=2)}")
    
    asyncio.run(main()) 