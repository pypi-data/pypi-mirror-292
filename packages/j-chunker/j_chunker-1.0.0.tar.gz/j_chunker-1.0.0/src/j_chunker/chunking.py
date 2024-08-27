# SPDX-License-Identifier: Apache-2.0
# Standard
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional

# Third Party
import MeCab
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# Local
from .llm import initialize_model
from .visualization import visualize_embeddings
from .embedding import generate_embeddings, cluster_paragraphs
from .text_processing import extract_text_from_pdf, preprocess_document
from .utils import save_chunks_to_json, process_and_clean_chunks, sentence_aware_japanese_chunking

def process_single_pdf(pdf_path, model, tagger, max_words=500, visualize=True):
    """
    Process a single PDF file: extract text, preprocess, generate embeddings, cluster, and chunk.

    Args:
        pdf_path (str): Path to the PDF file.
        tagger (MeCab.Tagger): Initialized MeCab tagger.
        max_words (int): Maximum number of words per chunk.
        visualize (bool): Visualize the clusters in a plot.

    Returns:
        tuple: A tuple containing the list of chunks and the PDF name.
    """
    pages = extract_text_from_pdf(pdf_path)
    paragraphs, tokenized_paragraphs, lemmatized_paragraphs, ngrams, page_numbers = preprocess_document(pages, tagger)
    embeddings = generate_embeddings(lemmatized_paragraphs, model)
    clusters = cluster_paragraphs(embeddings, lemmatized_paragraphs)
    chunks = sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    if visualize:
        visualize_embeddings(embeddings=embeddings, clusters=clusters, pdf_name=pdf_name)
    
    return chunks, pdf_name


def chunker(
    pdf_paths: List[str],
    output_dir: str,
    raw_dir: str,
    processed_dir: str,
    embedding_model_name: str,
    max_words: int = 500,
    llm_summarize: bool = False,
    visualize: bool = True,
    decoding_method: str = "greedy",
    max_new_tokens: int = 1024,
    min_new_tokens: int = 10,
    temperature: float = 0,
    top_k: int = 25,
    top_p: float = 1,
    stop_words: Optional[List[str]] = None
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
        decoding_method: Method used for decoding in the LLM.
        max_new_tokens: Maximum number of new tokens to generate in the LLM.
        min_new_tokens: Minimum number of new tokens to generate in the LLM.
        temperature: Sampling temperature for the LLM.
        top_k: Number of top tokens to consider for sampling in the LLM.
        top_p: Cumulative probability threshold for top-p sampling in the LLM.
        stop_words: List of stop words to end generation in the LLM.

    Returns:
        A dictionary containing processed chunks for each PDF.
    """
    tagger = MeCab.Tagger()
    model = SentenceTransformer(embedding_model_name)
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    final_chunks = {}

    if llm_summarize:
        llm = initialize_model(
            decoding_method=decoding_method,
            max_new_tokens=max_new_tokens,
            min_new_tokens=min_new_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            stop_words=stop_words if stop_words else ["\n\n\n"]
        )
    else:
        llm = None
    
    for pdf_path in tqdm(pdf_paths, desc="Processing PDFs"):
        try:
            logging.info(f"Processing: {pdf_path}")
            
            chunks, pdf_name = process_single_pdf(pdf_path, model, tagger, max_words, visualize)
            
            raw_output_file = Path(raw_dir) / f"{pdf_name}_raw.json"
            processed_output_file = Path(processed_dir) / f"{pdf_name}_processed.json"
            
            save_chunks_to_json(chunks, pdf_name, raw_output_file)
            processed_chunks = process_and_clean_chunks(chunks, pdf_name, processed_output_file, max_words, llm_summarize, llm)
            final_chunks[pdf_name] = processed_chunks
            
            logging.info(f"Completed processing: {pdf_path}")
            logging.info(f"Total chunks created: {len(chunks)}")

        except Exception as err:
            logging.error(f"Error processing {pdf_path}: {err}", exc_info=True)
    
    return final_chunks
