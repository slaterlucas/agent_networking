"""
Redis Vector Store for Agent Networking System

High-performance vector store using Redis with FT/HNSW for sub-millisecond k-NN lookups.
Integrates with the existing people networking system for preference matching.
"""

import os
import json
import asyncio
import redis
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class VectorSearchResult:
    """Result from vector search."""
    id: str
    score: float
    metadata: Dict[str, Any]
    text: str

class RedisVectorStore:
    """
    High-performance vector store using Redis FT/HNSW for fast similarity searches.
    """
    
    def __init__(self, namespace: str = "prefs", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize Redis vector store.
        
        Args:
            namespace: Namespace for the vector index
            model_name: Sentence transformer model name
        """
        self.namespace = namespace
        self.model = SentenceTransformer(model_name)
        self.vector_dim = self.model.get_sentence_embedding_dimension()
        
        # Redis connection
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
        
        # Index name
        self.index_name = f"idx:{namespace}"
        
    async def create_index(self, force_recreate: bool = False):
        """Create or recreate the vector index."""
        try:
            if force_recreate:
                try:
                    self.redis_client.ft(self.index_name).dropindex()
                    logger.info(f"Dropped existing index: {self.index_name}")
                except Exception:
                    pass  # Index doesn't exist
            
            # Create index with HNSW algorithm
            schema = [
                "user_id", "TEXT", "SORTABLE",
                "preferences", "TEXT",
                "metadata", "TEXT",
                "vec", "VECTOR", "HNSW", "6",
                "TYPE", "FLOAT32",
                "DIM", str(self.vector_dim),
                "DISTANCE_METRIC", "COSINE"
            ]
            
            self.redis_client.ft(self.index_name).create_index(
                schema,
                definition=redis.commands.search.IndexDefinition(
                    prefix=[f"{self.namespace}:"],
                    index_type=redis.commands.search.IndexType.HASH
                )
            )
            logger.info(f"Created vector index: {self.index_name}")
            
        except Exception as e:
            if "Index already exists" in str(e):
                logger.info(f"Index {self.index_name} already exists")
            else:
                logger.error(f"Error creating index: {e}")
                raise
    
    async def add_user_preferences(self, user_id: str, preferences: str, metadata: Dict[str, Any] = None):
        """
        Add user preferences to the vector store.
        
        Args:
            user_id: Unique user identifier
            preferences: User preferences as text
            metadata: Additional metadata
        """
        try:
            # Generate embedding
            embedding = self.model.encode(preferences)
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            metadata["user_id"] = user_id
            metadata["preferences"] = preferences
            
            # Store in Redis
            key = f"{self.namespace}:{user_id}"
            pipe = self.redis_client.pipeline()
            pipe.hset(key, mapping={
                "user_id": user_id,
                "preferences": preferences,
                "metadata": json.dumps(metadata),
                "vec": embedding.astype(np.float32).tobytes()
            })
            await asyncio.get_event_loop().run_in_executor(None, pipe.execute)
            
            logger.debug(f"Added preferences for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error adding user preferences: {e}")
            raise
    
    async def knn_search(self, query: str, k: int = 5, user_filter: Optional[List[str]] = None) -> List[VectorSearchResult]:
        """
        Perform k-nearest neighbors search.
        
        Args:
            query: Query text
            k: Number of results to return
            user_filter: Optional list of user IDs to filter by
            
        Returns:
            List of VectorSearchResult objects
        """
        try:
            # Generate query embedding
            query_embedding = self.model.encode(query)
            
            # Build search query
            search_query = f"*=>[KNN {k} @vec $BLOB]"
            if user_filter:
                user_filter_str = "|".join(user_filter)
                search_query = f"(@user_id:{user_filter_str}) => {search_query}"
            
            # Execute search
            def _search():
                return self.redis_client.ft(self.index_name).search(
                    search_query,
                    query_params={"BLOB": query_embedding.astype(np.float32).tobytes()},
                    dialect=2
                )
            
            result = await asyncio.get_event_loop().run_in_executor(None, _search)
            
            # Process results
            search_results = []
            for doc in result.docs:
                metadata = json.loads(doc.metadata) if hasattr(doc, 'metadata') else {}
                search_results.append(VectorSearchResult(
                    id=doc.user_id,
                    score=float(doc.__dict__.get('__score', 0)),
                    metadata=metadata,
                    text=doc.preferences
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error performing kNN search: {e}")
            return []
    
    async def find_similar_users(self, user_id: str, k: int = 5) -> List[VectorSearchResult]:
        """
        Find users similar to a given user.
        
        Args:
            user_id: User ID to find similar users for
            k: Number of similar users to return
            
        Returns:
            List of similar users
        """
        try:
            # Get user's preferences
            key = f"{self.namespace}:{user_id}"
            user_data = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.hgetall, key
            )
            
            if not user_data:
                logger.warning(f"User {user_id} not found")
                return []
            
            # Use their preferences as query
            preferences = user_data.get("preferences", "")
            results = await self.knn_search(preferences, k + 1)  # +1 to exclude self
            
            # Filter out the user themselves
            similar_users = [r for r in results if r.id != user_id]
            
            return similar_users[:k]
            
        except Exception as e:
            logger.error(f"Error finding similar users: {e}")
            return []
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences by ID."""
        try:
            key = f"{self.namespace}:{user_id}"
            user_data = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.hgetall, key
            )
            
            if not user_data:
                return None
            
            metadata = json.loads(user_data.get("metadata", "{}"))
            return {
                "user_id": user_data.get("user_id"),
                "preferences": user_data.get("preferences"),
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return None
    
    async def update_user_preferences(self, user_id: str, preferences: str, metadata: Dict[str, Any] = None):
        """Update user preferences."""
        await self.add_user_preferences(user_id, preferences, metadata)
    
    async def delete_user(self, user_id: str):
        """Delete user from vector store."""
        try:
            key = f"{self.namespace}:{user_id}"
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.delete, key
            )
            logger.info(f"Deleted user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        try:
            info = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.ft(self.index_name).info
            )
            
            return {
                "total_docs": info.get("num_docs", 0),
                "index_name": self.index_name,
                "vector_dim": self.vector_dim,
                "model": self.model.model_name if hasattr(self.model, 'model_name') else "unknown"
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}

