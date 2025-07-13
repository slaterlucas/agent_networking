"""
A2A Gateway for Agent Networking System (A2A SDK v0.2+)

This module provides the FastAPI app and AgentExecutor for agent-to-agent communication,
integrating with the existing people networking clustering system.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
import uvicorn

# Import networking system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from networking.networking import PeopleNetworking

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Define your agent's skills ---
skill = AgentSkill(
    id='networking',
    name='People Networking',
    description='Find similar people, cluster people, and get cluster members.',
    tags=['networking', 'clustering', 'similarity'],
    examples=['Find people similar to Alice', 'Cluster people into 3 groups'],
)

# --- Define the agent card ---
agent_card = AgentCard(
    name='Networking Agent',
    description='Agent for people clustering and networking tasks.',
    url='http://localhost:10002/',
    version='1.0.0',
    defaultInputModes=['text'],
    defaultOutputModes=['text'],
    capabilities=AgentCapabilities(streaming=True),
    skills=[skill],
)

# --- Implement the AgentExecutor with enhanced logging ---
class NetworkingAgentExecutor(AgentExecutor):
    def __init__(self):
        super().__init__()
        self.networking = PeopleNetworking()
        self._initialize_networking_data()
        
    def _initialize_networking_data(self):
        """Initialize networking with sample people data."""
        sample_people = {
            "Alice": "I love technology, programming, and outdoor activities.",
            "Bob": "I'm passionate about cooking, trying new recipes, and exploring different cuisines.",
            "Charlie": "I'm into fitness, yoga, and healthy living.",
            "Diana": "I love music, playing guitar, and going to concerts.",
            "Eve": "I'm a sports enthusiast, especially football and basketball.",
            "Frank": "I enjoy reading mystery novels and crime thrillers.",
            "Grace": "I'm passionate about cooking and experimenting with new flavors.",
            "Henry": "I love outdoor adventures like hiking, camping, and rock climbing.",
            "Iris": "I'm interested in technology, artificial intelligence, and machine learning.",
            "Jack": "I enjoy reading books, especially science fiction and fantasy novels."
        }
        self.networking.add_people(sample_people)
        self.networking.cluster_people(n_clusters=4, method='kmeans')
        logger.info("[A2A_GATEWAY] Networking data initialized with 10 sample people")
    
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """Execute networking tasks with enhanced A2A logging."""
        try:
            # Enhanced A2A message logging
            message = context.message
            message_id = getattr(message, 'messageId', 'unknown')
            sender_role = getattr(message, 'role', 'unknown')
            
            # Log incoming A2A message
            logger.info(f"[A2A_IN] Networking agent received message from {sender_role} (ID: {message_id})")
            
            if not message or not message.parts:
                response = "Hello! I'm the Networking Agent. I can help with people clustering and networking tasks."
                await event_queue.enqueue_event({
                    "type": "text",
                    "text": response
                })
                logger.info(f"[A2A_OUT] Networking agent sent greeting response")
                return
            
            # Extract text from message parts
            text = ""
            for part in message.parts:
                if hasattr(part, 'kind') and part.kind == 'text':
                    if hasattr(part, 'text') and part.text:
                        text = part.text
                        break
                    elif hasattr(part, 'root') and hasattr(part.root, 'text') and part.root.text:
                        text = part.root.text
                        break
            
            if not text:
                response = "Hello! I'm the Networking Agent. I can help with people clustering and networking tasks."
                await event_queue.enqueue_event({
                    "type": "text",
                    "text": response
                })
                logger.info(f"[A2A_OUT] Networking agent sent greeting response (no text found)")
                return
            
            logger.info(f"[A2A_PROCESS] Networking agent processing: '{text[:100]}...'")
            
            # Process networking tasks
            response = await self._process_networking_task(text)
            
            # Send response
            await event_queue.enqueue_event({
                "type": "text",
                "text": response
            })
            
            logger.info(f"[A2A_OUT] Networking agent sent response (length: {len(response)})")
            
        except Exception as e:
            logger.error(f"[A2A_ERROR] Error in networking agent: {e}")
            await event_queue.enqueue_event({
                "type": "text",
                "text": f"Sorry, I encountered an error: {str(e)}"
            })
    
    async def _process_networking_task(self, text: str) -> str:
        """Process networking tasks with detailed logging."""
        try:
            logger.info(f"[NETWORKING_START] Processing networking task: '{text[:50]}...'")
            
            if "similar" in text.lower():
                # Find similar people
                target_person = None
                for person in ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Iris", "Jack"]:
                    if person.lower() in text.lower():
                        target_person = person
                        break
                
                if target_person:
                    logger.info(f"[NETWORKING_SIMILAR] Finding people similar to {target_person}")
                    similar_people = self.networking.find_similar_people(target_person, k=3)
                    response = f"People similar to {target_person}:\n"
                    for name, score in similar_people:
                        response += f"- {name} (similarity: {score:.3f})\n"
                else:
                    response = "Please specify a person to find similar people for (e.g., 'Find people similar to Alice')."
            
            elif "cluster" in text.lower():
                # Cluster people
                logger.info(f"[NETWORKING_CLUSTER] Performing clustering analysis")
                clusters = self.networking.cluster_people(n_clusters=4, method='kmeans')
                response = "People clustering results:\n"
                for person, cluster in clusters.items():
                    response += f"- {person}: Cluster {cluster}\n"
            
            elif "members" in text.lower() and "cluster" in text.lower():
                # Get cluster members
                cluster_id = None
                for i in range(4):
                    if str(i) in text:
                        cluster_id = i
                        break
                
                if cluster_id is not None:
                    logger.info(f"[NETWORKING_MEMBERS] Getting members of cluster {cluster_id}")
                    members = self.networking.get_cluster_members(cluster_id)
                    response = f"Members of cluster {cluster_id}: {', '.join(members)}"
                else:
                    response = "Please specify a cluster ID (e.g., 'Show members of cluster 0')."
            
            elif "top pairs" in text.lower():
                # Find top similar pairs
                logger.info(f"[NETWORKING_PAIRS] Finding top similar pairs")
                pairs = self.networking.find_top_similar_pairs(k=5)
                response = "Top similar people pairs:\n"
                for (person1, person2), score in pairs:
                    response += f"- {person1} & {person2}: {score:.3f}\n"
            
            else:
                response = "I can help with:\n- Finding similar people (e.g., 'Find people similar to Alice')\n- Clustering people (e.g., 'Cluster people')\n- Getting cluster members (e.g., 'Show members of cluster 0')\n- Finding top similar pairs (e.g., 'Show top pairs')"
            
            logger.info(f"[NETWORKING_END] Completed networking task")
            return response
            
        except Exception as e:
            logger.error(f"[NETWORKING_ERROR] Error in networking processing: {e}")
            return f"Sorry, I encountered an error while processing the networking task: {str(e)}"
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Handle task cancellation with logging."""
        logger.info(f"[A2A_CANCEL] Networking agent task cancelled")
        await event_queue.enqueue_event({
            "type": "text",
            "text": "Networking task cancelled."
        })

# --- Set up the request handler and server ---
request_handler = DefaultRequestHandler(
    agent_executor=NetworkingAgentExecutor(),
    task_store=InMemoryTaskStore(),
)

server = A2AStarletteApplication(
    agent_card=agent_card, http_handler=request_handler
)

app = server.build()

if __name__ == "__main__":
    logger.info("[A2A_GATEWAY] Starting A2A Gateway on port 10002")
    uvicorn.run(app, host="0.0.0.0", port=10002) 