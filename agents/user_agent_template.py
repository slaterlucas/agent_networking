#!/usr/bin/env python3
"""
Individual User A2A Agent Template

This template creates a real A2A agent for each user with their specific preferences.
Each agent uses Exa API for search and wandb for tracking.
"""

import os
import asyncio
import logging
from typing import Dict, Any, List
from dataclasses import dataclass
import json
import httpx
from dotenv import load_dotenv
import traceback

# A2A SDK imports
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, Task, TaskStatus, Artifact, Message, Part
import uuid
from datetime import datetime
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

# Import our networking system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from networking.networking import PeopleNetworking
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    """User profile with preferences and networking data."""
    name: str
    preferences: str
    location: str
    budget: str
    dietary_restrictions: List[str]
    cuisine_preferences: List[str]
    interests: List[str]
    agent_port: int

# Pydantic models for API
class NetworkingRequest(BaseModel):
    target_person: str
    k: int = 5

class ClusteringRequest(BaseModel):
    n_clusters: int = 3
    method: str = "kmeans"

class PeoplePreferencesRequest(BaseModel):
    people_preferences: Dict[str, str]

class ExecuteRequest(BaseModel):
    message: Dict[str, Any]
    contextId: str = None

class ExaSearchClient:
    """Client for Exa API search functionality."""
    
    def __init__(self):
        self.api_key = os.getenv('EXA_API_KEY')
        self.base_url = "https://api.exa.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search using Exa API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json={
                        "query": query,
                        "numResults": num_results,
                        "includeDomains": [],
                        "excludeDomains": [],
                        "useAutoprompt": True
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get('results', [])
        except Exception as e:
            logger.error(f"Exa search error: {e}")
            return []

