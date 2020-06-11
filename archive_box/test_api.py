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

    def test_put_url_into_store(self) -> None:
        # temporary location for the mock storage
        with tempfile.TemporaryDirectory() as tempdir:
            dest_filename = Path(tempdir) / "temp123.bin"
            self.local_store.get_temp_filename.return_value = dest_filename

            api = ArchiveBoxApi(self.collection, self.processor_state, self.local_store)
            sdid, orig_filename, orig_mime = api.put_url_into_store('http://example.com/index.html')

        expected_sdid = "01_eba96378df9357a67df7a124a6ad5142"
        self.local_store.move_inplace.assert_called_with(expected_sdid, dest_filename)

        self.assertEqual(expected_sdid, sdid)
        self.assertEqual("index.html", orig_filename)
        self.assertEqual("text/html", orig_mime)

    def test_put_local_file_into_store(self) -> None:
        api = ArchiveBoxApi(self.collection, self.processor_state, self.local_store)
        with tempfile.TemporaryDirectory() as tempdir:
            filepath = Path(tempdir) / "hello.txt"
            filepath.write_text("hello, world!")
            expected_sdid = file_to_sdid(filepath)

            sdid, orig_filename, orig_mime = api.put_local_file_into_store(Path(tempdir), filepath)

        self.local_store.upload.assert_called_with(expected_sdid, filepath)

        self.assertEqual(expected_sdid, sdid)
        self.assertEqual("hello.txt", orig_filename)
        self.assertEqual("text/plain", orig_mime)
