import argparse
import sqlite3

from archive_box.workspace import Workspace
from archive_box.factory import Factory
from archive_box.collection import document_files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace')
    parser.add_argument('cid')
    parser.add_argument('data_id')

    args = parser.parse_args()

    workspace = Workspace.load_from_path(args.workspace)
    factory = Factory(
            workspace,
            None, # type: ignore
            lambda cid: sqlite3.connect(str(workspace.collection_db_path(cid)))
    )
    collection = factory.new_collection(args.cid)

    results = collection.docs.queryall(filter=lambda doc: args.data_id in document_files.list_data_ids(doc))
    for doc in results:
        print(doc.id)


if __name__ == "__main__":
    main()
