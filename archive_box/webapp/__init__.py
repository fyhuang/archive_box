from flask import Flask, abort, request, Response, send_file
from werkzeug import wsgi

from archive_box import archive_box_pb2 as pb2

from archive_box.workspace import Workspace
from archive_box.factory import Factory
from archive_box.storage import LocalFileStorage

from .streaming import serve_file_range


class Globals(object):
    def __init__(self):
        self.workspace: Workspace = None # type: ignore
        self.factory: Factory = None # type: ignore


app = Flask(__name__)
globals = Globals()


def _file_pointer_from_where(filegroup: pb2.FileGroup, where: str) -> pb2.FilePointer:
    # TODO(fyhuang): replace with a more generic solution
    if where.startswith("media_formats."):
        _, _, mf_name = where.partition(".")
        return filegroup.media_formats[mf_name]
    return getattr(filegroup, where)


def _local_store_app(cid: str):
    def serve_file(docid: str):
        local_store = globals.factory.new_collection_storage(cid)
        if not isinstance(local_store, LocalFileStorage):
            abort(500)

        collection = globals.factory.new_collection(cid)
        doc = collection.docs.get(docid)
        if doc is None:
            abort(404)

        which_file_pointer = request.args.get("which", "main")
        file_pointer = _file_pointer_from_where(doc.data, which_file_pointer)

        path = local_store.path_to(file_pointer.sdid)
        print("Serving SDID {} from path {}".format(file_pointer.sdid, path))
        return serve_file_range(path, mimetype=file_pointer.mime)

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
        store_app = _local_store_app(cid)
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
            use_reloader=False,
            use_debugger=True,
            threaded=True,
    )


def shutdown() -> None:
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


# import child views
from . import home, collection
