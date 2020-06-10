from werkzeug.exceptions import BadRequest, RequestedRangeNotSatisfiable
from flask import abort, request, Response, send_file
from pathlib import Path

from archive_box.byte_range import ByteRangeReader


def serve_file_range(path: Path, mimetype: str):
    if not path.exists():
        abort(404)

    range_header = request.headers.get("Range", None)
    if range_header is None:
        resp = send_file(path, mimetype=mimetype, conditional=True)
        resp.headers.add("Accept-Ranges", "bytes")
        return resp

    file_size = path.stat().st_size
    # Both ends of "range" are inclusive
    range = [0, file_size - 1]

    # Only support parsing one byte range with optional end, no support for negative offsets
    unit, _, ranges_text = range_header.partition("=")
    if unit != "bytes":
        raise RequestedRangeNotSatisfiable(description="Range must be specified using bytes")

    ranges = [rt.strip() for rt in ranges_text.split(',')]
    if len(ranges) != 1:
        raise RequestedRangeNotSatisfiable(description="Only one byte range can be specified")

    start, _, end = ranges[0].partition("-")
    if len(start) == 0:
        raise RequestedRangeNotSatisfiable(description="Range must be of the form <start>-[<end>]")

    range[0] = int(start)
    if len(end) > 0:
        range[1] = int(end)

    # clamp range to the file size
    range[1] = min(file_size - 1, range[1])

    def read_file():
        with ByteRangeReader(path.open("rb"), range[0], range[1]) as f:
            while True:
                data = f.read(1024 * 1024)
                if len(data) == 0:
                    return
                yield data

    resp = Response(read_file(), mimetype=mimetype)
    resp.headers.add("Accept-Ranges", "bytes")
    resp.headers.add("Content-Range", "bytes {start}-{end}/{total}".format(
        start=range[0],
        end=range[1],
        total=file_size,
    ))
    return resp
