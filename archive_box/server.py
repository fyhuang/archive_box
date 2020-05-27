import os
import secrets
from pathlib import Path

import toml
from flask import Flask, request

from . import manager


app = Flask(__name__)


def run(config) -> None:
    app.run(port=config["server"]["port"])

def shutdown() -> None:
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route("/hello")
def hello():
    return "World"

@app.route("/resync")
def resync():
    sync_file = manager.get().internal / "sync.tmp"
    with open(sync_file, "wb") as f:
        pass
    shutdown_server()


# other views
from . import collection
