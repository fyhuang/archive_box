from flask import Flask, request

from archive_box.workspace import Workspace
from archive_box.factory import Factory


class Globals(object):
    def __init__(self):
        self.workspace: Workspace = None # type: ignore
        self.factory: Factory = None # type: ignore


app = Flask(__name__)
globals = Globals()


def run(workspace: Workspace, factory: Factory):
    globals.workspace = workspace
    globals.factory = factory
    app.run(port=workspace.config["server"]["port"])


def shutdown() -> None:
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


# import child views
from . import home, collection
