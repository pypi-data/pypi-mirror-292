# SPDX-License-Identifier: Apache-2.0
# Standard
from typing import List

# Third Party
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from kneed import KneeLocator

def generate_embeddings(lemmatized_paragraphs: List[str], model) -> np.ndarray:
    """
    Generate embeddings for lemmatized paragraphs using Sentence Transformers.

    Args:
        lemmatized_paragraphs: List of lemmatized paragraphs.
        model: Initialized SentenceTransformer model.

    Returns:
        Array of embeddings for each paragraph.
    """
    return model.encode(lemmatized_paragraphs)

def find_optimal_clusters(embeddings: np.ndarray, max_clusters: int = 10) -> int:
    """
    Find the optimal number of clusters using the elbow method.

    Args:
        embeddings: Array of paragraph embeddings.
        max_clusters: Maximum number of clusters to consider.

    Returns:
        Optimal number of clusters.
    """
    n_samples = embeddings.shape[0]
    max_clusters = min(max_clusters, n_samples - 1)
    
    if max_clusters < 2:
        return 1
    
    inertias = [KMeans(n_clusters=k, random_state=42).fit(embeddings).inertia_
                for k in range(1, max_clusters + 1)]
    
    kneedle = KneeLocator(range(1, max_clusters + 1), inertias, curve='convex', direction='decreasing')
    optimal_clusters = kneedle.elbow or min(int(np.sqrt(n_samples)), 3)
    
    return optimal_clusters

def cluster_paragraphs(embeddings: np.ndarray, lemmatized_paragraphs: List[str], max_clusters: int = 20) -> np.ndarray:
    """
    Cluster paragraphs using K-means on embeddings and TF-IDF features.

    Args:
        embeddings: Array of paragraph embeddings.
        lemmatized_paragraphs: List of lemmatized paragraphs.
        max_clusters: Maximum number of clusters to consider.

    Returns:
        Array of cluster labels for each paragraph.
    """
    n_samples = len(lemmatized_paragraphs)
    
    if n_samples < 2:
        return np.zeros(n_samples, dtype=int)
    
    max_clusters = min(max_clusters, n_samples - 1)
    tfidf = TfidfVectorizer(max_features=min(100, n_samples))
    tfidf_features = tfidf.fit_transform(lemmatized_paragraphs)
    combined_features = np.hstack([embeddings, tfidf_features.toarray()])
    
    n_clusters = find_optimal_clusters(combined_features, max_clusters)
    
    return KMeans(n_clusters=n_clusters, random_state=42).fit_predict(combined_features)