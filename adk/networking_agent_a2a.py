"""
Networking Agent A2A Implementation

Specialized networking agent that handles people clustering, similarity matching,
and social networking functionality using the existing PeopleNetworking system.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from google_a2a.common.types import AgentCard, AgentSkill
from google_a2a.common.task_manager import BaseTaskManager
from networking.networking import PeopleNetworking
from adk.redis_vector_store import RedisVectorStore
import logging

logger = logging.getLogger(__name__)

# Networking Agent Card Definition
networking_card = AgentCard(
    id="networking-agent",
    name="People Networking Specialist",
    description="Expert in people clustering, similarity matching, and social networking based on preferences",
    skills=[
        AgentSkill(
            id="people-clustering",
            name="People Clustering",
            description="Clusters people into groups based on similar preferences using ML algorithms",
            tags=["clustering", "people", "similarity", "groups"],
            examples=["Cluster people into 5 groups", "Group people by similar interests"],
            inputModes=["text"],
            outputModes=["json"],
        ),
        AgentSkill(
            id="similarity-matching",
            name="Similarity Matching",
            description="Finds people with similar preferences and interests",
            tags=["similarity", "matching", "preferences", "people"],
            examples=["Find people similar to Alice", "Who has similar food preferences to Bob?"],
            inputModes=["text"],
            outputModes=["json"],
        ),
        AgentSkill(
            id="network-analysis",
            name="Network Analysis",
            description="Analyzes the social network structure and provides insights",
            tags=["network", "analysis", "insights", "social"],
            examples=["Analyze the social network structure", "Show network statistics"],
            inputModes=["text"],
            outputModes=["json"],
        ),
        AgentSkill(
            id="group-formation",
            name="Group Formation",
            description="Forms optimal groups of people for activities based on preferences",
            tags=["group", "formation", "optimization", "activities"],
            examples=["Form groups for lunch", "Create optimal dining groups"],
            inputModes=["text"],
            outputModes=["json"],
        ),
        AgentSkill(
            id="preference-profiling",
            name="Preference Profiling",
            description="Analyzes and profiles individual preferences and characteristics",
            tags=["profiling", "preferences", "analysis", "individual"],
            examples=["Profile Alice's preferences", "Analyze food preference patterns"],
            inputModes=["text"],
            outputModes=["json"],
        )
    ],
)

class NetworkingTaskManager(BaseTaskManager):
    """
    Networking agent task manager specializing in people clustering and similarity matching.
    """
    
    def __init__(self, people_network: Optional[PeopleNetworking] = None):
        """
        Initialize networking task manager.
        
        Args:
            people_network: Existing people networking instance
        """
        self.people_network = people_network or PeopleNetworking()
        self.vector_store = RedisVectorStore("networking")
        
        # Initialize vector store
        asyncio.create_task(self._initialize_vector_store())
        
    async def _initialize_vector_store(self):
        """Initialize the vector store with networking data."""
        try:
            await self.vector_store.create_index()
            
            # If we have networking data, populate vector store
            if self.people_network.people_data is not None:
                for _, row in self.people_network.people_data.iterrows():
                    await self.vector_store.add_user_preferences(
                        row['name'], 
                        row['preferences'],
                        {"clustering_enabled": True}
                    )
                logger.info(f"Initialized networking vector store with {len(self.people_network.people_data)} users")
        except Exception as e:
            logger.error(f"Error initializing networking vector store: {e}")
    
    async def on_task(self, task):
        """
        Handle incoming A2A networking tasks.
        
        Args:
            task: A2A task object
            
        Returns:
            Task response
        """
        try:
            skill_id = task.skill_id
            user_input = task.input.text
            
            logger.info(f"Processing networking task: {skill_id} - {user_input}")
            
            if skill_id == "people-clustering":
                return await self._handle_people_clustering(user_input, task)
            elif skill_id == "similarity-matching":
                return await self._handle_similarity_matching(user_input, task)
            elif skill_id == "network-analysis":
                return await self._handle_network_analysis(user_input, task)
            elif skill_id == "group-formation":
                return await self._handle_group_formation(user_input, task)
            elif skill_id == "preference-profiling":
                return await self._handle_preference_profiling(user_input, task)
            else:
                return {"error": f"Unknown networking skill: {skill_id}"}
                
        except Exception as e:
            logger.error(f"Error processing networking task: {e}")
            return {"error": str(e)}
    
    async def _handle_people_clustering(self, user_input: str, task) -> Dict[str, Any]:
        """Handle people clustering requests."""
        try:
            # Extract clustering parameters
            n_clusters = self._extract_number_from_input(user_input, default=5)
            method = "hierarchical" if "hierarchical" in user_input.lower() else "kmeans"
            
            # Ensure we have networking data
            if self.people_network.people_data is None or len(self.people_network.people_data) == 0:
                return {"error": "No people data available for clustering"}
            
            # Perform clustering
            clusters = self.people_network.cluster_people(n_clusters=n_clusters, method=method)
            
            # Get cluster members
            cluster_groups = {}
            for cluster_id in range(n_clusters):
                members = self.people_network.get_cluster_members(cluster_id)
                if members:  # Only add non-empty clusters
                    cluster_groups[f"cluster_{cluster_id}"] = members
            
            # Calculate cluster statistics
            cluster_stats = {
                "total_people": len(self.people_network.people_data),
                "num_clusters": len(cluster_groups),
                "clustering_method": method,
                "avg_cluster_size": sum(len(members) for members in cluster_groups.values()) / len(cluster_groups) if cluster_groups else 0
            }
            
            # Get feature importance for clustering
            try:
                important_features = self.people_network.get_feature_importance(n_features=5)
                cluster_stats["important_features"] = [
                    {"feature": feature, "importance": importance}
                    for feature, importance in important_features
                ]
            except Exception as e:
                logger.warning(f"Error getting feature importance: {e}")
                cluster_stats["important_features"] = []
            
            return {
                "query": user_input,
                "clustering_parameters": {
                    "n_clusters": n_clusters,
                    "method": method
                },
                "clusters": cluster_groups,
                "cluster_assignments": clusters,
                "statistics": cluster_stats,
                "clustering_success": True
            }
            
        except Exception as e:
            logger.error(f"Error in people clustering: {e}")
            return {"error": str(e), "clustering_success": False}
    
    async def _handle_similarity_matching(self, user_input: str, task) -> Dict[str, Any]:
        """Handle similarity matching requests."""
        try:
            # Extract target person from input
            target_person = self._extract_person_name(user_input)
            k = self._extract_number_from_input(user_input, default=5)
            
            if not target_person:
                # Use vector store for general similarity search
                search_results = await self.vector_store.knn_search(user_input, k=k)
                
                return {
                    "query": user_input,
                    "search_type": "preference_based",
                    "similar_people": [
                        {
                            "person": result.id,
                            "similarity_score": result.score,
                            "preferences": result.text
                        }
                        for result in search_results
                    ],
                    "matching_success": True
                }
            
            # Find similar people using traditional clustering
            traditional_similar = []
            if self.people_network.people_data is not None:
                try:
                    traditional_similar = self.people_network.find_similar_people(target_person, k=k)
                except Exception as e:
                    logger.warning(f"Error finding similar people with traditional method: {e}")
            
            # Find similar people using vector store
            vector_similar = await self.vector_store.find_similar_users(target_person, k=k)
            
            # Get top similar pairs for context
            top_pairs = []
            if self.people_network.people_data is not None:
                try:
                    top_pairs = self.people_network.find_top_k_similar_pairs(k=min(10, len(self.people_network.people_data)))
                except Exception as e:
                    logger.warning(f"Error finding top similar pairs: {e}")
            
            return {
                "query": user_input,
                "target_person": target_person,
                "traditional_similarity": [
                    {"person": name, "similarity_score": score}
                    for name, score in traditional_similar
                ],
                "vector_similarity": [
                    {
                        "person": result.id,
                        "similarity_score": result.score,
                        "preferences": result.text
                    }
                    for result in vector_similar
                ],
                "top_similar_pairs": [
                    {
                        "person1": person1,
                        "person2": person2,
                        "similarity_score": score
                    }
                    for person1, person2, score in top_pairs
                ],
                "matching_success": True
            }
            
        except Exception as e:
            logger.error(f"Error in similarity matching: {e}")
            return {"error": str(e), "matching_success": False}
    
    async def _handle_network_analysis(self, user_input: str, task) -> Dict[str, Any]:
        """Handle network analysis requests."""
        try:
            # Get networking statistics
            network_stats = self._get_network_statistics()
            
            # Get cluster analysis if available
            cluster_analysis = {}
            if self.people_network.people_data is not None and len(self.people_network.people_data) > 0:
                try:
                    clusters = self.people_network.cluster_people(n_clusters=min(5, len(self.people_network.people_data)))
                    cluster_analysis = {
                        "total_clusters": len(set(clusters.values())),
                        "cluster_distribution": {},
                        "largest_cluster_size": 0
                    }
                    
                    # Analyze cluster distribution
                    for cluster_id in set(clusters.values()):
                        members = self.people_network.get_cluster_members(cluster_id)
                        cluster_analysis["cluster_distribution"][f"cluster_{cluster_id}"] = len(members)
                        cluster_analysis["largest_cluster_size"] = max(cluster_analysis["largest_cluster_size"], len(members))
                        
                except Exception as e:
                    logger.warning(f"Error in cluster analysis: {e}")
            
            # Get vector store statistics
            vector_stats = await self.vector_store.get_stats()
            
            # Calculate network density and connectivity
            network_metrics = self._calculate_network_metrics()
            
            return {
                "query": user_input,
                "network_statistics": network_stats,
                "cluster_analysis": cluster_analysis,
                "vector_store_stats": vector_stats,
                "network_metrics": network_metrics,
                "analysis_success": True
            }
            
        except Exception as e:
            logger.error(f"Error in network analysis: {e}")
            return {"error": str(e), "analysis_success": False}
    
    async def _handle_group_formation(self, user_input: str, task) -> Dict[str, Any]:
        """Handle group formation requests."""
        try:
            # Extract group size and criteria
            group_size = self._extract_number_from_input(user_input, default=3)
            
            # Get all people
            if self.people_network.people_data is None or len(self.people_network.people_data) == 0:
                return {"error": "No people data available for group formation"}
            
            all_people = self.people_network.people_data['name'].tolist()
            
            # Form groups using clustering
            n_groups = max(1, len(all_people) // group_size)
            clusters = self.people_network.cluster_people(n_clusters=n_groups)
            
            # Create groups
            groups = {}
            for cluster_id in range(n_groups):
                members = self.people_network.get_cluster_members(cluster_id)
                if members:
                    groups[f"group_{cluster_id}"] = {
                        "members": members,
                        "size": len(members),
                        "compatibility_score": self._calculate_group_compatibility(members)
                    }
            
            # Alternative: Form groups based on similarity
            similarity_groups = self._form_similarity_based_groups(all_people, group_size)
            
            return {
                "query": user_input,
                "target_group_size": group_size,
                "clustering_based_groups": groups,
                "similarity_based_groups": similarity_groups,
                "total_people": len(all_people),
                "groups_formed": len(groups),
                "formation_success": True
            }
            
        except Exception as e:
            logger.error(f"Error in group formation: {e}")
            return {"error": str(e), "formation_success": False}
    
    async def _handle_preference_profiling(self, user_input: str, task) -> Dict[str, Any]:
        """Handle preference profiling requests."""
        try:
            # Extract target person
            target_person = self._extract_person_name(user_input)
            
            if not target_person:
                # General preference analysis
                return await self._analyze_general_preferences(user_input)
            
            # Get person's data
            person_data = None
            if self.people_network.people_data is not None:
                person_row = self.people_network.people_data[self.people_network.people_data['name'] == target_person]
                if not person_row.empty:
                    person_data = person_row.iloc[0]
            
            if person_data is None:
                return {"error": f"Person '{target_person}' not found"}
            
            # Get person's preferences
            preferences = person_data['preferences']
            
            # Find similar people
            similar_people = []
            try:
                similar_people = self.people_network.find_similar_people(target_person, k=5)
            except Exception:
                pass
            
            # Get cluster information
            cluster_info = {}
            try:
                clusters = self.people_network.cluster_people(n_clusters=5)
                person_cluster = clusters.get(target_person)
                if person_cluster is not None:
                    cluster_members = self.people_network.get_cluster_members(person_cluster)
                    cluster_info = {
                        "cluster_id": person_cluster,
                        "cluster_members": cluster_members,
                        "cluster_size": len(cluster_members)
                    }
            except Exception:
                pass
            
            # Analyze preferences using vector store
            vector_data = await self.vector_store.get_user_preferences(target_person)
            
            # Extract preference keywords
            preference_keywords = self._extract_preference_keywords(preferences)
            
            return {
                "query": user_input,
                "target_person": target_person,
                "preferences": preferences,
                "similar_people": [
                    {"person": name, "similarity_score": score}
                    for name, score in similar_people
                ],
                "cluster_info": cluster_info,
                "preference_keywords": preference_keywords,
                "vector_data": vector_data,
                "profiling_success": True
            }
            
        except Exception as e:
            logger.error(f"Error in preference profiling: {e}")
            return {"error": str(e), "profiling_success": False}
    
    def _extract_number_from_input(self, text: str, default: int = 5) -> int:
        """Extract number from user input."""
        import re
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else default
    
    def _extract_person_name(self, text: str) -> Optional[str]:
        """Extract person name from user input."""
        # Look for common patterns
        patterns = [
            r'(?:similar to|like|person|user) (\w+)',
            r'(\w+)(?:\'s|s) preferences',
            r'find (\w+)',
            r'(\w+) and'
        ]
        
        for pattern in patterns:
            import re
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _get_network_statistics(self) -> Dict[str, Any]:
        """Get basic network statistics."""
        stats = {
            "total_people": 0,
            "has_similarity_matrix": False,
            "has_clustering": False,
            "feature_matrix_shape": None
        }
        
        if self.people_network.people_data is not None:
            stats["total_people"] = len(self.people_network.people_data)
            stats["has_similarity_matrix"] = self.people_network.similarity_matrix is not None
            stats["has_clustering"] = self.people_network.cluster_labels is not None
            
            if self.people_network.feature_matrix is not None:
                stats["feature_matrix_shape"] = self.people_network.feature_matrix.shape
        
        return stats
    
    def _calculate_network_metrics(self) -> Dict[str, Any]:
        """Calculate network connectivity metrics."""
        metrics = {
            "density": 0.0,
            "average_similarity": 0.0,
            "connectivity": "unknown"
        }
        
        if self.people_network.similarity_matrix is not None:
            import numpy as np
            
            # Calculate average similarity (excluding diagonal)
            mask = np.ones(self.people_network.similarity_matrix.shape, dtype=bool)
            np.fill_diagonal(mask, False)
            
            avg_similarity = np.mean(self.people_network.similarity_matrix[mask])
            metrics["average_similarity"] = float(avg_similarity)
            
            # Calculate density (proportion of high similarity connections)
            high_similarity_threshold = 0.7
            high_similarity_count = np.sum(self.people_network.similarity_matrix[mask] > high_similarity_threshold)
            total_connections = np.sum(mask)
            
            metrics["density"] = float(high_similarity_count / total_connections) if total_connections > 0 else 0.0
            
            # Determine connectivity level
            if metrics["density"] > 0.5:
                metrics["connectivity"] = "high"
            elif metrics["density"] > 0.2:
                metrics["connectivity"] = "medium"
            else:
                metrics["connectivity"] = "low"
        
        return metrics
    
    def _calculate_group_compatibility(self, members: List[str]) -> float:
        """Calculate compatibility score for a group of people."""
        if len(members) < 2 or self.people_network.similarity_matrix is None:
            return 0.0
        
        # Get indices of members
        member_indices = []
        for member in members:
            for i, name in enumerate(self.people_network.people_data['name']):
                if name == member:
                    member_indices.append(i)
                    break
        
        if len(member_indices) < 2:
            return 0.0
        
        # Calculate average pairwise similarity
        import numpy as np
        similarities = []
        for i in range(len(member_indices)):
            for j in range(i + 1, len(member_indices)):
                idx1, idx2 = member_indices[i], member_indices[j]
                similarities.append(self.people_network.similarity_matrix[idx1, idx2])
        
        return float(np.mean(similarities)) if similarities else 0.0
    
    def _form_similarity_based_groups(self, all_people: List[str], target_size: int) -> List[Dict[str, Any]]:
        """Form groups based on similarity rather than clustering."""
        groups = []
        used_people = set()
        
        for person in all_people:
            if person in used_people:
                continue
            
            # Start a new group with this person
            group = [person]
            used_people.add(person)
            
            # Find similar people to add to group
            try:
                similar_people = self.people_network.find_similar_people(person, k=target_size * 2)
                for similar_person, score in similar_people:
                    if similar_person not in used_people and len(group) < target_size:
                        group.append(similar_person)
                        used_people.add(similar_person)
            except Exception:
                pass
            
            if len(group) > 1:  # Only add groups with more than one person
                groups.append({
                    "members": group,
                    "size": len(group),
                    "compatibility_score": self._calculate_group_compatibility(group)
                })
        
        return groups
    
    def _extract_preference_keywords(self, preferences: str) -> List[str]:
        """Extract key preference keywords from text."""
        # Common food and preference keywords
        keywords = [
            "italian", "japanese", "chinese", "mexican", "thai", "indian", "french",
            "vegetarian", "vegan", "gluten-free", "healthy", "spicy", "sweet",
            "quiet", "loud", "casual", "formal", "trendy", "traditional",
            "cheap", "expensive", "budget", "upscale", "fast", "slow"
        ]
        
        found_keywords = []
        text_lower = preferences.lower()
        
        for keyword in keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    async def _analyze_general_preferences(self, query: str) -> Dict[str, Any]:
        """Analyze general preferences across all people."""
        try:
            # Get all people's preferences
            all_preferences = []
            if self.people_network.people_data is not None:
                all_preferences = self.people_network.people_data['preferences'].tolist()
            
            # Extract common keywords
            all_keywords = []
            for prefs in all_preferences:
                keywords = self._extract_preference_keywords(prefs)
                all_keywords.extend(keywords)
            
            # Count keyword frequency
            from collections import Counter
            keyword_counts = Counter(all_keywords)
            
            # Get feature importance
            important_features = []
            try:
                important_features = self.people_network.get_feature_importance(n_features=10)
            except Exception:
                pass
            
            return {
                "query": query,
                "analysis_type": "general_preferences",
                "total_people": len(all_preferences),
                "common_keywords": dict(keyword_counts.most_common(10)),
                "important_features": [
                    {"feature": feature, "importance": importance}
                    for feature, importance in important_features
                ],
                "analysis_success": True
            }
            
        except Exception as e:
            logger.error(f"Error in general preference analysis: {e}")
            return {"error": str(e), "analysis_success": False}
    
    async def add_person_to_network(self, person_name: str, preferences: str):
        """Add a person to the networking system."""
        try:
            # Get current people data
            current_people = {}
            if self.people_network.people_data is not None:
                current_people = dict(zip(
                    self.people_network.people_data['name'],
                    self.people_network.people_data['preferences']
                ))
            
            # Add new person
            current_people[person_name] = preferences
            
            # Update networking system
            self.people_network.add_people(current_people)
            
            # Update vector store
            await self.vector_store.add_user_preferences(person_name, preferences)
            
            logger.info(f"Added person to network: {person_name}")
            
        except Exception as e:
            logger.error(f"Error adding person to network: {e}")
            raise


if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize task manager
        task_manager = NetworkingTaskManager()
        
        # Add sample people
        sample_people = {
            "alice": "I love Italian food, especially vegetarian options. I enjoy quiet restaurants for business meetings.",
            "bob": "I'm a big fan of sushi and Japanese cuisine. I like trendy places with good atmosphere.",
            "charlie": "I prefer healthy food, salads, and Mediterranean cuisine. I'm vegetarian and like casual dining.",
            "diana": "I love trying new cuisines, especially Thai and Vietnamese. I prefer authentic places with good reviews.",
            "eve": "I enjoy comfort food, American cuisine, and family-friendly restaurants. Budget-conscious, prefer under $25."
        }
        
        for person, preferences in sample_people.items():
            await task_manager.add_person_to_network(person, preferences)
        
        print("Networking Agent A2A Task Manager initialized with sample people")
        
        # Example task simulation
        class MockTask:
            def __init__(self, skill_id, input_text, context=None):
                self.skill_id = skill_id
                self.input = type('obj', (object,), {'text': input_text})
                self.context = context or {}
        
        # Test people clustering
        task = MockTask("people-clustering", "cluster people into 3 groups")
        result = await task_manager.on_task(task)
        print(f"People clustering result: {json.dumps(result, indent=2)}")
    
    asyncio.run(main()) 