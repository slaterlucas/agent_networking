"""
Exa Web Search Client for Agent Networking System

High-performance web search client using Exa API for real-time restaurant and location data.
"""

import os
import asyncio
import httpx
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Result from Exa search."""
    title: str
    url: str
    text: str
    score: float
    published_date: Optional[str] = None
    id: Optional[str] = None

class ExaSearchClient:
    """
    High-performance Exa search client for real-time web information.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Exa search client.
        
        Args:
            api_key: Exa API key (will use EXA_API_KEY env var if not provided)
        """
        self.api_key = api_key or os.getenv("EXA_API_KEY")
        if not self.api_key:
            raise ValueError("EXA_API_KEY environment variable must be set")
        
        self.base_url = "https://api.exa.ai"
        self.timeout = 10.0
        
    async def search_restaurants(self, query: str, location: str = None, num_results: int = 10) -> List[SearchResult]:
        """
        Search for restaurants using Exa API.
        
        Args:
            query: Search query
            location: Location to search in
            num_results: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        try:
            # Construct search query
            search_query = f"{query} restaurants"
            if location:
                search_query += f" in {location}"
            
            # Prepare request
            payload = {
                "query": search_query,
                "num_results": num_results,
                "include_domains": [
                    "yelp.com",
                    "google.com",
                    "opentable.com",
                    "zomato.com",
                    "tripadvisor.com",
                    "foursquare.com"
                ],
                "use_autoprompt": True,
                "include_text": True
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json=payload,
                    headers={"X-API-Key": self.api_key}
                )
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                for item in data.get("results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        text=item.get("text", ""),
                        score=item.get("score", 0.0),
                        published_date=item.get("published_date"),
                        id=item.get("id")
                    ))
                
                logger.info(f"Found {len(results)} restaurant results for: {search_query}")
                return results
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching restaurants: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching restaurants: {e}")
            return []
    
    async def search_locations(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        Search for location information.
        
        Args:
            query: Location query
            num_results: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        try:
            payload = {
                "query": f"{query} location information",
                "num_results": num_results,
                "include_domains": [
                    "google.com",
                    "yelp.com",
                    "foursquare.com",
                    "tripadvisor.com"
                ],
                "use_autoprompt": True,
                "include_text": True
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json=payload,
                    headers={"X-API-Key": self.api_key}
                )
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                for item in data.get("results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        text=item.get("text", ""),
                        score=item.get("score", 0.0),
                        published_date=item.get("published_date"),
                        id=item.get("id")
                    ))
                
                logger.info(f"Found {len(results)} location results for: {query}")
                return results
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching locations: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching locations: {e}")
            return []
    
    async def get_content(self, urls: List[str]) -> List[SearchResult]:
        """
        Get content from specific URLs.
        
        Args:
            urls: List of URLs to get content from
            
        Returns:
            List of SearchResult objects with content
        """
        try:
            payload = {
                "urls": urls,
                "include_text": True
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/contents",
                    json=payload,
                    headers={"X-API-Key": self.api_key}
                )
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                for item in data.get("results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        text=item.get("text", ""),
                        score=1.0,  # Content retrieval doesn't have scores
                        published_date=item.get("published_date"),
                        id=item.get("id")
                    ))
                
                logger.info(f"Retrieved content for {len(results)} URLs")
                return results
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting content: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting content: {e}")
            return []
    
    async def search_with_filters(self, query: str, filters: Dict[str, Any]) -> List[SearchResult]:
        """
        Search with custom filters.
        
        Args:
            query: Search query
            filters: Dictionary of filters to apply
            
        Returns:
            List of SearchResult objects
        """
        try:
            payload = {
                "query": query,
                "num_results": filters.get("num_results", 10),
                "use_autoprompt": filters.get("use_autoprompt", True),
                "include_text": filters.get("include_text", True)
            }
            
            # Add optional filters
            if "include_domains" in filters:
                payload["include_domains"] = filters["include_domains"]
            if "exclude_domains" in filters:
                payload["exclude_domains"] = filters["exclude_domains"]
            if "start_published_date" in filters:
                payload["start_published_date"] = filters["start_published_date"]
            if "end_published_date" in filters:
                payload["end_published_date"] = filters["end_published_date"]
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json=payload,
                    headers={"X-API-Key": self.api_key}
                )
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                for item in data.get("results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        text=item.get("text", ""),
                        score=item.get("score", 0.0),
                        published_date=item.get("published_date"),
                        id=item.get("id")
                    ))
                
                logger.info(f"Found {len(results)} results with filters for: {query}")
                return results
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching with filters: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching with filters: {e}")
            return []


# Utility functions for common searches
async def search_restaurants_by_preferences(preferences: str, location: str = None, num_results: int = 10) -> List[SearchResult]:
    """
    Search for restaurants based on user preferences.
    
    Args:
        preferences: User preferences as text
        location: Location to search in
        num_results: Number of results to return
        
    Returns:
        List of SearchResult objects
    """
    client = ExaSearchClient()
    return await client.search_restaurants(preferences, location, num_results)


async def find_restaurants_for_group(group_preferences: List[str], location: str = None, num_results: int = 10) -> List[SearchResult]:
    """
    Find restaurants that satisfy multiple users' preferences.
    
    Args:
        group_preferences: List of preference strings
        location: Location to search in
        num_results: Number of results to return
        
    Returns:
        List of SearchResult objects that match group preferences
    """
    client = ExaSearchClient()
    
    # Combine preferences into a single query
    combined_query = " ".join(group_preferences)
    
    return await client.search_restaurants(combined_query, location, num_results)


if __name__ == "__main__":
    # Example usage
    async def main():
        client = ExaSearchClient()
        
        # Search for restaurants
        results = await client.search_restaurants(
            "Italian vegetarian restaurants",
            location="New York City",
            num_results=5
        )
        
        print(f"Found {len(results)} restaurants:")
        for result in results:
            print(f"  {result.title} - {result.score:.3f}")
            print(f"    {result.url}")
            print(f"    {result.text[:100]}...")
            print()
        
        # Search for locations
        location_results = await client.search_locations("Times Square restaurants")
        print(f"Found {len(location_results)} location results")
        
        # Get content from URLs
        if results:
            content = await client.get_content([results[0].url])
            print(f"Retrieved content from {len(content)} URLs")
    
    asyncio.run(main()) 