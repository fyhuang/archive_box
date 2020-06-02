from flask import Flask, abort, request, send_file
from werkzeug import wsgi

from archive_box.workspace import Workspace
from archive_box.factory import Factory
from archive_box.storage import LocalFileStorage
from archive_box.sdid import StoredDataId


class Globals(object):
    def __init__(self):
        self.workspace: Workspace = None # type: ignore
        self.factory: Factory = None # type: ignore


app = Flask(__name__)
globals = Globals()


def local_store_app(cid: str):
    def serve_file(docid: str):
        local_store = globals.factory.new_collection_storage(cid)
        if not isinstance(local_store, LocalFileStorage):
            abort(500)

        collection = globals.factory.new_collection(cid)
        doc = collection.db.get_table("Document").get(docid)
        if doc is None:
            abort(404)

        path = local_store.path_to(StoredDataId.from_strid(doc.data.main.sdid))
        return send_file(path, mimetype=doc.data.main.mime)

    app = Flask("local_store_" + cid)
    app.add_url_rule("/<docid>", "serve_file", serve_file)
    return app


class LocalStoreDispatcher(object):
    def __init__(self, default_app) -> None:
        self.default_app = default_app

    def __call__(self, environ, start_response):
        prefix = wsgi.peek_path_info(environ)
        if prefix != "local":
            return self.default_app(environ, start_response)
        _ = wsgi.pop_path_info(environ)
        cid = wsgi.pop_path_info(environ)
        store_app = local_store_app(cid)
        return store_app(environ, start_response)


def init(workspace: Workspace, factory: Factory) -> None:
    globals.workspace = workspace
    globals.factory = factory
    factory.set_collection_storage_url_pattern("/local/{cid}")


def run() -> None:
    dispatcher = LocalStoreDispatcher(app)
    #app.run(port=workspace.config["server"]["port"])
    from werkzeug.serving import run_simple
    run_simple(
            "localhost",
            globals.workspace.config["server"]["port"],
            dispatcher,
            use_reloader=True,
            use_debugger=True
    )


def shutdown() -> None:
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


# import child views
from . import home, collection
