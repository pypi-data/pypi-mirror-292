# Intelligent Chunking of Japanese PDFs using Language Models, MeCab, and Janome

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Dependencies](#dependencies)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Function Descriptions](#function-descriptions)
7. [Clustering and Chunking Process](#clustering-and-chunking-process)
8. [Examples](#examples)
9. [Customization Options](#customization-options)
10. [Output](#output)
11. [Notes](#notes)
12. [Troubleshooting](#troubleshooting)
13. [License](#license)

## Introduction

### Background

The increasing volume of digital documents, particularly in PDF format, has created a need for efficient and intelligent document processing systems. For languages like Japanese, which lack clear word boundaries and have complex writing systems, traditional chunking methods often fall short. This white paper introduces a novel approach that combines the power of Language Models with Japanese-specific tools to overcome these challenges.

### Existing Problems

Current document processing systems face several challenges when dealing with Japanese PDFs:

1. **Lack of clear word boundaries**: Unlike languages that use spaces to separate words, Japanese text flows continuously, making it difficult for standard tokenization methods to identify word boundaries accurately.

2. **Complex writing system**: Japanese uses a mixture of kanji (logographic characters), hiragana, and katakana, making it challenging for non-specialized systems to process.

3. **Context-dependent meaning**: The meaning of Japanese characters can change significantly based on context, which is difficult for simple chunking algorithms to account for.

4. **PDF format complexities**: Extracting clean, structured text from PDFs can be challenging, especially with complex layouts or when dealing with scanned documents.

5. **Semantic coherence**: Existing chunking methods often break documents into fixed-size chunks without considering semantic boundaries, potentially splitting related content across different chunks.

6. **Scalability issues**: Processing large documents can be computationally expensive, especially when using advanced NLP techniques.

7. **Inconsistent formatting**: Japanese documents may mix vertical and horizontal text, further complicating the extraction and chunking process.

### Proposed Solution

This Python script presents an innovative approach to chunking Japanese PDF documents using a combination of advanced natural language processing techniques. The method leverages Large Language Models (LLMs), MeCab (a morphological analyzer for Japanese), and clustering algorithms to create semantically meaningful and size-appropriate chunks from Japanese text. This approach addresses several challenges in processing Japanese documents, particularly in the context of large language models and document analysis systems.

## Features

- Extracts text from PDF files with page number information
- Preprocesses and tokenizes text using both MeCab and Janome (optimized for Japanese)
- Generates embeddings for text chunks using a multilingual Sentence Transformer model
- Clusters text using K-means algorithm with combined embedding and TF-IDF features
- Creates intelligent chunks based on word count, semantic similarity, and sentence boundaries
- Optionally processes chunks using a Language Model for cleaning and proofreading
- Saves both raw and processed chunks with metadata (PDF name, page numbers, cluster, word count)
- Handles both Japanese and non-Japanese text

## Dependencies

- os
- re
- json
- time
- MeCab
- torch
- PyPDF2
- logging
- unicodedata
- numpy
- kneed
- dotenv
- functools
- sklearn
- langchain_ibm
- janome
- sentence_transformers
- ibm_watson_machine_learning

## Installation

You can install J-Chunker using pip:

```bash
pip install j_chunker
```

## Usage

Here's a basic example of how to use J-Chunker:

```python
from j_chunker import chunker
import os

pdf_paths = ["path/to/your/japanese.pdf"]
output_dir = os.getenv("OUTPUT_DIR", "output")
raw_dir = os.path.join(output_dir, "raw")
processed_dir = os.path.join(output_dir, "processed")

embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

chunks = chunker(pdf_paths, output_dir, raw_dir, processed_dir, embedding_model_name, max_words=1024, llm_summarize=False, visualize=True)

print(chunks)
```

### Parameters:

- `pdf_paths`: List of paths to PDF files to process
- `output_dir`: Directory to save output files
- `raw_dir`: Directory to save raw chunks
- `processed_dir`: Directory to save processed chunks
- `embedding_model_name`: Name of the Sentence Transformers model to use for embeddings
- `max_words`: Maximum number of words per chunk (default: 500)
- `llm_summarize`: Whether to use LLM for summarization (default: False)
- `visualize`: Whether to visualize the clusters (default: True)

## Environment Variables

J-Chunker uses the following environment variables:

- `OUTPUT_DIR`: Directory for output files (default: "output")
- `EMBEDDING_MODEL_NAME`: Name of the Sentence Transformers model (default: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

For LLM summarization (when enabled):
- `MODEL_NAME`: LLM model name
- `IBM_CLOUD_URL`: IBM Cloud URL
- `IBM_CLOUD_API_KEY`: IBM Cloud API key
- `PROJECT_ID`: Project ID for IBM Watson

You can set these variables in your environment or use a `.env` file.

## Function Descriptions

### `initialize_model()`

Initializes and returns a WatsonxLLM model with specified parameters.

**Example:**
```python
llm = initialize_model(temperature=0.2, max_new_tokens=1024)
```

### `extract_text_from_pdf(pdf_path)`

Extracts text content from a PDF file, along with page numbers.

**Example:**
```python
pages = extract_text_from_pdf("data/example.pdf")
print(f"Extracted {len(pages)} pages from the PDF")
```

### `preprocess_document(pages, tagger)`

Preprocesses the extracted text by tokenizing, lemmatizing, and generating n-grams.

**Example:**
```python
paragraphs, tokenized_paragraphs, lemmatized_paragraphs, ngrams, page_numbers = preprocess_document(pages, tagger)
print(f"Created {len(paragraphs)} paragraphs")
```

### `generate_embeddings(lemmatized_paragraphs, model)`

Generates embeddings for lemmatized paragraphs using a Sentence Transformer model.

**Example:**
```python
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
embeddings = generate_embeddings(lemmatized_paragraphs, model)
print(f"Generated embeddings shape: {embeddings.shape}")
```

### `find_optimal_clusters(embeddings, max_clusters=10)`

Finds the optimal number of clusters using the elbow method.

**Example:**
```python
optimal_clusters = find_optimal_clusters(embeddings, max_clusters=15)
print(f"Optimal number of clusters: {optimal_clusters}")
```

### `cluster_paragraphs(embeddings, lemmatized_paragraphs, max_clusters=20)`

Clusters paragraphs using K-means on combined embeddings and TF-IDF features.

**Example:**
```python
clusters = cluster_paragraphs(embeddings, lemmatized_paragraphs, max_clusters=15)
print(f"Assigned {len(set(clusters))} clusters")
```

### `sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words=1000)`

Chunks the document into smaller parts based on word count, cluster boundaries, and sentence integrity.

**Example:**
```python
chunks = sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words=800)
print(f"Created {len(chunks)} chunks")
```

### `clean_chunk(text)`

Cleans the processed chunk by removing unwanted patterns and formatting.

**Example:**
```python
cleaned_text = clean_chunk("This is a sample text... with some   extra spaces.")
print(f"Cleaned text: {cleaned_text}")
```

### `save_chunks_to_json(chunks, pdf_name, output_file)`

Saves document chunks to a JSON file.

**Example:**
```python
save_chunks_to_json(chunks, "example_pdf", "output/raw/example_chunks.json")
```

### `process_chunk_with_llm(chunk, llm, max_words)`

Processes a single chunk of text using the LLM for proofreading and cleaning.

**Example:**
```python
llm = initialize_model()
processed_chunk = process_chunk_with_llm(chunk, llm, max_words=500)
print(f"Processed chunk: {processed_chunk['content'][:100]}...")
```

### `process_single_pdf(pdf_path, model, tagger, max_words=500)`

Processes a single PDF file: extracts text, preprocesses, generates embeddings, clusters, and chunks.

**Example:**
```python
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
tagger = MeCab.Tagger()
chunks, pdf_name = process_single_pdf("data/example.pdf", model, tagger, max_words=600)
print(f"Processed PDF: {pdf_name}, created {len(chunks)} chunks")
```

### `process_and_clean_chunks(chunks, pdf_name, output_file, max_words, llm_summarize=False)`

Processes and optionally cleans all chunks using the LLM, then saves the results to a JSON file.

**Example:**
```python
process_and_clean_chunks(chunks, "example_pdf", "output/processed/example_processed.json", max_words=500, llm_summarize=True)
```

### `chunker(pdf_paths, output_dir, raw_dir, processed_dir, max_words=500, llm_summarize=False)`

Processes multiple PDF files: extracts text, preprocesses, generates embeddings, clusters, chunks, and optionally cleans.

**Example:**
```python
pdf_paths = ["data/file1.pdf", "data/file2.pdf"]
chunker(pdf_paths, "output", "output/raw", "output/processed", max_words=600, llm_summarize=True)
```

## Clustering and Chunking Process

### Clustering Process

1. **Generate Embeddings**: 
   Each paragraph is converted into a numerical vector using a multilingual Sentence Transformer model. These embeddings are dense vector representations of text that capture semantic meaning, allowing the computer to understand and compare the content of different paragraphs in a high-dimensional space.

2. **Create TF-IDF Features**: 
   TF-IDF (Term Frequency-Inverse Document Frequency) vectors are created for each paragraph to capture important terms. This numerical statistic reflects how important a word is to a document in a collection, complementing the semantic information from embeddings with information about word importance and uniqueness.

3. **Combine Features**: 
   Embeddings and TF-IDF features are combined for a richer representation. This combination allows the clustering algorithm to consider both semantic similarity and important term frequency when grouping paragraphs.

4. **Find Optimal Number of Clusters**: 
   The script uses the elbow method to determine the optimal number of clusters. This technique plots the explained variance as a function of the number of clusters and picks the elbow of the curve as the optimal number, automatically deciding how many distinct groups the paragraphs should be divided into.

5. **K-means Clustering**: 
   The script groups similar paragraphs based on their combined features using the K-means algorithm. This unsupervised machine learning method iteratively assigns each paragraph to the nearest cluster center and then recalculates the center based on the assigned paragraphs.

6. **Assign Cluster Labels**: 
   Each paragraph receives a cluster label, which is essentially a group identifier. These labels are used later in the chunking process to ensure that semantically related content stays together.

### Chunking Process

1. **Group by Cluster**: 
   Paragraphs are grouped according to their assigned cluster labels. This step ensures that semantically similar content is kept together in the subsequent chunking process.

2. **Sentence Splitting**: 
   Each paragraph is divided into individual sentences. This granular approach allows for more precise control over the content of each chunk and helps maintain the integrity of sentences.

3. **Word Counting**: 
   The script counts words in each sentence, using Janome for Japanese text and simple splitting for non-Japanese text. Janome, a morphological analyzer, can accurately count words in Japanese text. This step is crucial for controlling the size of the chunks.

4. **Chunk Creation**: 
   Chunks are created by adding sentences until the word limit is reached, respecting cluster boundaries. This approach balances the need for consistent chunk sizes with the goal of maintaining semantic coherence within each chunk.

5. **Metadata Tracking**: 
   The script tracks page numbers, cluster, and word count for each chunk. This metadata is valuable for understanding the document structure and for potential downstream tasks.

This combined process of clustering and chunking allows for the intelligent division of documents into semantically coherent, manageable pieces. It's particularly useful for processing long documents or for preparing text for further natural language processing tasks, as it maintains context and meaning while creating consistently sized text chunks.

## Examples

Let's walk through detailed examples of the entire process, including clustering outputs, for both Japanese and English texts.

### Japanese Example

Consider this Japanese text:

```python
japanese_text = """
東京は日本の首都です。人口が多く、経済の中心地でもあります。
東京には多くの観光名所があります。例えば、東京タワーやスカイツリーがあります。
日本の文化は独特です。茶道や歌舞伎などの伝統文化が今も息づいています。
日本料理も人気があります。寿司や天ぷらは世界中で愛されています。
日本の技術も有名です。家電製品や自動車など、高品質な製品を作っています。
"""

# Step 1: Preprocess the text
tagger = MeCab.Tagger()
paragraphs = japanese_text.split('\n')
paragraphs = [p for p in paragraphs if p.strip()]
_, _, lemmatized_paragraphs, _, page_numbers = preprocess_document([(1, p) for p in paragraphs], tagger)

print("Lemmatized paragraphs:")
for i, para in enumerate(lemmatized_paragraphs, 1):
    print(f"{i}. {para}")
print("-" * 50)

# Step 2: Generate embeddings
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
embeddings = generate_embeddings(lemmatized_paragraphs, model)

print(f"Embeddings shape: {embeddings.shape}")
print("-" * 50)

# Step 3: Cluster paragraphs
clusters = cluster_paragraphs(embeddings, lemmatized_paragraphs, max_clusters=3)

print("Clustering results:")
for i, (para, cluster) in enumerate(zip(paragraphs, clusters), 1):
    print(f"Paragraph {i} (Cluster {cluster}):")
    print(para)
    print()
print("-" * 50)

# Step 4: Create chunks
chunks = sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words=50)

print("Generated chunks:")
for chunk in chunks:
    print(f"Cluster: {chunk['cluster']}, Pages: {chunk['pages']}")
    print(f"Content: {chunk['content']}")
    print(f"Word count: {chunk['word_count']}")
    print("-" * 50)
```

Output:
```
Lemmatized paragraphs:
1. 東京 日本 首都 です 人口 多い 経済 中心 地 です
2. 東京 多く 観光 名所 あり ます 例えば 東京タワー スカイツリー あり ます
3. 日本 文化 独特 です 茶道 歌舞伎 など 伝統 文化 今 息づく て い ます
4. 日本 料理 人気 あり ます 寿司 天ぷら 世界 中 愛す られる て い ます
5. 日本 技術 有名 です 家電 製品 自動車 など 高 品質 製品 作る て い ます
--------------------------------------------------
Embeddings shape: (5, 384)
--------------------------------------------------
Clustering results:
Paragraph 1 (Cluster 0):
東京は日本の首都です。人口が多く、経済の中心地でもあります。

Paragraph 2 (Cluster 0):
東京には多くの観光名所があります。例えば、東京タワーやスカイツリーがあります。

Paragraph 3 (Cluster 1):
日本の文化は独特です。茶道や歌舞伎などの伝統文化が今も息づいています。

Paragraph 4 (Cluster 1):
日本料理も人気があります。寿司や天ぷらは世界中で愛されています。

Paragraph 5 (Cluster 2):
日本の技術も有名です。家電製品や自動車など、高品質な製品を作っています。

--------------------------------------------------
Generated chunks:
Cluster: 0, Pages: 1
Content: 東京は日本の首都です。人口が多く、経済の中心地でもあります。東京には多くの観光名所があります。例えば、東京タワーやスカイツリーがあります。
Word count: 36
--------------------------------------------------
Cluster: 1, Pages: 1
Content: 日本の文化は独特です。茶道や歌舞伎などの伝統文化が今も息づいています。日本料理も人気があります。寿司や天ぷらは世界中で愛されています。
Word count: 35
--------------------------------------------------
Cluster: 2, Pages: 1
Content: 日本の技術も有名です。家電製品や自動車など、高品質な製品を作っています。
Word count: 19
--------------------------------------------------
```

### English Example

Now, let's look at an English text:

```python
english_text = """
Artificial Intelligence (AI) is revolutionizing various industries.
Machine Learning, a subset of AI, enables computers to learn from data.
Natural Language Processing allows machines to understand human language.
Computer Vision is another important field in AI, focusing on image recognition.
These AI technologies are being applied in healthcare, finance, and transportation.
"""

# Step 1: Preprocess the text
paragraphs = english_text.split('\n')
paragraphs = [p for p in paragraphs if p.strip()]
_, _, lemmatized_paragraphs, _, page_numbers = preprocess_document([(1, p) for p in paragraphs], tagger)

print("Lemmatized paragraphs:")
for i, para in enumerate(lemmatized_paragraphs, 1):
    print(f"{i}. {para}")
print("-" * 50)

# Step 2: Generate embeddings
embeddings = generate_embeddings(lemmatized_paragraphs, model)

print(f"Embeddings shape: {embeddings.shape}")
print("-" * 50)

# Step 3: Cluster paragraphs
clusters = cluster_paragraphs(embeddings, lemmatized_paragraphs, max_clusters=3)

print("Clustering results:")
for i, (para, cluster) in enumerate(zip(paragraphs, clusters), 1):
    print(f"Paragraph {i} (Cluster {cluster}):")
    print(para)
    print()
print("-" * 50)

# Step 4: Create chunks
chunks = sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words=50)

print("Generated chunks:")
for chunk in chunks:
    print(f"Cluster: {chunk['cluster']}, Pages: {chunk['pages']}")
    print(f"Content: {chunk['content']}")
    print(f"Word count: {chunk['word_count']}")
    print("-" * 50)
```

Output:
```
Lemmatized paragraphs:
1. Artificial Intelligence ( AI ) is revolutionizing various industries .
2. Machine Learning , a subset of AI , enables computers to learn from data .
3. Natural Language Processing allows machines to understand human language .
4. Computer Vision is another important field in AI , focusing on image recognition .
5. These AI technologies are being applied in healthcare , finance , and transportation .
--------------------------------------------------
Embeddings shape: (5, 384)
--------------------------------------------------
Clustering results:
Paragraph 1 (Cluster 0):
Artificial Intelligence (AI) is revolutionizing various industries.

Paragraph 2 (Cluster 0):
Machine Learning, a subset of AI, enables computers to learn from data.

Paragraph 3 (Cluster 1):
Natural Language Processing allows machines to understand human language.

Paragraph 4 (Cluster 1):
Computer Vision is another important field in AI, focusing on image recognition.

Paragraph 5 (Cluster 2):
These AI technologies are being applied in healthcare, finance, and transportation.

--------------------------------------------------
Generated chunks:
Cluster: 0, Pages: 1
Content: Artificial Intelligence (AI) is revolutionizing various industries. Machine Learning, a subset of AI, enables computers to learn from data.
Word count: 18
--------------------------------------------------
Cluster: 1, Pages: 1
Content: Natural Language Processing allows machines to understand human language. Computer Vision is another important field in AI, focusing on image recognition.
Word count: 19
--------------------------------------------------
Cluster: 2, Pages: 1
Content: These AI technologies are being applied in healthcare, finance, and transportation.
Word count: 11
--------------------------------------------------
```

### Interpreting the Clustering Results

In both examples, we can observe how the clustering algorithm groups similar paragraphs:

1. **Japanese Example**:
   - Cluster 0: Paragraphs about Tokyo (general information and tourist attractions)
   - Cluster 1: Paragraphs about Japanese culture and cuisine
   - Cluster 2: Paragraph about Japanese technology

2. **English Example**:
   - Cluster 0: General AI and Machine Learning
   - Cluster 1: Specific AI fields (Natural Language Processing and Computer Vision)
   - Cluster 2: Applications of AI technologies

The clustering helps to group thematically similar content together, which is then reflected in the generated chunks. This approach ensures that related information is kept together, improving the coherence of each chunk.

Note that the exact cluster numbers may vary between runs due to the nature of the K-means algorithm, but the grouping of similar content should remain consistent.

### Visualizing Embeddings (Optional)

For a more in-depth understanding of how the clustering works, you can visualize the embeddings using dimensionality reduction techniques like t-SNE, UMAP or PCA. Here's an example using PCA:

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from umap import UMAP
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
    elif method == 'umap':
        reducer = UMAP(n_components=2, random_state=42)
        method_name = 'UMAP'
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

# Example usage:
# visualize_embeddings(embeddings, clusters, pdf_name="example.pdf", method='pca')
# visualize_embeddings(embeddings, clusters, pdf_name="example.pdf", method='tsne')
# visualize_embeddings(embeddings, clusters, pdf_name="example.pdf", method='umap')
```

This visualization can help you understand how the paragraphs are grouped in the embedding space and how well-separated the clusters are.

By examining these detailed outputs, you can gain insights into how the clustering process works and how it affects the final chunking of the document. This information can be valuable for fine-tuning the process or for understanding why certain chunks are created the way they are.

## Customization Options

### Clustering Customization

Adjust the maximum number of clusters to consider:

```python
clusters = cluster_paragraphs(embeddings, lemmatized_paragraphs, max_clusters=25)
```

### Chunking Customization

Modify the maximum words per chunk:

```python
chunks = sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words=1500)
```

### Embedding Model Customization

Change the embedding model:

```python
model = SentenceTransformer('different-multilingual-model')
```

### LLM Processing Customization

Enable or disable LLM processing and adjust parameters:

```python
chunker(pdf_paths, output_dir, raw_dir, processed_dir, max_words=600, llm_summarize=True)
```

## Output

The script generates two types of output for each processed PDF:

1. Raw chunks: `output/raw/{pdf_name}_raw.json`
2. Processed chunks: `output/processed/{pdf_name}_processed.json`

Example of the JSON structure:

```json
[
  {
    "chunk_id": 1,
    "content": "Processed and cleaned text content...",
    "pages": "1,2",
    "cluster": 0,
    "word_count": 250,
    "pdf_name": "example_pdf"
  },
  ...
]
```

## Notes

- The script is optimized for Japanese but can handle both Japanese and non-Japanese text.
- Processing time depends on the PDF size, the number of chunks created, and whether LLM processing is enabled.
- Adjust `max_words` in `chunker()` to control chunk size.
- The script uses a dynamic clustering approach, automatically determining the optimal number of clusters for each document.
- The combination of Sentence Transformer embeddings and TF-IDF features provides a rich representation for clustering, capturing both semantic and term-frequency information.
- The sentence-aware chunking process ensures that sentences are not split across chunks, maintaining readability and context.
- The use of both MeCab and Janome allows for flexible and accurate processing of Japanese text.
- The optional LLM-based post-processing step helps to clean and refine the chunks, potentially improving their quality for downstream tasks.
- For very large documents, consider implementing parallel processing to improve efficiency.
- Regular testing and validation are recommended, especially when processing documents from new domains or with different structures.
- The script now uses a multilingual Sentence Transformer model, which can handle both Japanese and non-Japanese text effectively.
- The `clean_chunk` function has been updated to handle both Japanese and non-Japanese text, preserving important characters and formatting.

## Advanced Usage

### Handling Mixed-Language Documents

The script can handle documents containing multiple languages. Here's an example of processing a mixed-language text:

```python
mixed_text = """
日本の技術革新は世界をリードしています。
Many Japanese companies are at the forefront of AI and robotics.
自動運転車の開発は、トヨタやホンダなどが積極的に取り組んでいます。
The integration of AI in daily life is more prevalent in Japan than in many other countries.
"""

# Preprocess and chunk the mixed-language text
paragraphs = mixed_text.split('\n')
paragraphs = [p for p in paragraphs if p.strip()]
_, _, lemmatized_paragraphs, _, page_numbers = preprocess_document([(1, p) for p in paragraphs], tagger)
embeddings = generate_embeddings(lemmatized_paragraphs, model)
clusters = cluster_paragraphs(embeddings, lemmatized_paragraphs, max_clusters=2)
chunks = sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words=100)

for chunk in chunks:
    print(f"Cluster: {chunk['cluster']}, Content: {chunk['content']}")
```

### Fine-tuning for Specific Domains

If you're working with documents from a specific domain (e.g., legal, medical, technical), you may want to fine-tune the process:

1. Use a domain-specific embedding model if available.
2. Adjust the `clean_chunk` function to preserve domain-specific terminology.
3. Modify the LLM prompts to include domain-specific instructions.

Example of modifying the `clean_chunk` function for legal documents:

```python
def clean_chunk_legal(text):
    # Add legal-specific cleaning rules
    legal_terms = ['原告', '被告', '判決', 'plaintiff', 'defendant', 'verdict']
    for term in legal_terms:
        text = text.replace(f" {term} ", f" {term}")  # Ensure legal terms are not split
    # ... (rest of the cleaning process)
    return text
```

### LLM Summarization

To use LLM-based summarization, you need to set up the necessary environment variables and set `llm_summarize=True`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure these environment variables are set in your .env file:
# MODEL_NAME
# IBM_CLOUD_URL
# IBM_CLOUD_API_KEY
# PROJECT_ID

chunks = chunker(pdf_paths, output_dir, raw_dir, processed_dir, embedding_model_name, max_words=1024, llm_summarize=True)
```

## Troubleshooting

If you encounter issues, try the following:

1. **Embedding errors**: Ensure you have the latest version of the `sentence-transformers` library installed.
2. **MeCab errors**: Check that MeCab and its dictionary are properly installed and accessible.
3. **Memory issues**: For large documents, try processing them in smaller batches or increase your system's memory.
4. **LLM processing errors**: Verify your IBM Cloud credentials and network connection.

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the developers of MeCab, Janome, and the Sentence Transformers library.
- Special thanks to the IBM Watsonx team for providing the LLM capabilities.
