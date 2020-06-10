from flask import abort, request, redirect, render_template, url_for
from werkzeug.wrappers import Response

from archive_box.processing.video.config import TargetRepresentation

from . import app, globals


@app.route("/c/<cid>", methods=["GET"])
def collection_index(cid: str):
    collection = globals.factory.new_collection(cid)
    if "q" in request.args:
        search_query = request.args["q"]
        search_name = "Search: {}".format(search_query)

        results = collection.search_index.query(search_query, 30)
        documents = collection.docs.getall([r.doc_id for r in results])
    else:
        filter = request.args.get("filter", "Recent")
        search_name = filter
        search_query = ""
        documents = collection.docs_recent()

    return render_template(
            "collection_index.html",
            collection_id=cid,
            collection_name=collection.config.display_name,
            search_name=search_name,
            search_query=search_query,
            documents=documents
    )


@app.route("/c/<cid>/d/<docid>", methods=["GET"])
def collection_document(cid: str, docid: str):
    collection = globals.factory.new_collection(cid)
    document = collection.docs.get(docid)
    if document is None:
        abort(404)

    main_url = "/local/{}/{}".format(cid, docid)

    media_formats = {}
    for name in document.data.media_formats.keys():
        url = "/local/{}/{}?which=media_formats.{}".format(cid, docid, name)
        if name == "original":
            media_formats["Original"] = url
        else:
            tr = TargetRepresentation.from_str(name)
            # TODO(fyhuang): omit codec if they're all the same
            # TODO(fyhuang): omit bitrate if there's only one per resolution
            media_formats["{}p @{}k {}".format(tr.height, tr.bitrate_kbits, tr.codec)] = url

    return render_template(
            "collection_document.html",
            collection_id=cid,
            collection_name=collection.config.display_name,
            document=document,
            main_url=main_url,
            media_formats=media_formats,
    )

@app.route("/c/<cid>/d/<docid>/edit", methods=["GET"])
def collection_document_edit(cid: str, docid: str):
    collection = globals.factory.new_collection(cid)
    document = collection.docs.get(docid)
    if document is None:
        abort(404)
    return render_template(
            "collection_document_edit.html",
            document=document,
            collection_id=cid,
    )

@app.route("/c/<cid>/d/<docid>/edit", methods=["POST"])
def collection_document_edit_submit(cid: str, docid: str):
    checkbox_fields = ["needs_review"]
    text_fields = ["display_name", "description"]
    list_fields = ["tags"]

    collection = globals.factory.new_collection(cid)
    document = collection.docs.get(docid)
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

    collection.docs.update(document)
    return redirect(url_for("collection_document", cid=cid, docid=docid))
