# J-Chunker: Intelligent Chunking of Japanese PDFs

J-Chunker is a Python package that provides intelligent chunking of Japanese PDF documents using advanced natural language processing techniques. It leverages Large Language Models (LLMs), MeCab, Janome, and clustering algorithms to create semantically meaningful and size-appropriate chunks from Japanese text.

## Features

- Extracts text from PDF files with page number information
- Preprocesses and tokenizes text using both MeCab and Janome (optimized for Japanese)
- Generates embeddings for text chunks using a multilingual Sentence Transformer model
- Clusters text using K-means algorithm with combined embedding and TF-IDF features
- Creates intelligent chunks based on word count, semantic similarity, and sentence boundaries
- Optionally processes chunks using a Language Model for cleaning and proofreading
- Saves both raw and processed chunks with metadata (PDF name, page numbers, cluster, word count)
- Handles both Japanese and non-Japanese text

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

## Key Components

1. **Text Extraction**: Extracts text from PDF files while preserving page information.
2. **Preprocessing**: Tokenizes and lemmatizes text using MeCab and Janome, optimized for Japanese language processing.
3. **Embedding Generation**: Creates dense vector representations of text chunks using a multilingual Sentence Transformer model.
4. **Clustering**: Groups similar paragraphs using K-means clustering on combined embedding and TF-IDF features.
5. **Intelligent Chunking**: Creates chunks based on word count, cluster boundaries, and sentence integrity.
6. **Optional LLM Processing**: Can use Language Models for additional cleaning and proofreading of chunks.

## Customization Options

- Adjust clustering parameters (e.g., maximum number of clusters)
- Modify chunk size (maximum words per chunk)
- Change the embedding model
- Enable or disable LLM processing

## Output

The package generates two types of output for each processed PDF:

1. Raw chunks: `output/raw/{pdf_name}_raw.json`
2. Processed chunks: `output/processed/{pdf_name}_processed.json`

## Advanced Usage

- Handles mixed-language documents
- Can be fine-tuned for specific domains (e.g., legal, medical, technical)
- Supports LLM-based summarization (requires additional setup)

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

## Notes

- Optimized for Japanese but can handle both Japanese and non-Japanese text
- Processing time depends on PDF size, number of chunks, and whether LLM processing is enabled
- Uses dynamic clustering to automatically determine the optimal number of clusters
- Combines Sentence Transformer embeddings and TF-IDF features for rich text representation
- Ensures sentences are not split across chunks, maintaining readability and context

## License

This project is licensed under the Apache 2.0 License. See the LICENSE file for details.

For more detailed information, examples, and troubleshooting tips, please refer to the full documentation on the project's GitHub page.
