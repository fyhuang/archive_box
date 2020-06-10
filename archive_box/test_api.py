import unittest
from unittest.mock import Mock, call

import tempfile
from pathlib import Path

from .api import *

from . import collection, storage, scanner
from .sdid import file_to_sdid

class MockCollection(object):
    pass

class MockProcessorState(object):
    def __init__(self):
        pass

class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.collection = Mock()
        self.processor_state = Mock()
        self.local_store = Mock()

    def test_add_document_from_file(self) -> None:
        expected_doc_id = "abc123"
        self.collection.add_document.return_value = expected_doc_id

        api = ArchiveBoxApi(self.collection, self.processor_state, self.local_store)
        with tempfile.TemporaryDirectory() as tempdir:
            filepath = Path(tempdir) / "hello.txt"
            filepath.write_text("hello, world!")
            expected_sdid = file_to_sdid(filepath)

            api.add_document_from_file(filepath, Path(tempdir))

        self.local_store.upload.assert_called_with(expected_sdid, filepath)
        self.collection.add_document.assert_called_with(expected_sdid, "hello.txt")
        self.processor_state.add_work_item.assert_has_calls([
            call(expected_doc_id, "transcode_video"),
            call(expected_doc_id, "upload"),
            call(expected_doc_id, "auto_summarize"),
            call(expected_doc_id, "index_for_search"),
        ])

    def test_add_document_from_url(self) -> None:
        expected_doc_id = "def456"
        self.collection.add_document.return_value = expected_doc_id

        # temporary location for the mock storage
        with tempfile.TemporaryDirectory() as tempdir:
            dest_filename = Path(tempdir) / "temp123.bin"
            self.local_store.get_temp_filename.return_value = dest_filename

            api = ArchiveBoxApi(self.collection, self.processor_state, self.local_store)
            api.add_document_from_url('http://example.com/index.html')

            expected_sdid = "01_eba96378df9357a67df7a124a6ad5142"
            self.local_store.move_inplace.assert_called_with(expected_sdid, dest_filename)
            self.collection.add_document.assert_called_with(expected_sdid, "index.html")
            self.processor_state.add_work_item.assert_has_calls([
                call(expected_doc_id, "transcode_video"),
                call(expected_doc_id, "upload"),
                call(expected_doc_id, "auto_summarize"),
                call(expected_doc_id, "index_for_search"),
            ])
