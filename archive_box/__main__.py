import argparse
import sqlite3
from pathlib import Path

from . import webapp
from .workspace import Workspace
from .factory import Factory
from .workers import manager as w_manager


def main() -> None:
    parser = argparse.ArgumentParser(description='Archive Box')
    parser.add_argument('--workspace', type=str, nargs=1, required=True)

    args = parser.parse_args()
    workspace_root = Path(args.workspace[0])
    workspace = Workspace.load_from_path(workspace_root)

    # TODO(fyhuang): implement connection pooling that stores connection in flask.g
    scanner_cpool = lambda: sqlite3.connect(str(workspace.scanner_db_path()), check_same_thread=False)
    collection_cpool = lambda cid: sqlite3.connect(str(workspace.collection_db_path(cid)), check_same_thread=False)
    factory = Factory(workspace, scanner_cpool, collection_cpool)
    factory.first_time_setup()

    # Start workers
    w_manager.start_worker(factory.new_scanner_worker())
    for cid in workspace.cids():
        print("Starting worker for {}".format(cid))
        worker = factory.new_processor_worker(cid)
        w_manager.start_worker(worker, "ProcessorWorker_{}".format(cid))

    # Run the web app
    webapp.init(workspace, factory)
    webapp.run()

    # Stop workers
    print("Waiting for workers to stop")
    w_manager.stop_all_workers()


if __name__ == "__main__":
    main()
