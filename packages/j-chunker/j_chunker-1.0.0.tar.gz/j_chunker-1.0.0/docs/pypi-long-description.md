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

## LLM Processing

When `llm_summarize` is set to `True`, J-Chunker uses a Large Language Model (LLM) to process and refine the text chunks. This feature provides several benefits:

1. **Text Cleaning**: The LLM can correct minor grammatical errors and improve the overall readability of the text.
2. **Summarization**: For longer chunks, the LLM can provide a concise summary, making it easier to grasp the main points quickly.
3. **Consistency**: The LLM can help maintain a consistent style and tone across all chunks.
4. **Terminology Standardization**: In technical or specialized documents, the LLM can ensure that terminology is used consistently throughout the text.

### Customizing LLM Parameters

J-Chunker allows you to customize the LLM parameters through the `chunker` function. Here's an example of how to use custom LLM parameters:

```python
from j_chunker import chunker
import os

pdf_paths = ["path/to/your/japanese.pdf"]
output_dir = os.getenv("OUTPUT_DIR", "output")
raw_dir = os.path.join(output_dir, "raw")
processed_dir = os.path.join(output_dir, "processed")

embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

chunks = chunker(
    pdf_paths,
    output_dir,
    raw_dir,
    processed_dir,
    embedding_model_name,
    max_words=1024,
    llm_summarize=True,
    visualize=True,
    decoding_method="sample",
    max_new_tokens=2048,
    min_new_tokens=20,
    temperature=0.7,
    top_k=50,
    top_p=0.95,
    stop_words=["\n\n\n", "END"]
)

print(chunks)
```

In this example, we're customizing several LLM parameters:

- `decoding_method`: Set to "sample" for more varied outputs.
- `max_new_tokens`: Increased to 2048 to allow for longer summaries.
- `min_new_tokens`: Set to 20 to ensure a minimum summary length.
- `temperature`: Increased to 0.7 for more creative outputs.
- `top_k`: Set to 50 to consider more token options during generation.
- `top_p`: Slightly reduced to 0.95 for more focused sampling.
- `stop_words`: Added "END" as an additional stop word.

These parameters allow you to fine-tune the LLM's behavior to best suit your specific use case. For example, increasing the temperature can lead to more diverse summaries, while adjusting the `max_new_tokens` can control the length of the generated content.

### LLM Setup

To use the LLM feature, you need to set up the necessary environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure these environment variables are set in your .env file:
# MODEL_NAME
# IBM_CLOUD_URL
# IBM_CLOUD_API_KEY
# PROJECT_ID
```

Note that using the LLM feature may increase processing time and requires additional setup for API access.

## Examples

### Processing a Japanese PDF

Let's say you have a Japanese PDF file named `japanese_document.pdf` with the following content:

```
東京は日本の首都です。人口が多く、経済の中心地でもあります。
東京には多くの観光名所があります。例えば、東京タワーやスカイツリーがあります。
日本の文化は独特です。茶道や歌舞伎などの伝統文化が今も息づいています。
日本料理も人気があります。寿司や天ぷらは世界中で愛されています。
日本の技術も有名です。家電製品や自動車など、高品質な製品を作っています。
```

You can process this PDF using J-Chunker as follows:

```python
from j_chunker import process_single_pdf
from sentence_transformers import SentenceTransformer
import MeCab

pdf_path = "path/to/japanese_document.pdf"
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
tagger = MeCab.Tagger()

chunks, pdf_name = process_single_pdf(pdf_path, model, tagger, max_words=50)

for chunk in chunks:
    print(f"Cluster: {chunk['cluster']}, Pages: {chunk['pages']}")
    print(f"Content: {chunk['content'][:50]}...")
    print(f"Word count: {chunk['word_count']}")
    print("-" * 50)
```

Output:
```
Cluster: 0, Pages: 1
Content: 東京は日本の首都です。人口が多く、経済の中心地でもあります。東京には多くの観光名所があります。...
Word count: 36
--------------------------------------------------
Cluster: 1, Pages: 1
Content: 日本の文化は独特です。茶道や歌舞伎などの伝統文化が今も息づいています。日本料理も人気があります。...
Word count: 35
--------------------------------------------------
Cluster: 2, Pages: 1
Content: 日本の技術も有名です。家電製品や自動車など、高品質な製品を作っています。
Word count: 19
--------------------------------------------------
```

### Processing an English PDF

J-Chunker can also handle non-Japanese text. Let's process an English PDF named `english_document.pdf` with the following content:

```
Artificial Intelligence (AI) is revolutionizing various industries.
Machine Learning, a subset of AI, enables computers to learn from data.
Natural Language Processing allows machines to understand human language.
Computer Vision is another important field in AI, focusing on image recognition.
These AI technologies are being applied in healthcare, finance, and transportation.
```

Process this PDF using the same method:

```python
pdf_path = "path/to/english_document.pdf"
chunks, pdf_name = process_single_pdf(pdf_path, model, tagger, max_words=30)

for chunk in chunks:
    print(f"Cluster: {chunk['cluster']}, Pages: {chunk['pages']}")
    print(f"Content: {chunk['content'][:50]}...")
    print(f"Word count: {chunk['word_count']}")
    print("-" * 50)
```

Output:
```
Cluster: 0, Pages: 1
Content: Artificial Intelligence (AI) is revolutionizing various industries. Machine Learning, a subset of AI, enables computers to learn from data...
Word count: 18
--------------------------------------------------
Cluster: 1, Pages: 1
Content: Natural Language Processing allows machines to understand human language. Computer Vision is another important field in AI, focusing on image recognition...
Word count: 19
--------------------------------------------------
Cluster: 2, Pages: 1
Content: These AI technologies are being applied in healthcare, finance, and transportation.
Word count: 11
--------------------------------------------------
```

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

## Notes

- Optimized for Japanese but can handle both Japanese and non-Japanese text
- Processing time depends on PDF size, number of chunks, and whether LLM processing is enabled
- Uses dynamic clustering to automatically determine the optimal number of clusters
- Combines Sentence Transformer embeddings and TF-IDF features for rich text representation
- Ensures sentences are not split across chunks, maintaining readability and context
- Visualization is set to True by default, but it won't work on systems without a display (e.g., headless Linux servers). If you're running J-Chunker on such a system, set `visualize=False` when calling the `chunker` function to avoid errors.

## License

This project is licensed under the Apache 2.0 License. See the LICENSE file for details.

For more detailed information, examples, and troubleshooting tips, please refer to the full documentation on the project's GitHub page.
