from . import manager
from .server import app

@app.route("/c/<cid>", methods=["GET"])
def collection_index(cid: str):
    db = manager.get().col(cid)
    collection = db.get_table("Collection").get(cid)
    return collection.display_name

@app.route("/c/<cid>", methods=["POST"])
def collection_post(cid: str):
    pass
