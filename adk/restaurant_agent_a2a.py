# """
# Restaurant Agent A2A Implementation

# Specialized restaurant agent using A2A protocol that provides domain expertise
# for restaurant searching and recommendation.
# """

# import asyncio
# import json
# from typing import Dict, Any, List, Optional
# from google_a2a.common.types import AgentCard, AgentSkill
# from google_a2a.common.task_manager import BaseTaskManager
# from adk.exa_client import ExaSearchClient
# from adk.rag_shield import RAGShield
# from adk.restaurant_selector.main import RestaurantSelectorAgent
# import logging

# logger = logging.getLogger(__name__)

# # Restaurant Agent Card Definition
# restaurant_card = AgentCard(
#     id="restaurant-agent",
#     name="Restaurant Domain Expert",
#     description="Specialized agent for restaurant discovery, analysis, and recommendations",
#     skills=[
#         AgentSkill(
#             id="restaurant-search",
#             name="Restaurant Search",
#             description="Searches for restaurants using real-time web data",
#             tags=["restaurant", "search", "discovery"],
#             examples=["Find Italian restaurants in NYC", "Search for vegetarian-friendly places"],
#             inputModes=["text"],
#             outputModes=["json"],
#         ),
#         AgentSkill(
#             id="restaurant-filter",
#             name="Restaurant Filtering",
#             description="Filters restaurants by specific criteria like price, cuisine, location",
#             tags=["restaurant", "filter", "criteria"],
#             examples=["Filter by price range $20-40", "Find restaurants with outdoor seating"],
#             inputModes=["text"],
#             outputModes=["json"],
#         ),
#         AgentSkill(
#             id="restaurant-analysis",
#             name="Restaurant Analysis",
#             description="Analyzes restaurant options and provides detailed recommendations",
#             tags=["restaurant", "analysis", "recommendation"],
#             examples=["Analyze these restaurants for a business meeting", "Compare sushi restaurants"],
#             inputModes=["text"],
#             outputModes=["json"],
#         ),
#         AgentSkill(
#             id="group-restaurant-matching",
#             name="Group Restaurant Matching",
#             description="Finds restaurants that satisfy multiple users' preferences",
#             tags=["restaurant", "group", "matching"],
#             examples=["Find restaurant for 3 people with different preferences", "Match restaurant to group needs"],
#             inputModes=["text"],
#             outputModes=["json"],
#         ),
#         AgentSkill(
#             id="restaurant-details",
#             name="Restaurant Details",
#             description="Gets detailed information about specific restaurants",
#             tags=["restaurant", "details", "information"],
#             examples=["Get details about Mario's Italian Restaurant", "What are the hours for Blue Sushi?"],
#             inputModes=["text"],
#             outputModes=["json"],
#         )
#     ],
# )

# class RestaurantTaskManager(BaseTaskManager):
#     """
#     Restaurant agent task manager specializing in restaurant-related tasks.
#     """
    
#     def __init__(self):
#         """Initialize restaurant task manager."""
#         self.exa_client = ExaSearchClient()
#         self.rag_shield = RAGShield()
#         self.restaurant_selector = RestaurantSelectorAgent()
        
#         # Restaurant-specific filtering criteria
#         self.price_ranges = {
#             "budget": {"min": 1, "max": 2, "description": "Under $20 per person"},
#             "moderate": {"min": 2, "max": 3, "description": "$20-40 per person"},
#             "upscale": {"min": 3, "max": 4, "description": "$40+ per person"}
#         }
        
#         self.cuisine_types = [
#             "italian", "japanese", "chinese", "mexican", "thai", "indian", "french",
#             "mediterranean", "american", "korean", "vietnamese", "greek", "spanish"
#         ]
        
#         self.dietary_restrictions = [
#             "vegetarian", "vegan", "gluten-free", "halal", "kosher", "dairy-free", "nut-free"
#         ]
        
#     async def on_task(self, task):
#         """
#         Handle incoming A2A restaurant tasks.
        
#         Args:
#             task: A2A task object
            
#         Returns:
#             Task response
#         """
#         try:
#             skill_id = task.skill_id
#             user_input = task.input.text
            
#             logger.info(f"Processing restaurant task: {skill_id} - {user_input}")
            
