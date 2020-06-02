"""Summarization and keyword extraction using gensim.

Results: relatively robust to long documents. Output is verbose but seems relevant enough for search.
"""

from typing import List

from gensim import summarization # type: ignore

def text_to_keywords_gensim(text: str) -> List[str]:
    return summarization.keywords(text).splitlines()

def text_to_summary_gensim(text: str) -> str:
    return summarization.summarizer.summarize(text)
