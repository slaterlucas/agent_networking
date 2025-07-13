import os
import json
import asyncio
from typing import Dict, List, Any
from exa_py import Exa
from datetime import datetime, timedelta


class EventSelectorAgent:
    """
    ADK Event Selector Agent integrated with Exa
    Searches and selects events based on user criteria
    """
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the event selector agent with configuration"""
        self.config = self._load_config(config_path)
        self.exa = Exa(api_key=os.getenv("EXA_API_KEY"))
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_path} not found, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for event selector"""
        return {
            "search_params": {
                "num_results": 10,
                "start_published_date": datetime.now().isoformat(),
                "end_published_date": (datetime.now() + timedelta(days=30)).isoformat()
            },
            "event_types": ["concert", "festival", "conference", "workshop", "meetup"],
            "location_radius": 50,
            "price_range": {"min": 0, "max": 500}
        }
    
    async def search_events(self, query: str, location: str = None, event_type: str = None) -> List[Dict[str, Any]]:
        """Search for events using Exa API"""
        try:
            # Construct search query
            search_query = f"{query} events"
            if location:
                search_query += f" in {location}"
            if event_type:
                search_query += f" {event_type}"
            
            # Search using Exa
            result = self.exa.search(
                query=search_query,
                num_results=self.config["search_params"]["num_results"],
                start_published_date=self.config["search_params"]["start_published_date"],
                end_published_date=self.config["search_params"]["end_published_date"],
                include_domains=["eventbrite.com", "meetup.com", "facebook.com", "ticketmaster.com"]
            )
            
            # Process and format results
            events = []
            for item in result.results:
                event = {
                    "title": item.title,
                    "url": item.url,
                    "snippet": item.text,
                    "published_date": item.published_date,
                    "score": item.score
                }
                events.append(event)
            
            return events
            
        except Exception as e:
            print(f"Error searching events: {e}")
            return []
    
    async def filter_events(self, events: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter events based on user criteria"""
        filtered_events = []
        
        for event in events:
            # Add filtering logic based on criteria
            if self._matches_criteria(event, criteria):
                filtered_events.append(event)
        
        return filtered_events
    
    def _matches_criteria(self, event: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if event matches given criteria"""
        # Implement filtering logic based on criteria
        # This is a basic implementation - can be extended
        return True
    
    async def select_best_events(self, events: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """Select the best events from the list"""
        # Sort by score (relevance) and return top events
        sorted_events = sorted(events, key=lambda x: x.get("score", 0), reverse=True)
        return sorted_events[:limit]
    
    async def run(self, user_query: str, location: str = None, event_type: str = None, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Main execution method for the event selector agent"""
        print(f"🎪 Event Selector Agent starting...")
        print(f"Query: {user_query}")
        
        # Search for events
        events = await self.search_events(user_query, location, event_type)
        print(f"Found {len(events)} events")
        
        # Filter events if criteria provided
        if criteria:
            events = await self.filter_events(events, criteria)
            print(f"Filtered to {len(events)} events")
        
        # Select best events
        best_events = await self.select_best_events(events)
        print(f"Selected {len(best_events)} best events")
        
        return best_events


async def main():
    """Example usage of the Event Selector Agent"""
    agent = EventSelectorAgent()
    
    # Example query
    user_query = "tech conferences and workshops"
    location = "San Francisco"
    event_type = "conference"
    
    results = await agent.run(user_query, location, event_type)
    
    print("\n🎯 Selected Events:")
    for i, event in enumerate(results, 1):
        print(f"{i}. {event['title']}")
        print(f"   URL: {event['url']}")
        print(f"   Score: {event['score']}")
        print()


if __name__ == "__main__":
    asyncio.run(main()) 