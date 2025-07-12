"""
People Networking System using Clustering Algorithms

This module provides functionality to find similar people based on their preferences
using various clustering algorithms and similarity measures.
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Tuple, Dict, Optional
import warnings
warnings.filterwarnings('ignore')


class PeopleNetworking:
    """
    A class to find similar people based on their preferences using clustering algorithms.
    """
    
    def __init__(self, max_features: int = 1000, min_df: int = 1, max_df: float = 0.95):
        """
        Initialize the PeopleNetworking system.
        
        Args:
            max_features: Maximum number of features for TF-IDF vectorization
            min_df: Minimum document frequency for TF-IDF
            max_df: Maximum document frequency for TF-IDF
        """
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2)
        )
        self.scaler = StandardScaler()
        self.people_data = None
        self.feature_matrix = None
        self.cluster_labels = None
        self.similarity_matrix = None
        
    def add_people(self, people_preferences: Dict[str, str]):
        """
        Add people and their preferences to the system.
        
        Args:
            people_preferences: Dictionary mapping person names to their preferences (string)
        """
        self.people_data = pd.DataFrame([
            {'name': name, 'preferences': prefs} 
            for name, prefs in people_preferences.items()
        ])
        
        # Convert preferences to numerical features
        self._vectorize_preferences()
        
    def _vectorize_preferences(self):
        """Convert text preferences to numerical feature vectors."""
        if self.people_data is None:
            raise ValueError("No people data available. Call add_people() first.")
        
        # Transform text to TF-IDF features
        tfidf_matrix = self.vectorizer.fit_transform(self.people_data['preferences'])
        
        # Convert to dense array and scale
        self.feature_matrix = self.scaler.fit_transform(tfidf_matrix.toarray())
        
        # Calculate similarity matrix
        self.similarity_matrix = cosine_similarity(self.feature_matrix)
        
    def cluster_people(self, n_clusters: int = 5, method: str = 'kmeans') -> Dict[str, int]:
        """
        Cluster people based on their preferences.
        
        Args:
            n_clusters: Number of clusters to create
            method: Clustering method ('kmeans' or 'hierarchical')
            
        Returns:
            Dictionary mapping person names to cluster labels
        """
        if self.feature_matrix is None:
            raise ValueError("No feature matrix available. Call add_people() first.")
        
        if method == 'kmeans':
            clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        elif method == 'hierarchical':
            clusterer = AgglomerativeClustering(n_clusters=n_clusters)
        else:
            raise ValueError("Method must be 'kmeans' or 'hierarchical'")
        
        self.cluster_labels = clusterer.fit_predict(self.feature_matrix)
        
        # Create name to cluster mapping
        cluster_mapping = {}
        for i, name in enumerate(self.people_data['name']):
            cluster_mapping[name] = int(self.cluster_labels[i])
        
        return cluster_mapping
    
    def find_similar_people(self, person_name: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Find top k most similar people to a given person.
        
        Args:
            person_name: Name of the person to find similarities for
            k: Number of similar people to return
            
        Returns:
            List of tuples (person_name, similarity_score) sorted by similarity
        """
        if self.similarity_matrix is None:
            raise ValueError("No similarity matrix available. Call add_people() first.")
        
        # Find the index of the person
        person_idx = None
        for i, name in enumerate(self.people_data['name']):
            if name == person_name:
                person_idx = i
                break
        
        if person_idx is None:
            raise ValueError(f"Person '{person_name}' not found in the dataset.")
        
        # Get similarity scores for this person
        similarities = self.similarity_matrix[person_idx]
        
        # Get indices of most similar people (excluding the person themselves)
        similar_indices = np.argsort(similarities)[::-1][1:k+1]
        
        # Create list of similar people with their similarity scores
        similar_people = []
        for idx in similar_indices:
            similar_name = self.people_data.iloc[idx]['name']
            similarity_score = similarities[idx]
            similar_people.append((similar_name, similarity_score))
        
        return similar_people
    
    def find_top_k_similar_pairs(self, k: int = 10) -> List[Tuple[str, str, float]]:
        """
        Find top k most similar pairs of people in the entire dataset.
        
        Args:
            k: Number of similar pairs to return
            
        Returns:
            List of tuples (person1, person2, similarity_score)
        """
        if self.similarity_matrix is None:
            raise ValueError("No similarity matrix available. Call add_people() first.")
        
        # Get upper triangular part of similarity matrix (excluding diagonal)
        n = len(self.people_data)
        similar_pairs = []
        
        for i in range(n):
            for j in range(i+1, n):
                similarity = self.similarity_matrix[i, j]
                person1 = self.people_data.iloc[i]['name']
                person2 = self.people_data.iloc[j]['name']
                similar_pairs.append((person1, person2, similarity))
        
        # Sort by similarity score and return top k
        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        return similar_pairs[:k]
    
    def get_cluster_members(self, cluster_id: int) -> List[str]:
        """
        Get all people in a specific cluster.
        
        Args:
            cluster_id: ID of the cluster
            
        Returns:
            List of person names in the cluster
        """
        if self.cluster_labels is None:
            raise ValueError("No cluster labels available. Call cluster_people() first.")
        
        cluster_members = []
        for i, label in enumerate(self.cluster_labels):
            if label == cluster_id:
                cluster_members.append(self.people_data.iloc[i]['name'])
        
        return cluster_members
    
    def visualize_clusters(self, save_path: Optional[str] = None):
        """
        Visualize the clusters using PCA for dimensionality reduction.
        
        Args:
            save_path: Optional path to save the plot
        """
        if self.feature_matrix is None or self.cluster_labels is None:
            raise ValueError("No clustering results available. Call cluster_people() first.")
        
        # Reduce dimensions for visualization
        pca = PCA(n_components=2)
        reduced_features = pca.fit_transform(self.feature_matrix)
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(reduced_features[:, 0], reduced_features[:, 1], 
                            c=self.cluster_labels, cmap='viridis', alpha=0.7)
        
        # Add person names as annotations
        for i, name in enumerate(self.people_data['name']):
            plt.annotate(name, (reduced_features[i, 0], reduced_features[i, 1]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.colorbar(scatter)
        plt.title('People Clustering Visualization (PCA)')
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def get_feature_importance(self, n_features: int = 10) -> List[Tuple[str, float]]:
        """
        Get the most important features (words) for clustering.
        
        Args:
            n_features: Number of top features to return
            
        Returns:
            List of tuples (feature_name, importance_score)
        """
        if self.feature_matrix is None:
            raise ValueError("No feature matrix available. Call add_people() first.")
        
        # Calculate feature importance as standard deviation across people
        feature_importance = np.std(self.feature_matrix, axis=0)
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Get top features
        top_indices = np.argsort(feature_importance)[::-1][:n_features]
        top_features = [(feature_names[i], feature_importance[i]) for i in top_indices]
        
        return top_features


def demo_example():
    """
    Demonstration of the PeopleNetworking system with sample data.
    """
    # Sample people with their preferences
    people_preferences = {
        "1": "I love reading books, especially science fiction and fantasy novels. I enjoy hiking and outdoor activities.",
        "2": "I'm passionate about technology, programming, and video games. I like sci-fi movies and board games.",
        "3": "I enjoy cooking, trying new recipes, and exploring different cuisines. I love traveling and photography.",
        "4": "I'm into fitness, yoga, and healthy living. I enjoy nature walks and meditation.",
        "5": "I love music, playing guitar, and going to concerts. I'm also interested in art and painting.",
        "5": "I'm a sports enthusiast, especially football and basketball. I enjoy watching games and playing fantasy sports.",
        "6": "I enjoy reading mystery novels and crime thrillers. I like solving puzzles and playing chess.",
        "7": "I'm passionate about cooking and experimenting with new flavors. I enjoy food photography and blogging.",
        "8": "I love outdoor adventures like hiking, camping, and rock climbing. I enjoy nature photography.",
        "8": "I'm interested in technology, artificial intelligence, and machine learning. I enjoy coding and building projects."
    }
    
    print("=== People Networking System Demo ===\n")
    
    # Initialize the system
    network = PeopleNetworking(max_features=500)
    
    # Add people and their preferences
    network.add_people(people_preferences)
    print(f"Added {len(people_preferences)} people to the system.\n")
    
    # Cluster people
    print("Clustering people into 3 groups...")
    clusters = network.cluster_people(n_clusters=3, method='kmeans')
    
    # # Display clusters
    # print("\nCluster assignments:")
    # for person, cluster_id in clusters.items():
    #     print(f"  {person}: Cluster {cluster_id}")
    
    # # Show cluster members
    # print("\nCluster members:")
    # for cluster_id in range(3):
    #     members = network.get_cluster_members(cluster_id)
    #     print(f"  Cluster {cluster_id}: {', '.join(members)}")
    
    # Find similar people for a specific person
    print(f"\nTop 3 people similar to Alice:")
    similar_to_alice = network.find_similar_people("3", k=3)
    for name, score in similar_to_alice:
        print(f"  {name}: {score:.3f}")
    
    # # Find top similar pairs
    # print(f"\nTop 5 most similar pairs:")
    # similar_pairs = network.find_top_k_similar_pairs(k=5)
    # for person1, person2, score in similar_pairs:
    #     print(f"  {person1} ↔ {person2}: {score:.3f}")
    
    # # Show important features
    # print(f"\nTop 5 distinguishing features:")
    # features = network.get_feature_importance(n_features=5)
    # for feature, importance in features:
    #     print(f"  {feature}: {importance:.3f}")


# Utility functions for easy usage
def find_similar_people_simple(people_preferences: Dict[str, str], 
                              target_person: str, 
                              k: int = 5) -> List[Tuple[str, float]]:
    """
    Simple function to find similar people without creating a class instance.
    
    Args:
        people_preferences: Dictionary mapping person names to preferences
        target_person: Name of the person to find similarities for
        k: Number of similar people to return
        
    Returns:
        List of tuples (person_name, similarity_score)
    """
    network = PeopleNetworking()
    network.add_people(people_preferences)
    return network.find_similar_people(target_person, k)


def cluster_people_simple(people_preferences: Dict[str, str], 
                         n_clusters: int = 3) -> Dict[str, int]:
    """
    Simple function to cluster people without creating a class instance.
    
    Args:
        people_preferences: Dictionary mapping person names to preferences
        n_clusters: Number of clusters to create
        
    Returns:
        Dictionary mapping person names to cluster labels
    """
    network = PeopleNetworking()
    network.add_people(people_preferences)
    return network.cluster_people(n_clusters)


if __name__ == "__main__":
    demo_example()
