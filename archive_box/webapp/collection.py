from flask import request, redirect, render_template
from werkzeug.wrappers import Response

from archive_box.sdid import StoredDataId

from . import app, globals

# TODO(fyhuang): put this in a separate api.py?
@app.route("/api/add_document", methods=["POST"])
def collection_add_document() -> Response:
    cid: str = request.form['cid']
    sdid: StoredDataId = StoredDataId.from_strid(request.form['sdid'])
    filename: str = request.form['filename']

    if "StoredData" in sdid.schema:
        raise RuntimeError("bad format?")

    # add the document to the collection
    collection = globals.factory.new_collection(cid)
    collection.add_document(sdid, filename)

    # remove from scanned files
    globals.factory.new_scanner_state().delete_scanned_file(sdid)

    return redirect('/')


@app.route("/c/<cid>", methods=["GET"])
def collection_index(cid: str):
    collection = globals.factory.new_collection(cid)
    documents = collection.docs_recent()
    return render_template(
            "collection_index.html",
            collection_id=cid,
            collection_name=collection.config["display_name"],
            search_name="Recent",
            documents=documents
    )


#@app.route("/c/<cid>/d/<docid>", methods=["GET"])
#def collection_document(cid: str, docid: str):
#    pass