class UserAgentExecutor(AgentExecutor):
    """A2A Agent Executor for individual users."""
    
    def __init__(self, user_profile: UserProfile):
        super().__init__()
        self.user_profile = user_profile
        self.exa_client = ExaSearchClient()
        self.networking = PeopleNetworking()
        
        # Initialize with sample people data for networking
        self._initialize_networking_data()
        
        # Initialize wandb for this user
        import wandb
        wandb.init(
            project="agent-networking",
            name=f"user-agent-{user_profile.name}",
            config={
                "user_name": user_profile.name,
                "location": user_profile.location,
                "interests": user_profile.interests
            }
        )
        self.wandb = wandb
    
    def _initialize_networking_data(self):
        """Initialize networking with sample people data."""
        sample_people = {
            "Alice": f"I love technology, programming, and outdoor activities. I enjoy {', '.join(self.user_profile.interests)}.",
            "Bob": "I'm passionate about cooking, trying new recipes, and exploring different cuisines. I love traveling and photography.",
            "Charlie": "I'm into fitness, yoga, and healthy living. I enjoy nature walks and meditation.",
            "Diana": "I love music, playing guitar, and going to concerts. I'm also interested in art and painting.",
            "Eve": "I'm a sports enthusiast, especially football and basketball. I enjoy watching games and playing fantasy sports.",
            "Frank": "I enjoy reading mystery novels and crime thrillers. I like solving puzzles and playing chess.",
            "Grace": "I'm passionate about cooking and experimenting with new flavors. I enjoy food photography and blogging.",
            "Henry": "I love outdoor adventures like hiking, camping, and rock climbing. I enjoy nature photography.",
            "Iris": "I'm interested in technology, artificial intelligence, and machine learning. I enjoy coding and building projects.",
            "Jack": "I enjoy reading books, especially science fiction and fantasy novels. I enjoy hiking and outdoor activities."
        }
        
        # Add current user to the network
        sample_people[self.user_profile.name] = self.user_profile.preferences
        
        self.networking.add_people(sample_people)
        self.networking.cluster_people(n_clusters=4, method='kmeans')
    
    async def execute(self, context: RequestContext, event_queue: EventQueue, **kwargs) -> None:
        """Execute tasks for this user agent using proper A2A SDK pattern."""
        try:
            # Extract message from context
            message = context.message
            if not message or not message.parts:
                response = f"Hello! I'm {self.user_profile.name}'s agent. How can I help you today?"
                task = self._build_task_response(response, context)
                await event_queue.enqueue_event(task)
                return
            
            # Get the text content from the first part (A2A SDK uses 'kind' and 'text')
            text = ""
            for part in message.parts:
                # Official SDK: part.kind == 'text', part.text is the content
                # Some SDKs may use part.root.text
                if hasattr(part, 'kind') and part.kind == 'text':
                    if hasattr(part, 'text') and part.text:
                        text = part.text
                        break
                    elif hasattr(part, 'root') and hasattr(part.root, 'text') and part.root.text:
                        text = part.root.text
                        break
            
            if not text:
                response = f"Hello! I'm {self.user_profile.name}'s agent. How can I help you today?"
                task = self._build_task_response(response, context)
                await event_queue.enqueue_event(task)
                return

            # Log the request
            log_data = {
                "request_type": "a2a_message",
                "messageId": getattr(message, 'messageId', None),
                "role": getattr(message, 'role', None),
                "text": text
            }
            self.wandb.log(log_data)
            
            # Process the message based on content
            if "search" in text.lower():
                query = text.replace("search", "").strip()
                if query:
                    results = await self.exa_client.search(query)
                    response = f"Search results for '{query}':\n{json.dumps(results[:2], indent=2)}"
                else:
                    response = "Please provide a search query."
            elif "networking" in text.lower() or "similar" in text.lower():
                # Use networking to find similar people
                try:
                    similar_people = self.networking.find_similar_people(self.user_profile.name, k=3)
                    response = f"People similar to {self.user_profile.name}:\n"
                    for name, score in similar_people:
                        response += f"- {name} (similarity: {score:.3f})\n"
                except Exception as e:
                    response = f"Networking feature for {self.user_profile.name}: I can help you find similar people based on your interests in {', '.join(self.user_profile.interests)}."
            elif "cluster" in text.lower():
                # Show cluster information
                try:
                    clusters = self.networking.cluster_people(n_clusters=4, method='kmeans')
                    user_cluster = clusters.get(self.user_profile.name, "Unknown")
                    cluster_members = self.networking.get_cluster_members(user_cluster)
                    response = f"{self.user_profile.name} is in cluster {user_cluster} with: {', '.join(cluster_members)}"
                except Exception as e:
                    response = f"Clustering analysis for {self.user_profile.name} based on interests: {', '.join(self.user_profile.interests)}"
            elif "recommendation" in text.lower():
                if "restaurant" in text.lower():
                    query = f"restaurants in {self.user_profile.location} for {', '.join(self.user_profile.cuisine_preferences)}"
                    results = await self.exa_client.search(query)
                    response = f"Restaurant recommendations for {self.user_profile.name}:\n{json.dumps(results[:2], indent=2)}"
                else:
                    query = f"activities and events in {self.user_profile.location} for {', '.join(self.user_profile.interests)}"
                    results = await self.exa_client.search(query)
                    response = f"Activity recommendations for {self.user_profile.name}:\n{json.dumps(results[:2], indent=2)}"
            else:
                response = f"Hello! I'm {self.user_profile.name}'s agent. I can help with:\n- Search queries\n- Networking opportunities (find similar people)\n- Clustering analysis\n- Personalized recommendations\n\nWhat would you like to do?"
            
            # Send response as a proper Task object
            task = self._build_task_response(response, context)
            await event_queue.enqueue_event(task)
            
        except Exception as e:
            logger.error(f"Error in user agent {self.user_profile.name}: {e}")
            self.wandb.log({"error": str(e)})
            with open("agents/agent_error.log", "a") as f:
                f.write(f"\n--- Exception for {self.user_profile.name} ---\n")
                f.write(traceback.format_exc())
            
            error_response = f"Sorry, I encountered an error: {str(e)}"
            task = self._build_task_response(error_response, context)
            await event_queue.enqueue_event(task)
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue, **kwargs) -> None:
        """Handle task cancellation (required by A2A SDK)."""
        self.wandb.log({"cancelled": True, "context": str(context)})
        await event_queue.enqueue_event(new_agent_text_message("Task cancelled."))

    def _build_task_response(self, text: str, context: RequestContext) -> Task:
        # Build a Task object following the A2A SDK structure
        task_id = getattr(context.message, 'taskId', None) or str(uuid.uuid4())
        context_id = getattr(context.message, 'contextId', None) or str(uuid.uuid4())
        # Build the artifact (text response)
        artifact = Artifact(
            artifactId=str(uuid.uuid4()),
            type="text",
            parts=[Part(kind="text", text=text)]
        )
        # Build the status
        status = TaskStatus(
            state="completed",
            message=Message(
                messageId=str(uuid.uuid4()),
                role="agent",
                parts=[Part(kind="text", text=text)]
            ),
            timestamp=datetime.now().isoformat()
        )
        # Build the Task
        task = Task(
            id=task_id,
            contextId=context_id,
            kind="task",
            status=status,
            artifacts=[artifact],
            history=None,
            metadata=None
        )
        return task

