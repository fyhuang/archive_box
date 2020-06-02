from flask import abort, request, redirect, render_template, url_for
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
    doc_id = collection.add_document(sdid, filename)

    # queue all processing for the new document
    pstate = globals.factory.new_processor_state(cid)
    pstate.add_work_item(doc_id, "upload")
    pstate.add_work_item(doc_id, "auto_summarize")
    pstate.add_work_item(doc_id, "index_for_search")
    pstate.add_work_item(doc_id, "transcode_video")

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


@app.route("/c/<cid>/d/<docid>", methods=["GET"])
def collection_document(cid: str, docid: str):
    collection = globals.factory.new_collection(cid)
    document = collection.db.get_table("Document").get(docid)
    if document is None:
        abort(404)

    main_url = "/local/{}/{}".format(cid, docid)

    return render_template(
            "collection_document.html",
            collection_id=cid,
            collection_name=collection.config["display_name"],
            document=document,
            main_url=main_url,
    )

@app.route("/c/<cid>/d/<docid>/edit", methods=["GET"])
def collection_document_edit(cid: str, docid: str):
    collection = globals.factory.new_collection(cid)
    document = collection.db.get_table("Document").get(docid)
    if document is None:
        abort(404)
    return render_template(
            "collection_document_edit.html",
            document=document,
    )

@app.route("/c/<cid>/d/<docid>/edit", methods=["POST"])
def collection_document_edit_submit(cid: str, docid: str):
    checkbox_fields = ["needs_review"]
    text_fields = ["display_name", "description"]
    list_fields = ["tags"]

    collection = globals.factory.new_collection(cid)
    document = collection.db.get_table("Document").get(docid)
    if document is None:
        abort(404)

    for f in checkbox_fields:
        if f in request.form:
            setattr(document, f, True)
        else:
            setattr(document, f, False)

    for f in text_fields:
        setattr(document, f, request.form.get(f, ""))

    for f in list_fields:
        del getattr(document, f)[:]
        for val in request.form.getlist(f):
            getattr(document, f).append(val)

    collection.db.get_table("Document").update(document)
    return redirect(url_for("collection_document", cid=cid, docid=docid))
