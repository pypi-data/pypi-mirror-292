# SPDX-License-Identifier: Apache-2.0
# Standard
import os
import logging
from pathlib import Path
from typing import List, Dict

# Third Party
import MeCab
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# Local
from .visualization import visualize_embeddings
from .embedding import generate_embeddings, cluster_paragraphs
from .text_processing import extract_text_from_pdf, preprocess_document
from .utils import save_chunks_to_json, process_and_clean_chunks, sentence_aware_japanese_chunking

def chunker(
    pdf_paths: List[str],
    output_dir: str,
    raw_dir: str,
    processed_dir: str,
    embedding_model_name: str,
    max_words: int = 500,
    llm_summarize: bool = False,
    visualize: bool = True
) -> Dict[str, List[Dict]]:
    """
    Process multiple PDF files: extract text, preprocess, generate embeddings, cluster, and chunk.

    Args:
        pdf_paths: List of paths to PDF files.
        output_dir: Directory to save output files.
        raw_dir: Directory to save raw chunks.
        processed_dir: Directory to save processed chunks.
        embedding_model_name: Name of the Sentence Transformers model to use for embeddings.
        max_words: Maximum number of words per chunk.
        llm_summarize: Whether to use LLM for summarization.
        visualize: Visualize the clusters in a plot.

    Returns:
        A dictionary containing processed chunks for each PDF.
    """
    tagger = MeCab.Tagger()
    model = SentenceTransformer(embedding_model_name)
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    final_chunks = {}
    
    for pdf_path in tqdm(pdf_paths, desc="Processing PDFs"):
        try:
            logging.info(f"Processing: {pdf_path}")
            
            pages = extract_text_from_pdf(pdf_path)
            paragraphs, tokenized_paragraphs, lemmatized_paragraphs, ngrams, page_numbers = preprocess_document(pages, tagger)
            embeddings = generate_embeddings(lemmatized_paragraphs, model)
            clusters = cluster_paragraphs(embeddings, lemmatized_paragraphs)
            chunks = sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words)
            pdf_name = Path(pdf_path).stem
            
            if visualize:
                visualize_embeddings(embeddings=embeddings, clusters=clusters, pdf_name=pdf_name)
            
            raw_output_file = Path(raw_dir) / f"{pdf_name}_raw.json"
            processed_output_file = Path(processed_dir) / f"{pdf_name}_processed.json"
            
            save_chunks_to_json(chunks, pdf_name, raw_output_file)
            processed_chunks = process_and_clean_chunks(chunks, pdf_name, processed_output_file, max_words, llm_summarize)
            final_chunks[pdf_name] = processed_chunks
            
            logging.info(f"Completed processing: {pdf_path}")
            logging.info(f"Total chunks created: {len(chunks)}")

        except Exception as err:
            logging.error(f"Error processing {pdf_path}: {err}", exc_info=True)
    
    return final_chunks
