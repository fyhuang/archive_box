import unittest
from pathlib import Path

from .extract_pdf import *

PARAGRAPH_1 = '''
Paragraph 1. However little known the feelings or views of such a man may be on his first entering a neighborhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters.
'''.strip()

FOOTNOTE = '''
Footnote: contents of this file are in the public domain.
'''.strip()

class ExtractPdfTests(unittest.TestCase):
    def test_try_join_word(self) -> None:
        self.assertEqual(None, try_join_word("nota", "word"))
        self.assertEqual("understand", try_join_word("un-", "derstand"))

    def test_reconstruct_paragraph(self) -> None:
        self.assertEqual(
            "Mr. Bennet was among the earliest of those who waited on Mr. Bingley",
            reconstruct_paragraph("Mr. Bennet was\namong the earli-\nest of those who wait-\ned on Mr. Bingley")
        )

    def test_extract_pdf_paragraphs(self) -> None:
        paragraphs = extract_pdf_paragraphs(Path("testdata") / "sample_paper.pdf")
        self.assertEqual("Archive Box Test PDF", paragraphs[0])
        self.assertEqual("John Doe <johndoe@example.com>, Jane Smith <janesmith@example.com>", paragraphs[1])
        self.assertEqual(PARAGRAPH_1, paragraphs[2])
        self.assertEqual(FOOTNOTE, paragraphs[-1])
