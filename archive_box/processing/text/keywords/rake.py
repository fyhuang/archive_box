"""RAKE method for keyword extraction.

References:

https://github.com/csurfer/rake-nltk

Rose, Stuart & Engel, Dave & Cramer, Nick & Cowley, Wendy. (2010). Automatic Keyword Extraction from Individual Documents. 10.1002/9780470689646.ch1.
"""

import collections
import inspect
import itertools
import string
import zipfile
from pathlib import Path
from typing import Tuple, List, Set, Dict, Mapping, Iterable, NamedTuple, Counter

import nltk.tokenize # type: ignore


_METRIC = "ratio"


class IndexedPhrase(NamedTuple):
    phrase: List[str]
    first_word_index: int

    @staticmethod
    def merged(phrases: List['IndexedPhrase']) -> 'IndexedPhrase':
        a = list(itertools.chain.from_iterable(ip.phrase for ip in phrases))
        return IndexedPhrase(
                a,
                phrases[0].first_word_index
        )


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


def compute_cooccurance(phrases: Iterable[List[str]]) -> Mapping[str, int]:
    word_counter: Counter[str] = Counter()
    for phrase in phrases:
        word_counter.update(tup[0] for tup in itertools.product(phrase, phrase))
    return word_counter

    #result = collections.defaultdict(lambda: 0)
    #for tup, count in tuple_counter.items():
    #    result[tup[0]] += count
    #return result


def gen_phrases_rake(text: str) -> Tuple[List[str], List[IndexedPhrase]]:
    tokens = [t.lower() for t in nltk.tokenize.wordpunct_tokenize(text)]
    indexed_tokens = [IndexedPhrase([t], i) for i, t in enumerate(tokens)]
    delimiters = load_delimiters()

    result = []
    for key, phrase_iter in itertools.groupby(indexed_tokens, key=lambda ip: is_delimiters(ip.phrase[0], delimiters)):
        if key == True:
            # is a delimiter
            continue

        phrase_list = list(phrase_iter)
        result.append(IndexedPhrase.merged(phrase_list))

    return (tokens, result)


# TODO(fyhuang): support for other languages?
def text_to_keywords_rake(text: str) -> List[str]:
    tokens, phrases = gen_phrases_rake(text)

    candidate_keywords = {}
    for indexed_phrase in phrases:
        candidate_keywords[' '.join(indexed_phrase.phrase)] = indexed_phrase.phrase

    frequency = Counter(tokens)
    degree = compute_cooccurance(candidate_keywords.values())

    scores: Dict[str, float] = {}
    for kw, phrase in candidate_keywords.items():
        p_degree = sum(degree[w] for w in phrase)
        p_frequency = sum(frequency[w] for w in phrase)
        if _METRIC == "degree":
            scores[kw] = p_degree
        elif _METRIC == "frequency":
            scores[kw] = p_frequency
        elif _METRIC == "ratio":
            scores[kw] = p_degree / p_frequency
        else:
            raise RuntimeError("unknown metric {}".format(_METRIC))

    ranked_keywords = list(candidate_keywords.keys())
    ranked_keywords.sort(key=lambda kw: scores[kw], reverse=True)

    # TODO(fyhuang): support for intervening stopwords
    return ranked_keywords[:5]
