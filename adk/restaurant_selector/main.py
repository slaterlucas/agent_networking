import os
import json
import asyncio
from typing import Dict, List, Any
from exa_py import Exa


class RestaurantSelectorAgent:
    """
    ADK Restaurant Selector Agent integrated with Exa
    Searches and selects restaurants based on user criteria
    """
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the restaurant selector agent with configuration"""
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
        """Default configuration for restaurant selector"""
        return {
            "search_params": {
                "num_results": 10,
                "use_autoprompt": True
            },
            "cuisine_types": ["italian", "japanese", "mexican", "chinese", "american", "thai", "indian", "french"],
            "price_range": {"min": 1, "max": 4},  # 1-4 $ rating
            "rating_threshold": 4.0,
            "distance_radius": 25,  # miles
            "dietary_restrictions": ["vegetarian", "vegan", "gluten-free", "halal", "kosher"]
        }
    
    async def search_restaurants(self, query: str, location: str = None, cuisine: str = None) -> List[Dict[str, Any]]:
        """Search for restaurants using Exa API"""
        try:
            # Construct search query
            search_query = f"{query} restaurants"
            if location:
                search_query += f" in {location}"
            if cuisine:
                search_query += f" {cuisine} cuisine"
            
            # Search using Exa
            result = self.exa.search(
                query=search_query,
                num_results=self.config["search_params"]["num_results"],
                use_autoprompt=self.config["search_params"]["use_autoprompt"],
                include_domains=["yelp.com", "google.com", "opentable.com", "zomato.com", "tripadvisor.com"]
            )
            
            # Process and format results
            restaurants = []
            for item in result.results:
                restaurant = {
                    "name": item.title,
                    "url": item.url,
                    "description": item.text,
                    "published_date": item.published_date,
                    "score": item.score
                }
                restaurants.append(restaurant)
            
            return restaurants
            
        except Exception as e:
            print(f"Error searching restaurants: {e}")
            return []
    
    async def filter_restaurants(self, restaurants: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter restaurants based on user criteria"""
        filtered_restaurants = []
        
        for restaurant in restaurants:
            if self._matches_criteria(restaurant, criteria):
                filtered_restaurants.append(restaurant)
        
        return filtered_restaurants
    
    def _matches_criteria(self, restaurant: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if restaurant matches given criteria"""
        # Basic implementation - can be extended with more sophisticated matching
        description = restaurant.get("description", "").lower()
        
        # Check cuisine type
        if "cuisine" in criteria:
            cuisine = criteria["cuisine"].lower()
            if cuisine not in description:
                return False
        
        # Check dietary restrictions
        if "dietary_restrictions" in criteria:
            restrictions = criteria["dietary_restrictions"]
            for restriction in restrictions:
                if restriction.lower() in description:
                    return True
        
        # Check price range (basic text analysis)
        if "price_range" in criteria:
            price_indicators = ["$", "$$", "$$$", "$$$$", "expensive", "cheap", "affordable"]
            # This is a simplified implementation
            return True
        
        return True
    
    async def select_best_restaurants(self, restaurants: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """Select the best restaurants from the list"""
        # Sort by score (relevance) and return top restaurants
        sorted_restaurants = sorted(restaurants, key=lambda x: x.get("score", 0), reverse=True)
        return sorted_restaurants[:limit]
    
    async def get_restaurant_details(self, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get additional details for selected restaurants"""
        detailed_restaurants = []
        
        for restaurant in restaurants:
            try:
                # Use Exa to get more content about the restaurant
                content_result = self.exa.get_contents([restaurant["url"]])
                
                if content_result.results:
                    restaurant_detail = restaurant.copy()
                    restaurant_detail["full_content"] = content_result.results[0].text
                    detailed_restaurants.append(restaurant_detail)
                else:
                    detailed_restaurants.append(restaurant)
                    
            except Exception as e:
                print(f"Error getting details for {restaurant['name']}: {e}")
                detailed_restaurants.append(restaurant)
        
        return detailed_restaurants
    
    async def run(self, user_query: str, location: str = None, cuisine: str = None, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Main execution method for the restaurant selector agent"""
        print(f"🍽️  Restaurant Selector Agent starting...")
        print(f"Query: {user_query}")
        
        # Search for restaurants
        restaurants = await self.search_restaurants(user_query, location, cuisine)
        print(f"Found {len(restaurants)} restaurants")
        
        # Filter restaurants if criteria provided
        if criteria:
            restaurants = await self.filter_restaurants(restaurants, criteria)
            print(f"Filtered to {len(restaurants)} restaurants")
        
        # Select best restaurants
        best_restaurants = await self.select_best_restaurants(restaurants)
        print(f"Selected {len(best_restaurants)} best restaurants")
        
        # Get detailed information
        detailed_restaurants = await self.get_restaurant_details(best_restaurants)
        print(f"Retrieved details for {len(detailed_restaurants)} restaurants")
        
        return detailed_restaurants


async def main():
    """Example usage of the Restaurant Selector Agent"""
    agent = RestaurantSelectorAgent()
    
    # Example query
    user_query = "highly rated Italian restaurants"
    location = "New York City"
    cuisine = "Italian"
    criteria = {
        "dietary_restrictions": ["vegetarian"],
        "price_range": {"min": 2, "max": 4}
    }
    
    results = await agent.run(user_query, location, cuisine, criteria)
    
    print("\n🎯 Selected Restaurants:")
    for i, restaurant in enumerate(results, 1):
        print(f"{i}. {restaurant['name']}")
        print(f"   URL: {restaurant['url']}")
        print(f"   Score: {restaurant['score']}")
        print(f"   Description: {restaurant['description'][:100]}...")
        print()


if __name__ == "__main__":
    asyncio.run(main()) 