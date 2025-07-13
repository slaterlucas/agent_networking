"""
Centralized Networking API Service

This service provides REST endpoints for the PeopleNetworking functionality,
allowing the frontend and other services to access networking features.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import logging
from networking.networking import PeopleNetworking

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the networking system
networking = PeopleNetworking()

# Initialize with sample data
sample_people = {
    "Alice": "I love technology, programming, and outdoor activities. I enjoy hiking and coding.",
    "Bob": "I'm passionate about cooking, trying new recipes, and exploring different cuisines. I love traveling and photography.",
    "Charlie": "I'm into fitness, yoga, and healthy living. I enjoy nature walks and meditation.",
    "Diana": "I love music, playing guitar, and going to concerts. I'm also interested in art and painting.",
    "Eve": "I'm a sports enthusiast, especially football and basketball. I enjoy watching games and playing fantasy sports.",
    "Frank": "I enjoy reading mystery novels and crime thrillers. I like solving puzzles and playing chess.",
    "Grace": "I'm passionate about cooking and experimenting with new flavors. I enjoy food photography and blogging.",
    "Henry": "I love outdoor adventures like hiking, camping, and rock climbing. I enjoy nature photography.",
    "Iris": "I'm interested in technology, artificial intelligence, and machine learning. I enjoy coding and building projects.",
    "Jack": "I enjoy reading books, especially science fiction and fantasy novels. I enjoy hiking and outdoor activities."
}

networking.add_people(sample_people)
networking.cluster_people(n_clusters=4, method='kmeans')

# Pydantic models
class NetworkingRequest(BaseModel):
    target_person: str
    k: int = 5

class ClusteringRequest(BaseModel):
    n_clusters: int = 3
    method: str = "kmeans"

class PeoplePreferencesRequest(BaseModel):
    people_preferences: Dict[str, str]

class PersonProfile(BaseModel):
    name: str
    preferences: str
    interests: Optional[List[str]] = None
    location: Optional[str] = None

# Create FastAPI app
app = FastAPI(
    title="Networking API",
    description="API for people networking, clustering, and similarity matching",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Networking API",
        "version": "1.0.0",
        "endpoints": [
            "/networking/similar",
            "/networking/cluster", 
            "/networking/clusters/{cluster_id}",
            "/networking/top-pairs",
            "/networking/features",
            "/networking/update-preferences",
            "/networking/people",
            "/networking/add-person"
        ]
    }

@app.post("/networking/similar")
async def find_similar_people(request: NetworkingRequest):
    """Find similar people to a target person."""
    try:
        similar_people = networking.find_similar_people(request.target_person, request.k)
        return {
            "target_person": request.target_person,
            "similar_people": [{"name": name, "similarity": float(score)} for name, score in similar_people]
        }
    except Exception as e:
        logger.error(f"Error finding similar people: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/networking/cluster")
async def cluster_people(request: ClusteringRequest):
    """Cluster people based on their preferences."""
    try:
        clusters = networking.cluster_people(request.n_clusters, request.method)
        cluster_members = {}
        for cluster_id in range(request.n_clusters):
            cluster_members[cluster_id] = networking.get_cluster_members(cluster_id)
        return {
            "clusters": clusters,
            "cluster_members": cluster_members,
            "n_clusters": request.n_clusters,
            "method": request.method
        }
    except Exception as e:
        logger.error(f"Error clustering people: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/networking/clusters/{cluster_id}")
async def get_cluster_members(cluster_id: int):
    """Get members of a specific cluster."""
    try:
        members = networking.get_cluster_members(cluster_id)
        return {"cluster_id": cluster_id, "members": members}
    except Exception as e:
        logger.error(f"Error getting cluster members: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/networking/top-pairs")
async def find_top_similar_pairs(k: int = 10):
    """Find top k most similar pairs of people."""
    try:
        similar_pairs = networking.find_top_k_similar_pairs(k)
        return {
            "similar_pairs": [
                {"person1": p1, "person2": p2, "similarity": float(score)} 
                for p1, p2, score in similar_pairs
            ]
        }
    except Exception as e:
        logger.error(f"Error finding top pairs: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/networking/features")
async def get_feature_importance(n_features: int = 10):
    """Get the most important features for clustering."""
    try:
        features = networking.get_feature_importance(n_features)
        return {
            "features": [{"feature": feature, "importance": float(importance)} for feature, importance in features]
        }
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/networking/update-preferences")
async def update_people_preferences(request: PeoplePreferencesRequest):
    """Update the people preferences in the networking system."""
    try:
        networking.add_people(request.people_preferences)
        return {"message": "Preferences updated successfully", "count": len(request.people_preferences)}
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/networking/people")
async def get_all_people():
    """Get all people in the networking system."""
    try:
        if networking.people_data is not None:
            people = []
            for _, row in networking.people_data.iterrows():
                people.append({
                    "name": row['name'],
                    "preferences": row['preferences']
                })
            return {"people": people}
        else:
            return {"people": []}
    except Exception as e:
        logger.error(f"Error getting people: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/networking/add-person")
async def add_person(person: PersonProfile):
    """Add a single person to the networking system."""
    try:
        people_data = {person.name: person.preferences}
        networking.add_people(people_data)
        return {
            "message": f"Person {person.name} added successfully",
            "person": {
                "name": person.name,
                "preferences": person.preferences,
                "interests": person.interests,
                "location": person.location
            }
        }
    except Exception as e:
        logger.error(f"Error adding person: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/networking/stats")
async def get_networking_stats():
    """Get statistics about the networking system."""
    try:
        stats = {
            "total_people": len(networking.people_data) if networking.people_data is not None else 0,
            "has_clusters": networking.cluster_labels is not None,
            "has_similarity_matrix": networking.similarity_matrix is not None,
            "has_feature_matrix": networking.feature_matrix is not None
        }
        
        if networking.cluster_labels is not None:
            stats["n_clusters"] = len(set(networking.cluster_labels))
        
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 