#             if skill_id == "restaurant-search":
#                 return await self._handle_restaurant_search(user_input, task)
#             elif skill_id == "restaurant-filter":
#                 return await self._handle_restaurant_filter(user_input, task)
#             elif skill_id == "restaurant-analysis":
#                 return await self._handle_restaurant_analysis(user_input, task)
#             elif skill_id == "group-restaurant-matching":
#                 return await self._handle_group_restaurant_matching(user_input, task)
#             elif skill_id == "restaurant-details":
#                 return await self._handle_restaurant_details(user_input, task)
#             else:
#                 return {"error": f"Unknown restaurant skill: {skill_id}"}
                
#         except Exception as e:
#             logger.error(f"Error processing restaurant task: {e}")
#             return {"error": str(e)}
    
#     async def _handle_restaurant_search(self, user_input: str, task) -> Dict[str, Any]:
#         """Handle restaurant search requests."""
#         try:
#             # Extract search parameters
#             location = task.context.get("location", "New York City") if hasattr(task, 'context') else "New York City"
#             num_results = task.context.get("num_results", 10) if hasattr(task, 'context') else 10
            
#             # Search using Exa client
#             search_results = await self.exa_client.search_restaurants(
#                 user_input, 
#                 location=location, 
#                 num_results=num_results
#             )
            
#             # Also use the existing restaurant selector for additional results
#             try:
#                 selector_results = await self.restaurant_selector.search_restaurants(
#                     user_input, 
#                     location=location
#                 )
                
#                 # Combine results (avoid duplicates by URL)
#                 combined_results = search_results.copy()
#                 existing_urls = {r.url for r in search_results}
                
#                 for selector_result in selector_results:
#                     if selector_result.get("url") not in existing_urls:
#                         # Convert selector result to search result format
#                         from adk.exa_client import SearchResult
#                         combined_results.append(SearchResult(
#                             title=selector_result.get("name", ""),
#                             url=selector_result.get("url", ""),
#                             text=selector_result.get("description", ""),
#                             score=selector_result.get("score", 0.0)
#                         ))
                
#                 search_results = combined_results
                
#             except Exception as e:
#                 logger.warning(f"Error using restaurant selector: {e}")
            
#             # Format results
#             formatted_results = []
#             for result in search_results:
#                 formatted_results.append({
#                     "name": result.title,
#                     "url": result.url,
#                     "description": result.text[:300] + "..." if len(result.text) > 300 else result.text,
#                     "relevance_score": result.score,
#                     "published_date": result.published_date
#                 })
            
#             return {
#                 "query": user_input,
#                 "location": location,
#                 "total_results": len(formatted_results),
#                 "restaurants": formatted_results,
#                 "search_success": True
#             }
            
#         except Exception as e:
#             logger.error(f"Error in restaurant search: {e}")
#             return {"error": str(e), "search_success": False}
    
#     async def _handle_restaurant_filter(self, user_input: str, task) -> Dict[str, Any]:
#         """Handle restaurant filtering requests."""
#         try:
#             # Get restaurants from context or search
#             restaurants = task.context.get("restaurants", []) if hasattr(task, 'context') else []
            
#             if not restaurants:
#                 # First search for restaurants
#                 search_results = await self.exa_client.search_restaurants(user_input, num_results=15)
#                 restaurants = [
#                     {
#                         "name": r.title,
#                         "url": r.url,
#                         "description": r.text,
#                         "score": r.score
#                     }
#                     for r in search_results
#                 ]
            
#             # Extract filtering criteria from user input
#             criteria = self._extract_filter_criteria(user_input)
            
#             # Filter restaurants
#             filtered_restaurants = []
#             for restaurant in restaurants:
#                 if self._matches_filter_criteria(restaurant, criteria):
#                     filtered_restaurants.append(restaurant)
            
#             return {
#                 "original_query": user_input,
#                 "filter_criteria": criteria,
#                 "total_restaurants": len(restaurants),
#                 "filtered_restaurants": len(filtered_restaurants),
#                 "restaurants": filtered_restaurants,
#                 "filter_success": True
#             }
            
#         except Exception as e:
#             logger.error(f"Error in restaurant filtering: {e}")
#             return {"error": str(e), "filter_success": False}
    
#     async def _handle_restaurant_analysis(self, user_input: str, task) -> Dict[str, Any]:
#         """Handle restaurant analysis requests."""
#         try:
#             # Get restaurants to analyze
#             restaurants = task.context.get("restaurants", []) if hasattr(task, 'context') else []
            