def create_user_agent(user_profile: UserProfile):
    """Create an A2A agent for a specific user."""
    
    # Define agent skills
    skills = [
        AgentSkill(
            id='search',
            name='Intelligent Search',
            description=f'Search for information relevant to {user_profile.name}\'s interests',
            tags=['search', 'information']
        ),
        AgentSkill(
            id='networking',
            name='People Networking',
            description=f'Find similar people and create networking opportunities for {user_profile.name}',
            tags=['networking', 'people']
        ),
        AgentSkill(
            id='clustering',
            name='People Clustering',
            description=f'Analyze people clusters and group similar individuals for {user_profile.name}',
            tags=['clustering', 'analysis']
        ),
        AgentSkill(
            id='recommendation',
            name='Personalized Recommendations',
            description=f'Provide personalized recommendations for {user_profile.name}',
            tags=['recommendations', 'personalization']
        )
    ]
    
    # Create agent card with proper structure
    agent_card = AgentCard(
        name=f"{user_profile.name}'s Agent",
        description=f"Personal A2A agent for {user_profile.name} with interests in {', '.join(user_profile.interests)}",
        url=f"http://localhost:{user_profile.agent_port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=True).__dict__,
        skills=skills
    )
    
    # Create agent executor
    executor = UserAgentExecutor(user_profile)
    task_store = InMemoryTaskStore()
    request_handler = DefaultRequestHandler(agent_executor=executor, task_store=task_store)

    # Create A2A application
    a2a_app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )
    
    # Build the Starlette ASGI app
    a2a_starlette_app = a2a_app.build()
    # Create a FastAPI app
    fastapi_app = FastAPI()

    # Register the custom /a2a/execute endpoint on the main app (before mounting)
    @fastapi_app.post("/a2a/execute")
    async def execute_task(request: ExecuteRequest):
        """Custom execution endpoint that directly calls the agent executor."""
        try:
            # Extract message from request
            message_data = request.message
            message_id = message_data.get('messageId', str(uuid.uuid4()))
            role = message_data.get('role', 'user')
            parts = message_data.get('parts', [])
            # Extract text from parts
            text = ""
            for part in parts:
                if part.get('kind') == 'text' and part.get('text'):
                    text = part['text']
                    break
            if not text:
                return {
                    "status": {
                        "state": "completed",
                        "message": {
                            "messageId": str(uuid.uuid4()),
                            "role": "agent",
                            "parts": [{"kind": "text", "text": f"Hello! I'm {user_profile.name}'s agent. How can I help you?"}]
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                }
            # Process the message using the executor logic
            if "search" in text.lower():
                query = text.replace("search", "").strip()
                if query:
                    results = await executor.exa_client.search(query)
                    response = f"Search results for '{query}':\n{json.dumps(results[:2], indent=2)}"
                else:
                    response = "Please provide a search query."
            elif "networking" in text.lower() or "similar" in text.lower():
                try:
                    similar_people = executor.networking.find_similar_people(user_profile.name, k=3)
                    response = f"People similar to {user_profile.name}:\n"
                    for name, score in similar_people:
                        response += f"- {name} (similarity: {score:.3f})\n"
                except Exception as e:
                    response = f"Networking feature for {user_profile.name}: I can help you find similar people based on your interests in {', '.join(user_profile.interests)}."
            elif "cluster" in text.lower():
                try:
                    clusters = executor.networking.cluster_people(n_clusters=4, method='kmeans')
                    user_cluster = clusters.get(user_profile.name, "Unknown")
                    cluster_members = executor.networking.get_cluster_members(user_cluster)
                    response = f"{user_profile.name} is in cluster {user_cluster} with: {', '.join(cluster_members)}"
                except Exception as e:
                    response = f"Clustering analysis for {user_profile.name} based on interests: {', '.join(user_profile.interests)}"
            elif "recommendation" in text.lower():
                if "restaurant" in text.lower():
                    query = f"restaurants in {user_profile.location} for {', '.join(user_profile.cuisine_preferences)}"
                    results = await executor.exa_client.search(query)
                    response = f"Restaurant recommendations for {user_profile.name}:\n{json.dumps(results[:2], indent=2)}"
                else:
                    query = f"activities and events in {user_profile.location} for {', '.join(user_profile.interests)}"
                    results = await executor.exa_client.search(query)
                    response = f"Activity recommendations for {user_profile.name}:\n{json.dumps(results[:2], indent=2)}"
            else:
                response = f"Hello! I'm {user_profile.name}'s agent. I can help with:\n- Search queries\n- Networking opportunities (find similar people)\n- Clustering analysis\n- Personalized recommendations\n\nWhat would you like to do?"
            # Return A2A-compatible response
            return {
                "status": {
                    "state": "completed",
                    "message": {
                        "messageId": str(uuid.uuid4()),
                        "role": "agent",
                        "parts": [{"kind": "text", "text": response}]
                    },
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error in custom execute endpoint: {e}")
            return {
                "status": {
                    "state": "failed",
                    "message": {
                        "messageId": str(uuid.uuid4()),
                        "role": "agent",
                        "parts": [{"kind": "text", "text": f"Sorry, I encountered an error: {str(e)}"}]
                    },
                    "timestamp": datetime.now().isoformat()
                }
            }

    # Now mount the A2A app at /a2a (after registering custom endpoint)
    fastapi_app.mount("/a2a", a2a_starlette_app)
    
    # Add networking REST endpoints
    @fastapi_app.get("/")
    async def root():
        return {"status": "ok", "agent": agent_card.name}
    
    @fastapi_app.post("/networking/similar")
    async def find_similar_people(request: NetworkingRequest):
        """Find similar people to a target person."""
        try:
            similar_people = executor.networking.find_similar_people(request.target_person, request.k)
            return {
                "target_person": request.target_person,
                "similar_people": [{"name": name, "similarity": float(score)} for name, score in similar_people]
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @fastapi_app.post("/networking/cluster")
    async def cluster_people(request: ClusteringRequest):
        """Cluster people based on their preferences."""
        try:
            clusters = executor.networking.cluster_people(request.n_clusters, request.method)
            cluster_members = {}
            for cluster_id in range(request.n_clusters):
                cluster_members[cluster_id] = executor.networking.get_cluster_members(cluster_id)
            return {
                "clusters": clusters,
                "cluster_members": cluster_members
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @fastapi_app.get("/networking/clusters/{cluster_id}")
    async def get_cluster_members(cluster_id: int):
        """Get members of a specific cluster."""
        try:
            members = executor.networking.get_cluster_members(cluster_id)
            return {"cluster_id": cluster_id, "members": members}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @fastapi_app.post("/networking/top-pairs")
    async def find_top_similar_pairs(k: int = 10):
        """Find top k most similar pairs of people."""
        try:
            similar_pairs = executor.networking.find_top_k_similar_pairs(k)
            return {
                "similar_pairs": [
                    {"person1": p1, "person2": p2, "similarity": float(score)} 
                    for p1, p2, score in similar_pairs
                ]
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @fastapi_app.get("/networking/features")
    async def get_feature_importance(n_features: int = 10):
        """Get the most important features for clustering."""
        try:
            features = executor.networking.get_feature_importance(n_features)
            return {
                "features": [{"feature": feature, "importance": float(importance)} for feature, importance in features]
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @fastapi_app.post("/networking/update-preferences")
    async def update_people_preferences(request: PeoplePreferencesRequest):
        """Update the people preferences in the networking system."""
        try:
            executor.networking.add_people(request.people_preferences)
            return {"message": "Preferences updated successfully", "count": len(request.people_preferences)}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    return fastapi_app

if __name__ == "__main__":
    # Example usage
    user_profile = UserProfile(
        name="Alice",
        preferences="I love technology, programming, and outdoor activities",
        location="San Francisco",
        budget="medium",
        dietary_restrictions=["vegetarian"],
        cuisine_preferences=["Italian", "Asian"],
        interests=["technology", "programming", "hiking"],
        agent_port=10003
    )
    
    app = create_user_agent(user_profile)
    print(f"Created agent for {user_profile.name}") 