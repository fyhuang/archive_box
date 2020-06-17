import argparse
import sqlite3
import json

import cfgparse

from archive_box.config import B2Credentials
from archive_box.workspace import Workspace
from archive_box.factory import Factory
from archive_box.sync.remote_sync_b2 import RemoteSyncB2


def sync_collection(workspace: Workspace, factory: Factory, cid: str) -> None:
    config = workspace.collection_config(cid)

    if config.sync == "none":
        print("Skipping {} (no sync method defined)".format(cid))
        return
    elif config.sync == "b2":
        assert config.sync_b2_bucket_name is not None
        syncer = RemoteSyncB2(
                factory,
                cfgparse.mapping_to_nt(workspace.config["b2_credentials"], B2Credentials),
                config.sync_b2_bucket_name,
        )
    else:
        raise RuntimeError("Unknown sync method {}".format(config.sync))

    print("Syncing {} with method {}".format(cid, config.sync))
    syncer.sync(cid)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace')

    args = parser.parse_args()

    workspace = Workspace.load_from_path(args.workspace)
    factory = Factory.with_naive_cpools(workspace)

    for cid in workspace.cids():
        sync_collection(workspace, factory, cid)


if __name__ == "__main__":
    main()
