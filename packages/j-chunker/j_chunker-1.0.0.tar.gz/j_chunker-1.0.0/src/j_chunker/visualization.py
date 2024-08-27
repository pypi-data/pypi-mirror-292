# SPDX-License-Identifier: Apache-2.0
# Third Party
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from scipy.spatial import ConvexHull

def visualize_embeddings(embeddings, clusters, pdf_name=None, method='pca'):
    """
    Visualize embeddings using various dimensionality reduction techniques.
    
    Parameters:
    - embeddings: numpy array of shape (n_samples, n_features)
    - clusters: numpy array of cluster labels
    - pdf_name: str, optional name of the PDF file for the title
    - method: str, visualization method ('pca', 'tsne', or 'umap')
    """
    # Choose dimensionality reduction method
    if method == 'pca':
        reducer = PCA(n_components=2)
        method_name = 'PCA'
    elif method == 'tsne':
        reducer = TSNE(n_components=2, random_state=42)
        method_name = 't-SNE'
    else:
        raise ValueError("Invalid method. Choose 'pca', 'tsne', or 'umap'.")

    # Perform dimensionality reduction
    embeddings_2d = reducer.fit_transform(embeddings)
    
    # Create a new figure
    plt.figure(figsize=(12, 8))
    
    # Get unique clusters and assign colors
    unique_clusters = np.unique(clusters)
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_clusters)))
    
    # Plot each cluster
    for cluster, color in zip(unique_clusters, colors):
        mask = clusters == cluster
        plt.scatter(embeddings_2d[mask, 0], embeddings_2d[mask, 1], 
                    c=[color], label=f'Cluster {cluster}', alpha=0.7)
        
        # Plot centroid
        centroid = embeddings_2d[mask].mean(axis=0)
        plt.scatter(centroid[0], centroid[1], c=[color], s=200, marker='*', 
                    edgecolors='black', linewidth=1.5)
        
        # Plot convex hull
        if np.sum(mask) >= 3:  # Need at least 3 points for a hull
            hull = ConvexHull(embeddings_2d[mask])
            for simplex in hull.simplices:
                plt.plot(embeddings_2d[mask][simplex, 0], embeddings_2d[mask][simplex, 1], 
                         c=color, linestyle='--', alpha=0.5)
    
    # Add labels and title
    plt.xlabel(f'First {method_name} Component')
    plt.ylabel(f'Second {method_name} Component')
    title = f'Paragraph Embeddings Clustered ({method_name})'
    if pdf_name:
        title += f'\n{pdf_name}'
    plt.title(title)
    
    # Add legend
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Adjust layout and display
    plt.tight_layout()
    plt.show()
