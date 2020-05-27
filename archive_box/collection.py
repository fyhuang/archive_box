import sqlite3

from . import archive_box_pb2 as pb2
from .globals import app, globals


class Collection(object):
    def __init__(self, internal_path, node_config, config) -> None:
        self.config = config
        conn = sqlite3.connect(internal_path / "{}.db".format(self.config["id"]))

        # TODO(fyhuang): don't need to create SyncedDb (and run CREATE TABLE) every request
        self.db = SyncedDb(self.conn, node_config, [pb2.Collection, pb2.Document])

    @staticmethod
    def from_id(cid: str):
        with globals.lock:
            internal = globals.internal
            node_config = globals.node_config
            config = globals.config["collections"][cid]
        return Collection(internal, node_config, config)


@app.route("/c/<cid>/")
def collection_index(cid: str):
    c = Collection.from_id(cid)
    collection = c.db.get_table("Collection").get(cid)
    return collection.display_name
