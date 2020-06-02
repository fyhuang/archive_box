from typing import List

from .summary_gensim import *

def text_to_summary(text: str) -> str:
    return text_to_summary_gensim(text)

def text_to_keywords(text: str) -> List[str]:
    return text_to_keywords_gensim(text)