#             if not restaurants:
#                 # Search for restaurants to analyze
#                 search_results = await self.exa_client.search_restaurants(user_input, num_results=8)
#                 restaurants = [
#                     {
#                         "name": r.title,
#                         "url": r.url,
#                         "description": r.text,
#                         "score": r.score
#                     }
#                     for r in search_results
#                 ]
            
#             # Use RAG shield to analyze restaurants
#             sources = []
#             for restaurant in restaurants:
#                 source = f"Restaurant: {restaurant['name']}\n"
#                 source += f"URL: {restaurant['url']}\n"
#                 source += f"Description: {restaurant['description']}\n"
#                 source += f"Relevance Score: {restaurant['score']}\n"
#                 sources.append(source)
            
#             analysis_prompt = self.rag_shield.build_basic_prompt(
#                 f"Analyze these restaurants for: {user_input}",
#                 sources
#             )
            
#             # Simple analysis without LLM (since we don't have it initialized here)
#             # In production, you'd use an LLM here
#             analysis = {
#                 "total_restaurants": len(restaurants),
#                 "top_rated": sorted(restaurants, key=lambda x: x['score'], reverse=True)[:3],
#                 "analysis_summary": f"Analyzed {len(restaurants)} restaurants based on: {user_input}",
#                 "recommendations": [
#                     {
#                         "restaurant": r['name'],
#                         "reason": f"High relevance score ({r['score']:.3f}) for your criteria",
#                         "url": r['url']
#                     }
#                     for r in sorted(restaurants, key=lambda x: x['score'], reverse=True)[:3]
#                 ]
#             }
            
#             return {
#                 "analysis_query": user_input,
#                 "restaurants_analyzed": len(restaurants),
#                 "analysis": analysis,
#                 "analysis_success": True
#             }
            
#         except Exception as e:
#             logger.error(f"Error in restaurant analysis: {e}")
#             return {"error": str(e), "analysis_success": False}
    
#     async def _handle_group_restaurant_matching(self, user_input: str, task) -> Dict[str, Any]:
#         """Handle group restaurant matching requests."""
#         try:
#             # Get group preferences from context
#             group_preferences = task.context.get("group_preferences", []) if hasattr(task, 'context') else []
#             location = task.context.get("location", "New York City") if hasattr(task, 'context') else "New York City"
            
#             if not group_preferences:
#                 # Try to extract from user input
#                 group_preferences = [user_input]
            
#             # Combine all preferences for search
#             combined_query = " ".join(group_preferences)
            
#             # Search for restaurants that might satisfy the group
#             search_results = await self.exa_client.search_restaurants(
#                 combined_query, 
#                 location=location, 
#                 num_results=12
#             )
            
#             # Score restaurants based on how well they match group preferences
#             scored_restaurants = []
#             for result in search_results:
#                 match_score = self._calculate_group_match_score(result.text, group_preferences)
#                 scored_restaurants.append({
#                     "name": result.title,
#                     "url": result.url,
#                     "description": result.text[:300] + "..." if len(result.text) > 300 else result.text,
#                     "relevance_score": result.score,
#                     "group_match_score": match_score,
#                     "combined_score": (result.score + match_score) / 2
#                 })
            
#             # Sort by combined score
#             scored_restaurants.sort(key=lambda x: x['combined_score'], reverse=True)
            
#             return {
#                 "group_query": user_input,
#                 "group_preferences": group_preferences,
#                 "location": location,
#                 "total_restaurants": len(scored_restaurants),
#                 "best_matches": scored_restaurants[:5],
#                 "all_restaurants": scored_restaurants,
#                 "matching_success": True
#             }
            
#         except Exception as e:
#             logger.error(f"Error in group restaurant matching: {e}")
#             return {"error": str(e), "matching_success": False}
    
#     async def _handle_restaurant_details(self, user_input: str, task) -> Dict[str, Any]:
#         """Handle restaurant details requests."""
#         try:
#             # Search for the specific restaurant
#             search_results = await self.exa_client.search_restaurants(user_input, num_results=3)
            
#             if not search_results:
#                 return {"error": "Restaurant not found", "details_success": False}
            
#             # Get detailed content for top result
#             top_result = search_results[0]
#             detailed_content = await self.exa_client.get_content([top_result.url])
            
#             restaurant_details = {
#                 "name": top_result.title,
#                 "url": top_result.url,
#                 "basic_info": top_result.text,
#                 "relevance_score": top_result.score,
#                 "published_date": top_result.published_date
#             }
            
#             if detailed_content:
#                 restaurant_details["detailed_content"] = detailed_content[0].text
            
