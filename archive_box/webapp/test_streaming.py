import unittest
import tempfile
from flask import Flask

from .streaming import *


class ServeFileRangeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        (Path(self.tempdir.name) / "hello.txt").write_text("hello, world!")

        def get_file(filename: str):
            return serve_file_range(Path(self.tempdir.name) / filename, mimetype="text/plain")
        self.app = Flask("test_range")
        self.app.add_url_rule("/<filename>", "get_file", get_file)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_head(self) -> None:
        with self.app.test_client() as client:
            response = client.head('/hello.txt')
        self.assertEqual(b"", response.data)
        self.assertEqual("13", response.headers.get("Content-Length"))
        self.assertEqual("bytes", response.headers.get("Accept-Ranges"))

    def test_no_range_header(self) -> None:
        with self.app.test_client() as client:
            response = client.get('/hello.txt')
        self.assertEqual(b"hello, world!", response.data)
        self.assertEqual("bytes", response.headers.get("Accept-Ranges"))

    def test_no_file(self) -> None:
        with self.app.test_client() as client:
            response = client.get('/unknown')
        self.assertEqual(404, response.status_code)

    def test_bad_range_unit(self) -> None:
        with self.app.test_client() as client:
            self.assertEqual(416, client.get('/hello.txt', headers=[('Range', 'words=1-2')]).status_code)

    def test_partial(self) -> None:
        with self.app.test_client() as client:
            self.assertEqual(b'hel', client.get('/hello.txt', headers=[('Range', 'bytes=0-2')]).data)

    def test_partial_to_end(self) -> None:
        with self.app.test_client() as client:
            self.assertEqual(b'world!', client.get('/hello.txt', headers=[('Range', 'bytes=7-')]).data)
