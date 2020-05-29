from flask import Flask, request

from archive_box.workspace import Workspace
from archive_box.factory import Factory


app = Flask(__name__)
workspace: Workspace = None # type: ignore
factory: Factory = None # type: ignore


def run(ws: Workspace, f: Factory):
    global workspace, factory
    workspace = ws
    factory = f
    app.run(port=ws.config["server"]["port"])


def shutdown() -> None:
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


# import child views
from . import home, collection
