# SPDX-License-Identifier: Apache-2.0
# Standard
import json
import logging
import re
import unicodedata
from typing import List, Dict
from pathlib import Path

# Third Party
from tqdm import tqdm

# Local
from .text_processing import is_japanese, count_words, split_into_sentences

def save_chunks_to_json(chunks: List[Dict], pdf_name: str, output_file: Path):
    """
    Save document chunks to a JSON file.

    Args:
        chunks: List of document chunks.
        pdf_name: Name of the PDF file.
        output_file: Path to the output JSON file.
    """
    chunk_data = [
        {
            "chunk_id": i,
            "content": chunk['content'],
            "pages": chunk['pages'],
            "cluster": int(chunk['cluster']),
            "pdf_name": pdf_name
        } for i, chunk in enumerate(chunks, 1)
    ]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunk_data, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Chunks have been saved to {output_file}")

def clean_chunk(text: str) -> str:
    """
    Clean the processed chunk by removing unwanted patterns and formatting,
    retaining Japanese (including kanji, hiragana, and katakana), English words,
    numbers, and essential punctuation.

    Args:
        text: The text chunk to clean.

    Returns:
        The cleaned text chunk.
    """
    def should_retain(char):
        return (unicodedata.category(char).startswith('L') or
                unicodedata.category(char).startswith('N') or
                char in '。、.,!?：:;()（）[]「」『』')

    # Clean the text
    cleaned_text = ''.join(char if should_retain(char) else ' ' for char in text)
    
    # Remove multiple spaces and trim
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    # Remove spaces before Japanese punctuation
    cleaned_text = re.sub(r'\s([。、！？：；）］」』])', r'\1', cleaned_text)
    
    # Remove spaces after opening brackets
    cleaned_text = re.sub(r'([（［「『])\s', r'\1', cleaned_text)
    
    # Remove isolated punctuation marks
    cleaned_text = re.sub(r'\s([.,!?：:;])\s', ' ', cleaned_text)
    
    # Handle specific patterns
    cleaned_text = re.sub(r'([。、.,!?：:;])\1+', r'\1', cleaned_text)  # Remove repeated punctuation
    cleaned_text = re.sub(r'([\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf\u3400-\u4dbf])\s+(?=[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf\u3400-\u4dbf])', r'\1', cleaned_text)  # Remove spaces between Japanese characters
    
    return cleaned_text.strip()

def process_and_clean_chunks(chunks: List[Dict], pdf_name: str, output_file: Path, max_words: int, llm_summarize: bool = False) -> List[Dict]:
    """
    Process and clean all chunks, then save the results to a JSON file.

    Args:
        chunks: List of chunk dictionaries to process.
        pdf_name: Name of the PDF file.
        output_file: Path to the output JSON file.
        max_words: Maximum number of words per chunk.
        llm_summarize: Whether to use LLM for summarization.

    Returns:
        List of processed and cleaned chunks.
    """
    processed_chunks = []
    for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks"), 1):
        if chunk['content'].strip():
            logging.info(f"Processing chunk {i}/{len(chunks)}")
            cleaned_text = clean_chunk(chunk['content'])
            logging.info(f"Processed and cleaned chunk: {cleaned_text[:100]}...")
            processed_chunks.append({
                "chunk_id": i,
                "cluster": int(chunk['cluster']),
                "content": cleaned_text,
                "pages": chunk['pages'],
                "pdf_name": pdf_name
            })
        else:
            logging.info(f"Skipping empty chunk {i}/{len(chunks)}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_chunks, f, ensure_ascii=False, indent=2)

    logging.info(f"Processed and cleaned chunks have been saved to {output_file}")
    return processed_chunks

def sentence_aware_japanese_chunking(paragraphs: List[str], clusters: List[int], page_numbers: List[int], max_words: int = 1000) -> List[Dict]:
    """
    Perform sentence-aware chunking on the given paragraphs, respecting cluster boundaries and page numbers.

    Args:
        paragraphs: A list of paragraph strings to be chunked.
        clusters: A list of cluster labels corresponding to each paragraph.
        page_numbers: A list of page numbers corresponding to each paragraph.
        max_words: The maximum number of words allowed in each chunk.

    Returns:
        A list of dictionaries, where each dictionary represents a chunk.
    """
    chunks = []
    cluster_groups = {}
    
    for para, cluster, page_num in zip(paragraphs, clusters, page_numbers):
        cluster_groups.setdefault(cluster, []).append((para, page_num))
    
    for cluster in sorted(cluster_groups.keys()):
        cluster_content = cluster_groups[cluster]
        current_chunk = []
        current_words = 0
        current_pages = set()
        
        for para, page_num in cluster_content:
            for sentence in split_into_sentences(para):
                sentence_words = count_words(sentence)
                
                if current_words + sentence_words > max_words and current_chunk:
                    chunk_text = ''.join(current_chunk) if is_japanese(current_chunk[0]) else ' '.join(current_chunk)
                    chunk_words = count_words(chunk_text)
                    chunks.append({
                        'content': chunk_text,
                        'pages': ','.join(map(str, sorted(current_pages))),
                        'cluster': cluster,
                        'word_count': chunk_words
                    })
                    logging.info(f"Created chunk: cluster {cluster}, words {chunk_words}, pages {','.join(map(str, sorted(current_pages)))}")
                    current_chunk = []
                    current_words = 0
                    current_pages = set()
                
                current_chunk.append(sentence)
                current_words += sentence_words
                current_pages.add(page_num)
        
        if current_chunk:
            chunk_text = ''.join(current_chunk) if is_japanese(current_chunk[0]) else ' '.join(current_chunk)
            chunk_words = count_words(chunk_text)
            chunks.append({
                'content': chunk_text,
                'pages': ','.join(map(str, sorted(current_pages))),
                'cluster': cluster,
                'word_count': chunk_words
            })
            logging.info(f"Created final chunk for cluster {cluster}: words {chunk_words}, pages {','.join(map(str, sorted(current_pages)))}")
    
    return chunks