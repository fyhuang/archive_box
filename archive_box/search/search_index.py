import sqlite3
from typing import Optional, List, Tuple, NamedTuple

from dtsdb import sqlite_util

from archive_box import archive_box_pb2 as pb2


_HIGHLIGHT_PREFIX = "<<<::"
_HIGHLIGHT_POSTFIX = "::>>>"


class Snippet(NamedTuple):
    snippet: str
    highlight: Tuple[int, int]

    @staticmethod
    def from_sqlite(sqlite_snippet: Optional[str]) -> Optional['Snippet']:
        if sqlite_snippet is None:
            return None

        # extract the highlighted snippet
        before_highlight, _, rest = sqlite_snippet.partition(_HIGHLIGHT_PREFIX)
        if len(rest) == 0:
            # no highlighted portion
            return None

        highlighted, _, after_highlight = rest.partition(_HIGHLIGHT_POSTFIX)

        hi_indices = (len(before_highlight), len(before_highlight) + len(highlighted))
        return Snippet(before_highlight + highlighted + after_highlight, hi_indices)
    
    def highlighted_str(self) -> str:
        hi_slice = slice(self.highlight[0], self.highlight[1])
        return self.snippet[hi_slice]


class SearchResult(NamedTuple):
    doc_id: str
    display_name_snippet: Optional[Snippet]
    tags_snippet: Optional[Snippet]
    freetext_snippet: Optional[Snippet]


class SqliteDocumentSearchIndex(object):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def first_time_setup(self) -> None:
        schema = '''CREATE VIRTUAL TABLE doc_fts_index USING fts5 (
            doc_id UNINDEXED,
            display_name,
            tags,
            freetext,
            tokenize = porter
        )'''
        sqlite_util.ensure_table_matches(self.conn, schema)

    def reset_index(self) -> None:
        with self.conn:
            self.conn.execute('DELETE FROM doc_fts_index WHERE true')

    def update_index(self, doc: pb2.Document) -> None:
        tags_encoded = ' '.join(doc.tags)
        freetext_encoded = '\n\n'.join([
            doc.description,
            doc.orig_filename,
            doc.downloaded_from_url,
            doc.auto_summary,
            ' '.join(doc.auto_keywords),
            # TODO(fyhuang): metadata
        ]).strip()

        with self.conn:
            self.conn.execute('''INSERT OR REPLACE INTO doc_fts_index
                (doc_id, display_name, tags, freetext)
            VALUES (?, ?, ?, ?)''',
                (doc.id, doc.display_name, tags_encoded, freetext_encoded))

    def query(self, query: str, num_results: int) -> List[SearchResult]:
        select_query = '''
        SELECT
            doc_id,
            highlight(doc_fts_index, 1, '{hi_left}', '{hi_right}'),
            snippet  (doc_fts_index, 2, '{hi_left}', '{hi_right}', '', {snippet_len}),
            snippet  (doc_fts_index, 3, '{hi_left}', '{hi_right}', '', {snippet_len})
        FROM doc_fts_index
        WHERE doc_fts_index MATCH ?
        ORDER BY rank LIMIT {limit}
        '''.format(
                hi_left=_HIGHLIGHT_PREFIX,
                hi_right=_HIGHLIGHT_POSTFIX,
                snippet_len=10, # num tokens?
                limit=num_results,
        )

        c = self.conn.cursor()
        c.execute(select_query, (query,))
        result = []
        for row in c:
            sr = SearchResult(
                row[0],
                Snippet.from_sqlite(row[1]),
                Snippet.from_sqlite(row[2]),
                Snippet.from_sqlite(row[3]),
            )
            result.append(sr)
        return result
