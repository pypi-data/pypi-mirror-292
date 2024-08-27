# -*- coding: utf-8 -*-

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import nltk

def lemmatize_text(text, pos_tags=None):
    """
    Reduces words in text to their lemmas (dictionary forms).

    Args:
        text (str or list): Text or list of tokens to lemmatize.
        pos_tags (list, optional): List of part-of-speech tags for each token. 
                                    If None, POS tags will be determined automatically.

    Returns:
        str or list: Text or list of tokens with words reduced to their lemmas.
    """
    lemmatizer = WordNetLemmatizer()

    if isinstance(text, str):
        tokens = text.split()
        if pos_tags is None:
            pos_tags = get_wordnet_pos_tags(tokens)
        lemmas = [lemmatizer.lemmatize(token, pos=tag) for token, tag in zip(tokens, pos_tags)]
        return ' '.join(lemmas)
    elif isinstance(text, list):
        if pos_tags is None:
            pos_tags = get_wordnet_pos_tags(text)
        return [lemmatizer.lemmatize(token, pos=tag) for token, tag in zip(text, pos_tags)]
    else:
        raise TypeError("Input text must be a string or a list of tokens.")

def get_wordnet_pos_tags(tokens):
    """
    Determines part-of-speech tags for a list of tokens and converts them to a format 
    understandable by WordNetLemmatizer.

    Args:
        tokens (list): List of tokens.

    Returns:
        list: List of part-of-speech tags in WordNet format.
    """
    pos_tags = nltk.pos_tag(tokens)
    wordnet_tags = []
    for token, tag in pos_tags:
        if tag.startswith('J'):
            wordnet_tags.append(wordnet.ADJ)
        elif tag.startswith('V'):
            wordnet_tags.append(wordnet.VERB)
        elif tag.startswith('N'):
            wordnet_tags.append(wordnet.NOUN)
        elif tag.startswith('R'):
            wordnet_tags.append(wordnet.ADV)
        else:
            wordnet_tags.append(wordnet.NOUN)  # Default to noun
    return wordnet_tags