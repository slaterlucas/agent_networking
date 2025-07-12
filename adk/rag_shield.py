"""
RAG Shield for Agent Networking System

Hallucination prevention system that constrains agent responses to only use provided sources.
Integrates with the vector store and Exa search results.
"""

from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class RAGShield:
    """
    RAG Shield system to prevent hallucinations by constraining responses to sources.
    """
    
    # System prompt template
    SYSTEM_TEMPLATE = """# System Instructions
You are an AI assistant helping with restaurant recommendations and user networking.

CRITICAL RULES:
1. Answer ONLY using information from the "Sources" section below
2. If you cannot find relevant information in the sources, say "I don't have enough information to answer that"
3. Always cite your sources using [Source N] format
4. Do not make up information or use knowledge not provided in the sources
5. Be helpful but stay within the bounds of the provided information

# Task
{task}

# Sources
{sources}

# Response
Please provide your response based only on the sources above:"""

    USER_CONTEXT_TEMPLATE = """# User Context
User: {user_id}
Preferences: {preferences}
Similar Users: {similar_users}

# Query
{query}

# Available Sources
{sources}

Please provide a response that helps this user based on their preferences and the available information."""

    COLLABORATION_TEMPLATE = """# Collaboration Request
Primary User: {primary_user}
Secondary User: {secondary_user}
Task: {task}

# User Preferences
Primary User Preferences: {primary_preferences}
Secondary User Preferences: {secondary_preferences}

# Available Sources
{sources}

Please help these users collaborate by finding options that work for both of them based on the available information."""

    def __init__(self):
        """Initialize RAG Shield."""
        pass
    
    def build_basic_prompt(self, task: str, sources: List[str]) -> str:
        """
        Build a basic prompt with RAG shield protection.
        
        Args:
            task: The task or query to respond to
            sources: List of source texts to use
            
        Returns:
            Formatted prompt with RAG shield protection
        """
        # Format sources with numbers
        formatted_sources = []
        for i, source in enumerate(sources, 1):
            formatted_sources.append(f"[Source {i}] {source}")
        
        sources_text = "\n".join(formatted_sources)
        
        return self.SYSTEM_TEMPLATE.format(
            task=task,
            sources=sources_text
        )
    
    def build_user_context_prompt(self, user_id: str, preferences: str, similar_users: List[str], 
                                 query: str, sources: List[str]) -> str:
        """
        Build a prompt with user context and RAG shield protection.
        
        Args:
            user_id: User ID
            preferences: User preferences
            similar_users: List of similar users
            query: User query
            sources: List of source texts
            
        Returns:
            Formatted prompt with user context and RAG shield
        """
        # Format sources
        formatted_sources = []
        for i, source in enumerate(sources, 1):
            formatted_sources.append(f"[Source {i}] {source}")
        
        sources_text = "\n".join(formatted_sources)
        similar_users_text = ", ".join(similar_users) if similar_users else "None"
        
        return self.USER_CONTEXT_TEMPLATE.format(
            user_id=user_id,
            preferences=preferences,
            similar_users=similar_users_text,
            query=query,
            sources=sources_text
        )
    
    def build_collaboration_prompt(self, primary_user: str, secondary_user: str, task: str,
                                  primary_preferences: str, secondary_preferences: str,
                                  sources: List[str]) -> str:
        """
        Build a collaboration prompt with RAG shield protection.
        
        Args:
            primary_user: Primary user ID
            secondary_user: Secondary user ID
            task: Collaboration task
            primary_preferences: Primary user preferences
            secondary_preferences: Secondary user preferences
            sources: List of source texts
            
        Returns:
            Formatted collaboration prompt with RAG shield
        """
        # Format sources
        formatted_sources = []
        for i, source in enumerate(sources, 1):
            formatted_sources.append(f"[Source {i}] {source}")
        
        sources_text = "\n".join(formatted_sources)
        
        return self.COLLABORATION_TEMPLATE.format(
            primary_user=primary_user,
            secondary_user=secondary_user,
            task=task,
            primary_preferences=primary_preferences,
            secondary_preferences=secondary_preferences,
            sources=sources_text
        )
    
    def extract_restaurant_info(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """
        Extract relevant restaurant information from search results.
        
        Args:
            search_results: List of search results from Exa
            
        Returns:
            List of formatted restaurant information strings
        """
        restaurant_sources = []
        
        for result in search_results:
            if isinstance(result, dict):
                title = result.get("title", "Unknown Restaurant")
                url = result.get("url", "")
                text = result.get("text", "")
                score = result.get("score", 0.0)
                
                # Format restaurant information
                restaurant_info = f"{title}\n"
                restaurant_info += f"URL: {url}\n"
                restaurant_info += f"Relevance Score: {score:.3f}\n"
                restaurant_info += f"Information: {text[:500]}..."  # Limit text length
                
                restaurant_sources.append(restaurant_info)
            else:
                # Handle SearchResult objects
                restaurant_info = f"{result.title}\n"
                restaurant_info += f"URL: {result.url}\n"
                restaurant_info += f"Relevance Score: {result.score:.3f}\n"
                restaurant_info += f"Information: {result.text[:500]}..."
                
                restaurant_sources.append(restaurant_info)
        
        return restaurant_sources
    
    def extract_user_preferences(self, users_data: List[Dict[str, Any]]) -> List[str]:
        """
        Extract user preference information for sources.
        
        Args:
            users_data: List of user data dictionaries
            
        Returns:
            List of formatted user preference strings
        """
        user_sources = []
        
        for user_data in users_data:
            user_id = user_data.get("user_id", "Unknown")
            preferences = user_data.get("preferences", "")
            metadata = user_data.get("metadata", {})
            
            user_info = f"User: {user_id}\n"
            user_info += f"Preferences: {preferences}\n"
            if metadata:
                user_info += f"Additional Info: {json.dumps(metadata)}\n"
            
            user_sources.append(user_info)
        
        return user_sources
    
    def validate_response(self, response: str, sources: List[str]) -> Dict[str, Any]:
        """
        Validate that the response uses only information from sources.
        
        Args:
            response: Generated response
            sources: List of source texts
            
        Returns:
            Validation results dictionary
        """
        validation_results = {
            "is_valid": True,
            "issues": [],
            "citations_found": [],
            "hallucination_risk": "low"
        }
        
        # Check for source citations
        import re
        citation_pattern = r'\[Source \d+\]'
        citations = re.findall(citation_pattern, response)
        validation_results["citations_found"] = citations
        
        # Basic validation checks
        if not citations:
            validation_results["issues"].append("No source citations found")
            validation_results["hallucination_risk"] = "medium"
        
        if "I don't have enough information" in response:
            validation_results["hallucination_risk"] = "very_low"
        
        # Check for common hallucination indicators
        hallucination_indicators = [
            "I know that", "It's well known that", "Generally speaking",
            "In my experience", "I believe", "I think"
        ]
        
        for indicator in hallucination_indicators:
            if indicator.lower() in response.lower():
                validation_results["issues"].append(f"Potential hallucination indicator: {indicator}")
                validation_results["hallucination_risk"] = "high"
        
        if validation_results["issues"]:
            validation_results["is_valid"] = False
        
        return validation_results
    
    def create_fallback_response(self, task: str) -> str:
        """
        Create a safe fallback response when validation fails.
        
        Args:
            task: Original task/query
            
        Returns:
            Safe fallback response
        """
        return f"I don't have enough reliable information to answer your question about '{task}'. Please provide more specific details or try a different query."

# Utility functions
def build_restaurant_recommendation_prompt(user_preferences: str, search_results: List[Dict[str, Any]]) -> str:
    """
    Build a prompt for restaurant recommendations with RAG shield.
    
    Args:
        user_preferences: User preferences
        search_results: Search results from Exa
        
    Returns:
        RAG-protected prompt
    """
    shield = RAGShield()
    sources = shield.extract_restaurant_info(search_results)
    
    task = f"Recommend restaurants based on these preferences: {user_preferences}"
    
    return shield.build_basic_prompt(task, sources)

def build_group_collaboration_prompt(users_data: List[Dict[str, Any]], task: str, 
                                   search_results: List[Dict[str, Any]]) -> str:
    """
    Build a prompt for group collaboration with RAG shield.
    
    Args:
        users_data: List of user data
        task: Collaboration task
        search_results: Search results from Exa
        
    Returns:
        RAG-protected collaboration prompt
    """
    shield = RAGShield()
    
    # Combine user preferences and restaurant sources
    user_sources = shield.extract_user_preferences(users_data)
    restaurant_sources = shield.extract_restaurant_info(search_results)
    all_sources = user_sources + restaurant_sources
    
    if len(users_data) >= 2:
        return shield.build_collaboration_prompt(
            primary_user=users_data[0].get("user_id", "User1"),
            secondary_user=users_data[1].get("user_id", "User2"),
            task=task,
            primary_preferences=users_data[0].get("preferences", ""),
            secondary_preferences=users_data[1].get("preferences", ""),
            sources=all_sources
        )
    else:
        return shield.build_basic_prompt(task, all_sources)

if __name__ == "__main__":
    # Example usage
    shield = RAGShield()
    
    # Example sources
    sources = [
        "Mario's Italian Restaurant: Located downtown, serves authentic Italian cuisine with vegetarian options. Price range: $20-35. Highly rated for ambiance.",
        "Sushi Paradise: Modern Japanese restaurant with fresh sushi and trendy atmosphere. Price range: $40-60. Popular with young professionals.",
        "Green Garden Cafe: Healthy, vegetarian-friendly restaurant. Offers salads, Mediterranean dishes. Price range: $15-25. Quiet atmosphere good for business meetings."
    ]
    
    # Build basic prompt
    task = "Find restaurants suitable for a vegetarian who likes quiet places for business meetings"
    prompt = shield.build_basic_prompt(task, sources)
    print("Basic Prompt:")
    print(prompt)
    print("\n" + "="*50 + "\n")
    
    # Build collaboration prompt
    collab_prompt = shield.build_collaboration_prompt(
        primary_user="alice",
        secondary_user="bob",
        task="Find a restaurant for lunch",
        primary_preferences="Vegetarian Italian food, quiet atmosphere, under $30",
        secondary_preferences="Japanese food, trendy atmosphere, willing to spend up to $50",
        sources=sources
    )
    print("Collaboration Prompt:")
    print(collab_prompt)
    print("\n" + "="*50 + "\n")
    
    # Validate response
    sample_response = "Based on [Source 1] and [Source 3], I recommend Mario's Italian Restaurant for Alice as it has vegetarian options and quiet atmosphere under $30. However, I don't have enough information to find a perfect match for both preferences simultaneously."
    validation = shield.validate_response(sample_response, sources)
    print("Validation Results:")
    print(json.dumps(validation, indent=2)) 