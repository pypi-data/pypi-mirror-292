# SPDX-License-Identifier: Apache-2.0
# Standard
import re
from typing import List, Tuple

# Third Party
import PyPDF2
from janome.tokenizer import Tokenizer

# Initialize the Janome tokenizer
janome_tokenizer = Tokenizer()

def extract_text_from_pdf(pdf_path: str) -> List[Tuple[int, str]]:
    """
    Extract text content from a PDF file, along with page numbers.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        List of tuples, each containing (page_number, text_content)
    """
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return [(i, page.extract_text()) for i, page in enumerate(reader.pages, 1)]

def preprocess_document(pages: List[Tuple[int, str]], tagger) -> Tuple[List[str], List[List[Tuple]], List[str], List[str], List[int]]:
    """
    Preprocess the document by tokenizing, lemmatizing, and generating n-grams.

    Args:
        pages: List of tuples containing (page_number, text_content)
        tagger: Initialized MeCab tagger.

    Returns:
        Tuple containing:
            - list of paragraphs (str)
            - list of tokenized paragraphs (list of tuples)
            - list of lemmatized paragraphs (list of str)
            - list of n-grams (list of str)
            - list of page numbers for each paragraph
    """
    paragraphs, page_numbers, tokenized_paragraphs, lemmatized_paragraphs, all_ngrams = [], [], [], [], []
    
    for page_num, text in pages:
        page_paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        
        for para in page_paragraphs:
            tokens = tokenize_with_pos(para, tagger)
            lemmas = lemmatize(tokens)
            ngrams = generate_ngrams([token[0] for token in tokens])
            
            paragraphs.append(para)
            page_numbers.append(page_num)
            tokenized_paragraphs.append(tokens)
            lemmatized_paragraphs.append(' '.join(lemmas))
            all_ngrams.extend(ngrams)
    
    return paragraphs, tokenized_paragraphs, lemmatized_paragraphs, all_ngrams, page_numbers

def tokenize_with_pos(text: str, tagger) -> List[Tuple[str, str, str]]:
    """
    Tokenize Japanese text and extract part-of-speech information using MeCab.

    Args:
        text: Input Japanese text.
        tagger: Initialized MeCab tagger.

    Returns:
        List of tuples, each containing (surface_form, part_of_speech, base_form)
    """
    node = tagger.parseToNode(text)
    tokens = []
    while node:
        if node.surface:
            feature = node.feature.split(',')
            surface = node.surface
            pos = feature[0]
            base = feature[6] if len(feature) > 7 else surface
            tokens.append((surface, pos, base))
        node = node.next
    return tokens

def lemmatize(tokens: List[Tuple[str, str, str]]) -> List[str]:
    """
    Lemmatize tokens based on their part of speech.

    Args:
        tokens: List of tuples (surface_form, part_of_speech, base_form).

    Returns:
        List of lemmatized tokens.
    """
    return [token[2] if token[1] not in ['助詞', '助動詞'] else token[0] for token in tokens]

def generate_ngrams(tokens: List[str], n: int = 2) -> List[str]:
    """
    Generate n-grams from a list of tokens.

    Args:
        tokens: List of tokens.
        n: The 'n' in n-gram.

    Returns:
        List of n-grams.
    """
    return [' '.join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def is_japanese(text: str) -> bool:
    """
    Check if the text contains Japanese characters.

    Args:
        text: The input text to check.

    Returns:
        True if the text contains Japanese characters, False otherwise.
    """
    return any('\u4e00' <= char <= '\u9fff' or '\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text)

def count_words(text: str) -> int:
    """
    Count words in the given text, using Janome for Japanese and a simple split for other languages.

    Args:
        text: The input text to count words from.

    Returns:
        The number of words in the text.
    """
    return len(list(janome_tokenizer.tokenize(text, wakati=True))) if is_japanese(text) else len(text.split())

def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences, handling both Japanese and non-Japanese text.

    Args:
        text: The input text to split into sentences.

    Returns:
        A list of sentences extracted from the input text.
    """
    if is_japanese(text):
        sentences = re.split(r'。|！|？', text)
        return [s + '。' for s in sentences if s.strip()]
    else:
        return re.findall(r'[^.!?]+[.!?]*', text)