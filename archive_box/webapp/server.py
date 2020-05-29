import os
import secrets
from pathlib import Path

import toml
from flask import Flask, request, render_template

#from . import manager, ingestor


app = Flask(__name__)


def run(config) -> None:
    app.run(port=config["server"]["port"])

def shutdown() -> None:
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

#@app.route("/")
#def index() -> str:
#    collections = [{"id": key, "name": value["display_name"]} for key, value in manager.get().config.get("collections", {}).items()]
#    inbox_path = ingestor.get().inbox_path
#    waiting_files = [
#        {"path": value.relative_to(inbox_path), "sdid": key.to_strid()} for key, value in ingestor.get().get_waiting().items()
#    ]
#
#    return render_template(
#        'index.html',
#        collections=collections,
#        waiting_files=waiting_files
#    )


# other views
from . import collection
