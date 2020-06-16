import json
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

    # DEPRECATED, see api_create_document
    api = globals.factory.new_api(cid)
    collection = globals.factory.new_collection(cid)
    doc_id = collection.add_document(sdid, filename)
    api.first_time_process(doc_id)

    # remove from scanned files
    globals.factory.new_scanner_state().delete_scanned_file(sdid)

    return redirect('/')


@app.route("/api/create_document/<cid>", methods=["POST"])
def api_create_document(cid: str) -> Any:
    request_data = request.get_json()
    api = globals.factory.new_api(cid)

    print(request_data)

    doc_id = api.create_document(
        request_data["source"],
        needs_review=request_data.get("needs_review", True),
        doc_title=request_data["title"],
        doc_tags=set(request_data["tags"]),
        doc_description=request_data["description"],
        user_metadata=request_data["metadata"],
        orig_url=request_data.get("orig_url", None),
        base_path=request_data.get("base_path", None),
        skip_duplicates=request_data.get("skip_duplicates", True),
    )

    result = {
        "status": "OK",
    }
    if doc_id is not None:
        result["doc_id"] = doc_id
    return json.dumps(result)


@app.route("/api/reprocess_document/<cid>/d/<docid>")
def api_reprocess_document(cid: str, docid: str) -> Any:
    api = globals.factory.new_api(cid)
    api.reprocess(docid)
    return redirect(request.referrer)
