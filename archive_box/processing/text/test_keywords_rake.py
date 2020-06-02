import unittest

from .keywords_rake import *


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

    def test_gen_phrases_rake(self) -> None:
        tokens, result = gen_phrases_rake(_TEXT)
        self.assertEqual(IndexedPhrase(["hello"], 0), result[0])
        self.assertEqual(IndexedPhrase(["like", "cats"], 12), result[4])
        self.assertEqual(IndexedPhrase(["go", "west"], 20), result[6])

    def test_compute_cooccurance(self) -> None:
        result = compute_cooccurance([
            ["hello", "world"],
            ["hello", "my", "friend"],
            ["never"],
        ])
        self.assertEqual(0, result["unknown"])
        self.assertEqual(1, result["never"])
        self.assertEqual(2, result["world"])
        self.assertEqual(3, result["my"])
        self.assertEqual(3, result["friend"])
        self.assertEqual(5, result["hello"])

    def test_text_to_keywords_rake(self) -> None:
        keywords = text_to_keywords_rake(_TEXT)

