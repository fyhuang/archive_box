from . import manager
from .server import app

@app.route("/c/<cid>", methods=["GET"])
def collection_index(cid: str):
    collection = manager.get().col(cid)
    return collection.config["display_name"]
