import os
import secrets
from pathlib import Path

import toml
from flask import Flask, request


def run_server(workspace: Path) -> None:
    app.run(port=self.config["server"]["port"])

def shutdown_server() -> None:
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()



@app.route("/hello")
def hello():
    return "World"

@app.route("/resync")
def resync():
    global server
    sync_file = server.internal / "sync.tmp"
    with open(sync_file, "wb") as f:
        pass
    shutdown_server()


class Server(object):
    def __init__(self, workspace: Path) -> None:

    def maybe_sync(self) -> None:
        if not (self.internal / "sync.tmp").exists():
            return

        # sync needs to be performed
        for _, c in self.collections.items():
            c.sync()

    def collection(self, id: str) -> Collection:
        return Collection(self.internal, self.config["collections"][id])

    def run(self) -> None:
