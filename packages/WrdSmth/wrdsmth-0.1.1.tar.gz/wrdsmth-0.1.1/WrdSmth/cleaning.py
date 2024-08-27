# -*- coding: utf-8 -*-

import re

def clean_text(text):
    """
    Cleans text by removing HTML tags, punctuation, and extra spaces.

    Args:
        text (str): Text to be cleaned.

    Returns:
        str: Cleaned text.
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # Convert to lowercase
    text = text.lower()

    # Remove extra spaces
    text = ' '.join(text.split())

    return text