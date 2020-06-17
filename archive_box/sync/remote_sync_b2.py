import sqlite3
import tempfile
from pathlib import Path
from typing import Any, NamedTuple

from b2sdk import v1 as b2 # type: ignore
from b2sdk.v1.exception import FileNotPresent, MissingAccountData # type: ignore

from archive_box.config import B2Credentials
from archive_box.factory import Factory


class RemoteSyncB2(object):
    def __init__(self, factory: Factory, credentials: B2Credentials, bucket_name: str, b2_raw_api: Any = None):
        self.credentials = credentials
        self.bucket_name = bucket_name
        # TODO(fyhuang): maybe a circular dependency later if we want to include sync in factory
        self.factory = factory

        # TODO(fyhuang): cache auth token between runs?
        self.info = b2.InMemoryAccountInfo()
        self.api = b2.B2Api(self.info, raw_api=b2_raw_api)

    def _auth_if_needed(self) -> None:
        try:
            self.info.get_account_auth_token()
            return
        except MissingAccountData:
            pass

        self.api.authorize_account(
                "production",
                self.credentials.application_key_id,
                self.credentials.application_key
        )

    def sync(self, cid: str) -> None:
        # TODO(fyhuang): create a syncer per-collection, don't take CID as input
        self._auth_if_needed()
        collection = self.factory.new_collection(cid)

        remote_target_name = "db/{}.db".format(cid)
        bucket = self.api.get_bucket_by_name(self.bucket_name)

        with tempfile.TemporaryDirectory() as tempdir:
            local_target_path = Path(tempdir) / "temp_{}.db".format(cid)
            download_dest = b2.DownloadDestLocalFile(local_target_path)
            try:
                # TODO(fyhuang): check the returned info?
                bucket.download_file_by_name(remote_target_name, download_dest)
                # Perform the sync
                with sqlite3.connect(str(local_target_path)) as other_conn:
                    collection.synced_db.sync(other_conn)
            except FileNotPresent:
                # This is fine, we'll just upload our copy of the db
                pass

            # Our DB file now has the latest changes, and can be uploaded
            bucket.upload_local_file(
                local_file=self.factory.workspace.collection_db_path(cid),
                file_name=remote_target_name,
                # TODO(fyhuang): any file infos needed?
                # TODO(fyhuang): turn off auto_continue?
            )