#             # Extract key information
#             extracted_info = self._extract_restaurant_info(restaurant_details)
            
#             return {
#                 "query": user_input,
#                 "restaurant_details": restaurant_details,
#                 "extracted_info": extracted_info,
#                 "details_success": True
#             }
            
#         except Exception as e:
#             logger.error(f"Error getting restaurant details: {e}")
#             return {"error": str(e), "details_success": False}
    
#     def _extract_filter_criteria(self, user_input: str) -> Dict[str, Any]:
#         """Extract filtering criteria from user input."""
#         criteria = {}
        
#         # Price range detection
#         if "budget" in user_input.lower() or "cheap" in user_input.lower():
#             criteria["price_range"] = "budget"
#         elif "expensive" in user_input.lower() or "upscale" in user_input.lower():
#             criteria["price_range"] = "upscale"
#         elif "moderate" in user_input.lower():
#             criteria["price_range"] = "moderate"
        
#         # Cuisine type detection
#         for cuisine in self.cuisine_types:
#             if cuisine.lower() in user_input.lower():
#                 criteria["cuisine"] = cuisine
#                 break
        
#         # Dietary restrictions
#         found_restrictions = []
#         for restriction in self.dietary_restrictions:
#             if restriction.lower() in user_input.lower():
#                 found_restrictions.append(restriction)
#         if found_restrictions:
#             criteria["dietary_restrictions"] = found_restrictions
        
#         return criteria
    
#     def _matches_filter_criteria(self, restaurant: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
#         """Check if restaurant matches filter criteria."""
#         text = restaurant.get("description", "").lower()
        
#         # Check cuisine
#         if "cuisine" in criteria:
#             if criteria["cuisine"].lower() not in text:
#                 return False
        
#         # Check dietary restrictions
#         if "dietary_restrictions" in criteria:
#             found_restriction = False
#             for restriction in criteria["dietary_restrictions"]:
#                 if restriction.lower() in text:
#                     found_restriction = True
#                     break
#             if not found_restriction:
#                 return False
        
#         # Additional criteria can be added here
#         return True
    
#     def _calculate_group_match_score(self, restaurant_text: str, group_preferences: List[str]) -> float:
#         """Calculate how well a restaurant matches group preferences."""
#         restaurant_text = restaurant_text.lower()
#         total_score = 0.0
        
#         for preference in group_preferences:
#             preference_words = preference.lower().split()
#             matches = sum(1 for word in preference_words if word in restaurant_text)
#             preference_score = matches / len(preference_words) if preference_words else 0
#             total_score += preference_score
        
#         return total_score / len(group_preferences) if group_preferences else 0.0
    
#     def _extract_restaurant_info(self, restaurant_details: Dict[str, Any]) -> Dict[str, Any]:
#         """Extract key information from restaurant details."""
#         text = restaurant_details.get("detailed_content", restaurant_details.get("basic_info", ""))
        
#         extracted = {
#             "name": restaurant_details.get("name", ""),
#             "url": restaurant_details.get("url", ""),
#             "has_vegetarian_options": any(word in text.lower() for word in ["vegetarian", "vegan", "plant-based"]),
#             "has_outdoor_seating": any(word in text.lower() for word in ["outdoor", "patio", "terrace"]),
#             "accepts_reservations": any(word in text.lower() for word in ["reservation", "book", "table"]),
#             "price_indicators": []
#         }
        
#         # Extract price indicators
#         if "$" in text:
#             extracted["price_indicators"].append("$ symbols found")
#         for price_word in ["expensive", "affordable", "cheap", "budget", "upscale"]:
#             if price_word in text.lower():
#                 extracted["price_indicators"].append(price_word)
        
#         return extracted


# if __name__ == "__main__":
#     # Example usage
#     async def main():
#         # Initialize task manager
#         task_manager = RestaurantTaskManager()
        
#         print("Restaurant Agent A2A Task Manager initialized")
        
#         # Example task simulation
#         class MockTask:
#             def __init__(self, skill_id, input_text, context=None):
#                 self.skill_id = skill_id
#                 self.input = type('obj', (object,), {'text': input_text})
#                 self.context = context or {}
        
#         # Test restaurant search
#         task = MockTask("restaurant-search", "Italian vegetarian restaurants", {"location": "New York City"})
#         result = await task_manager.on_task(task)
#         print(f"Restaurant search result: {json.dumps(result, indent=2)}")
    
#     asyncio.run(main()) 