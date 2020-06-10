from typing import Any
from flask import request, redirect

from . import app, globals


# TODO(fyhuang): make this a scanner specific API? have scanner not pre-ingest docs?
@app.route("/api/add_document", methods=["POST"])
def collection_add_document() -> Any:
    cid: str = request.form['cid']
    sdid: str = request.form['sdid']
    filename: str = request.form['filename']

    if "StoredData" in sdid:
        raise RuntimeError("bad format?")

    api = globals.factory.new_api(cid)
    api._add_from_store(sdid, filename)

    # remove from scanned files
    globals.factory.new_scanner_state().delete_scanned_file(sdid)

    return redirect('/')


@app.route("/api/create_document/<cid>", methods=["POST"])
def api_create_document(cid: str) -> Any:
    urls_or_paths = request.form.getlist('files')
    # TODO(fyhuang): customize summary, tags, etc.
