"""
ADK Agents with Exa Integration

This package contains Autonomous Developer Kit (ADK) agents integrated with the Exa API
for intelligent search and selection tasks.

Available agents:
- EventSelectorAgent: Searches and selects events based on user criteria
- RestaurantSelectorAgent: Searches and selects restaurants based on user preferences
"""

__version__ = "1.0.0"
__author__ = "ADK Team"
__description__ = "ADK agents integrated with Exa API for intelligent search and selection"

# Import main agent classes for easy access
try:
    from .event_selector.main import EventSelectorAgent
    from .restaurant_selector.main import RestaurantSelectorAgent
except ImportError:
    # Handle case where submodules aren't available
    pass

__all__ = [
    "EventSelectorAgent",
    "RestaurantSelectorAgent",
] 