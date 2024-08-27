# -*- coding: utf-8 -*-

import nltk

def tokenize_text(text):
    """
    Tokenizes text into a list of words.

    Args:
        text (str): Text to be tokenized.

    Returns:
        list: A list of tokens (words).
    """
    tokens = nltk.word_tokenize(text)
    return tokens