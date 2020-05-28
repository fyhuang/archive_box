import datetime

from flask import request, redirect, render_template

from . import manager, ingestor, util
from . import archive_box_pb2 as pb2
from .server import app
from .storage.stored_data import StoredDataId

def now_ms() -> int:
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000.0)


@app.route("/api/ingest", methods=["POST"])
def collection_ingest_document():
    cid = request.form['cid']
    sdid = StoredDataId.from_strid(request.form['sdid'])
    filename = request.form['filename']

    # add the document to the collection
    collection = manager.get().col(cid)
    document = pb2.Document()
    document.id = util.new_id()
    document.data_id = sdid.to_strid()

    document.needs_review = True
    document.creation_time_ms = now_ms()
    document.last_mod_time_ms = now_ms()

    document.display_name = filename
    document.orig_filename = filename

    collection.db.get_table("Document").update(document)

    # tell ingestor to target this collection
    ingestor.get().set_target(sdid, cid)

    return redirect('/')


@app.route("/c/<cid>", methods=["GET"])
def collection_index(cid: str):
    collection = manager.get().col(cid)
    documents = collection.db.get_table("Document").queryall(lambda m: True, lambda m: m.creation_time_ms, reverse=True, limit=50)
    return render_template(
            "collection_index.html",
            documents=documents
    )


@app.route("/c/<cid>/d/<docid>", methods=["GET"])
def collection_document(cid: str, docid: str):
    pass
