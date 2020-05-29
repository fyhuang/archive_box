from flask import request, redirect, render_template

from . import app, workspace, factory

# TODO(fyhuang): put this in a separate api.py?
@app.route("/api/add_document", methods=["POST"])
def collection_add_document():
    cid = request.form['cid']
    sdid = StoredDataId.from_strid(request.form['sdid'])
    filename = request.form['filename']

    # add the document to the collection
    collection = factory.new_collection(cid)
    cid.add_document(sdid, filename)

    # remove from scanned files
    factory.new_scanner_state().delete_scanned_file(sdid)

    return redirect('/')


@app.route("/c/<cid>", methods=["GET"])
def collection_index(cid: str):
    collection = factory.new_collection(cid)
    documents = collection.docs_recent()
    return render_template(
            "collection_index.html",
            collection_name=collection.config["display_name"],
            search_name="Recent",
            documents=documents
    )


#@app.route("/c/<cid>/d/<docid>", methods=["GET"])
#def collection_document(cid: str, docid: str):
#    pass