# Utility function for easy setup
async def setup_vector_store_with_preferences(preferences: Dict[str, str], namespace: str = "prefs") -> RedisVectorStore:
    """
    Set up vector store with user preferences.
    
    Args:
        preferences: Dictionary of user_id -> preferences
        namespace: Vector store namespace
        
    Returns:
        Initialized RedisVectorStore
    """
    store = RedisVectorStore(namespace)
    await store.create_index(force_recreate=True)
    
    # Add all preferences
    for user_id, prefs in preferences.items():
        await store.add_user_preferences(user_id, prefs)
    
    logger.info(f"Set up vector store with {len(preferences)} users")
    return store


if __name__ == "__main__":
    # Example usage
    async def main():
        # Sample preferences
        preferences = {
            "alice": "I love Italian food, especially vegetarian options. I enjoy quiet restaurants for business meetings.",
            "bob": "I'm a big fan of sushi and Japanese cuisine. I like trendy places with good atmosphere.",
            "charlie": "I prefer healthy food, salads, and Mediterranean cuisine. I'm vegetarian and like casual dining."
        }
        
        # Set up vector store
        store = await setup_vector_store_with_preferences(preferences)
        
        # Find similar users
        similar_to_alice = await store.find_similar_users("alice", k=2)
        print(f"Users similar to Alice:")
        for result in similar_to_alice:
            print(f"  {result.id}: {result.score:.3f}")
        
        # Search by query
        search_results = await store.knn_search("vegetarian Italian restaurant", k=3)
        print(f"\nUsers interested in vegetarian Italian:")
        for result in search_results:
            print(f"  {result.id}: {result.score:.3f}")
        
        # Get stats
        stats = await store.get_stats()
        print(f"\nVector store stats: {stats}")
    
    asyncio.run(main()) 