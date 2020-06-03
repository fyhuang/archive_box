import unittest
import sqlite3

from .search_index import *

from archive_box import archive_box_pb2 as pb2


class SnippetTests(unittest.TestCase):
    def test_from_sqlite(self) -> None:
        expected = Snippet("alpha beta gamma", (6, 10))
        self.assertEqual(
                expected,
                Snippet.from_sqlite("alpha <<<::beta::>>> gamma")
        )
        h_slice = slice(expected.highlight[0], expected.highlight[1])
        self.assertEqual("beta", expected.snippet[h_slice])

    def test_from_sqlite_empty(self) -> None:
        self.assertEqual(
                Snippet("hello world", (6, 6)),
                Snippet.from_sqlite("hello <<<::::>>>world")
        )

    def test_from_sqlite_begin(self) -> None:
        self.assertEqual(
                Snippet("hello world", (0, 5)),
                Snippet.from_sqlite("<<<::hello::>>> world")
        )

    def test_from_sqlite_end(self) -> None:
        self.assertEqual(
                Snippet("hello world", (6, 11)),
                Snippet.from_sqlite("hello <<<::world::>>>")
        )


class SqliteDocumentSearchIndexTests(unittest.TestCase):
    def get_index(self) -> SqliteDocumentSearchIndex:
        conn = sqlite3.connect(":memory:")
        index = SqliteDocumentSearchIndex(conn)
        index.first_time_setup()
        return index

    def test_basic(self) -> None:
        index = self.get_index()

        doc = pb2.Document()
        doc.id = "abc123"
        doc.display_name = "My Document"
        doc.tags.extend(["tag1", "tag2"])
        doc.auto_summary = "Search indexing is fun"
        index.update_index(doc)

        r1 = index.query("Document", 1)[0]
        self.assertEqual(doc.id, r1.doc_id)
        self.assertEqual(Snippet("My Document", (3, 11)), r1.display_name_snippet)
        self.assertEqual(None, r1.tags_snippet)
        self.assertEqual(None, r1.freetext_snippet)

        r2 = index.query("tag2", 1)[0]
        assert r2.tags_snippet is not None
        self.assertEqual("tag2", r2.tags_snippet.highlighted_str())

        # porter stemming
        r3 = index.query("index", 1)[0]
        assert r3.freetext_snippet is not None
        self.assertEqual("indexing", r3.freetext_snippet.highlighted_str())
