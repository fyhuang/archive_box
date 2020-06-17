import argparse
import sqlite3
import json

from google.protobuf import json_format

from archive_box.workspace import Workspace
from archive_box.factory import Factory
from archive_box.collection import document_files


def gc_collection(cid: str, factory: Factory):
    # make sure that nothing is being processed
    pstate = factory.new_processor_state(cid)
    if pstate.get_queue_size() > 0:
        print("Warning: not GC-ing {} because there are unfinished processing items".format(cid))
        return

    storage = factory.new_collection_storage(cid)
    stored_data_ids = set(storage.list())

    doc_data_ids = set()
    collection = factory.new_collection(cid)
    for doc in collection.docs.queryall():
        doc_data_ids |= document_files.list_data_ids(doc)

    # remove any stored_data_ids that are not referenced
    unreferenced_sdids = stored_data_ids - doc_data_ids
    print("Cleaning up {} unreferenced IDs:".format(len(unreferenced_sdids)))
    for sdid in unreferenced_sdids:
        print("  {}".format(sdid))
        storage.delete(sdid)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace')
    parser.add_argument('cids', nargs='+')

    args = parser.parse_args()

    workspace = Workspace.load_from_path(args.workspace)
    factory = Factory(
            workspace,
            lambda: sqlite3.connect(str(workspace.scanner_db_path())),
            lambda cid: sqlite3.connect(str(workspace.collection_db_path(cid))),
    )

    # TODO(fyhuang): clear the local store if there are no items being processed

    for cid in args.cids:
        gc_collection(cid, factory)


if __name__ == "__main__":
    main()
