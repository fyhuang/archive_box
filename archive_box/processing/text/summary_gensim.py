"""Summarization and keyword extraction using gensim.

Results: relatively robust to long documents. Output is verbose but seems relevant enough for search.
"""

import traceback
from typing import List

from gensim import summarization # type: ignore

def text_to_keywords_gensim(text: str) -> List[str]:
    return summarization.keywords(text).splitlines()

def text_to_summary_gensim(text: str) -> str:
    try:
        return summarization.summarizer.summarize(text)
    except ValueError as e:
        if str(e) == "input must have more than one sentence":
            # nothing we can do about it here
            print("Cannot summarize: {}".format(text))
            traceback.print_exc()
            return ""
        raise e
