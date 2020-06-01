# Extract keywords from text
from typing import List

from . import rake

def text_to_keywords(text: str) -> List[str]:
    return rake.text_to_keywords_rake(text)
