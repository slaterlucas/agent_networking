"""
show_agent_fields.py
Lists all valid constructor arguments for google.adk.agents.Agent
"""

from pprint import pprint
from google.adk.agents import Agent

def list_agent_fields():
    # every Pydantic-v2 model has a .model_fields dict
    fields = Agent.model_fields
    cleaned = {
        name: {
            "type": str(info.annotation),
            "required": info.is_required(),
            "default": info.default
        }
        for name, info in fields.items()
    }
    pprint(cleaned, sort_dicts=False)

if __name__ == "__main__":
    list_agent_fields()
