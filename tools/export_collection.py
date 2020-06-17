import argparse
import sqlite3
import json

from google.protobuf import json_format

from archive_box.workspace import Workspace
from archive_box.factory import Factory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace')
    parser.add_argument('--export', required=False, dest="export_file")
    parser.add_argument('--import', required=False, dest="import_file")
    parser.add_argument('cid')

    args = parser.parse_args()

    workspace = Workspace.load_from_path(args.workspace)
    factory = Factory(
            workspace,
            None, # type: ignore
            lambda cid: sqlite3.connect(str(workspace.collection_db_path(cid)))
    )
    collection = factory.new_collection(args.cid)

    if args.export_file:
        print("Exporting to {}".format(args.export_file))

        all_docs_struct = []
        for doc in collection.docs.queryall():
            doc_json = json_format.MessageToJson(doc)
            doc_struct = json.loads(doc_json)
            all_docs_struct.append(doc_struct)

        with open(args.export_file, "w") as f:
            json.dump(all_docs_struct, f, indent=2)
    elif args.import_file:
        raise NotImplementedError()
    else:
        print("Nothing to do!")


if __name__ == "__main__":
    main()
