import inspect
import itertools
import string
import zipfile
from pathlib import Path
from typing import Tuple, List, Set, NamedTuple

import nltk.tokenize # type: ignore


class IndexedPhrase(NamedTuple):
    phrase: List[str]
    first_word_index: int


def load_delimiters() -> Set[str]:
    import archive_box
    # TODO(fyhuang): is it easier to use __file__?
    package_path = Path(inspect.getfile(archive_box)).resolve().parent
    root_path = package_path.parent
    stopwords_path = root_path / "extern" / "nltk" / "stopwords.zip"
    with zipfile.ZipFile(stopwords_path, "r") as zip:
        with zip.open("stopwords/english", "r") as f:
            stopwords = f.read().decode().splitlines()
    return set(stopwords) | set(string.punctuation)


def is_delimiters(word: str, delimiters: Set[str]) -> bool:
    if word in delimiters:
        return True
    return all(letter in delimiters for letter in word)


def tokenize_rake(text: str) -> Tuple[List[str], List[IndexedWord]]:
    #sentences = nltk.tokenize.sent_tokenize(text)
    tokens = [t.lower() for t in nltk.tokenize.wordpunct_tokenize(text)]
    return tokens, [IndexedWord(t, i) for i, t in enumerate(tokens)]


def gen_phrases_rake(indexed_words: List[IndexedWord]):
    delimiters = load_delimiters()
    for key, phrase_iter in itertools.groupby(indexed_words, key=lambda t: is_delimiters(t.word, delimiters)):
        if key == True:
            # is a delimiter
            continue

        phrase_list = list(phrase_iter)
        yield IndexedWord(' '.join(iw.word for iw in phrase_list), phrase_list[0].word_index)


# TODO(fyhuang): support for other languages?
def text_to_keywords_rake(text: str) -> List[str]:
    tokens, indexed_words = tokenize_rake(text)
    phrases: List[IndexedWord] = list(gen_phrases_rake(indexed_words))

    candidate_keywords: Set[str] = set()
    for phrase_iw in phrases:
        candidate_keywords.add(phrase_iw.word)

    # TODO(fyhuang): ranking
    ranked_keywords = list(candidate_keywords)

    # TODO(fyhuang): support for intervening stopwords
    return list(candidate_keywords)[:5]
