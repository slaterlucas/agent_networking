"""
A2A Gateway for Agent Networking System (A2A SDK v0.2+)

This module provides the FastAPI app and AgentExecutor for agent-to-agent communication,
integrating with the existing people networking clustering system.
"""

import logging
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
import uvicorn

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

# --- Implement the AgentExecutor ---
class NetworkingAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # TODO: Implement real networking logic here
        await event_queue.enqueue_event({
            "type": "text",
            "text": f"Received task: {context.task.task_type} (implement logic here)"
        })
    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        await event_queue.enqueue_event({
            "type": "text",
            "text": "Task cancelled."
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
    uvicorn.run(app, host="0.0.0.0", port=10002) 