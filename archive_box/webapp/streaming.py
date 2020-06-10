from flask import abort, send_file
from pathlib import Path


def serve_file_range(path: Path, mimetype: str):
    if not path.exists():
        abort(404)

    resp = send_file(path, mimetype=mimetype, conditional=True)
    resp.headers.add("Accept-Ranges", "bytes")
    return resp
