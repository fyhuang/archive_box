import unittest

from .rake import *


_TEXT = '''
Hello, world! Some words are from the dictionary.
I like cats; and also kittens. "Go West, young man!" said the old man.
'''


class KeywordsTests(unittest.TestCase):
    def test_load_delimiters(self) -> None:
        delimiters = load_delimiters()
        self.assertTrue(len(delimiters) > 0)
        self.assertTrue("of" in delimiters)
        self.assertTrue("." in delimiters)

    def test_tokenize_rake(self) -> None:
        tokens, indexed_words = tokenize_rake(_TEXT)
        self.assertEqual("hello", tokens[0])
        self.assertEqual("the", tokens[-4])
        self.assertEqual(IndexedWord("hello", 0), indexed_words[0])
        self.assertEqual(IndexedWord("the", 27), indexed_words[-4])

    def test_gen_phrases_rake(self) -> None:
        tokens, indexed_words = tokenize_rake(_TEXT)
        result = list(gen_phrases_rake(indexed_words))
        self.assertEqual(IndexedWord("hello", 0), result[0])
        self.assertEqual(IndexedWord("like cats", 12), result[4])
        self.assertEqual(IndexedWord("go west", 20), result[6])

    def test_text_to_keywords_rake(self) -> None:
        keywords = text_to_keywords_rake(_TEXT)
        print(keywords)
