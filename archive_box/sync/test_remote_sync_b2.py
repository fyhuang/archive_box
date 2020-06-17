import unittest
import io
import toml
from pathlib import Path

from b2sdk import v1 as b2 # type: ignore
from b2sdk import raw_simulator # type: ignore

from .remote_sync_b2 import *
from archive_box.config import B2Credentials
from archive_box.workspace import Workspace
from archive_box.factory import Factory
import archive_box.archive_box_pb2 as pb2

from dtsdb import ProtoTable, SyncedDb


class RemoteSyncB2IntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sim = raw_simulator.RawSimulator()
        account_id, master_key = self.sim.create_account()
        credentials = B2Credentials(account_id, master_key)

        # TODO(fyhuang): can this setup be done without creating an entire fake workspace?
        self.tempdir = tempfile.TemporaryDirectory()
        (Path(self.tempdir.name) / "config.toml").write_text(toml.dumps({
            "collections": {
                "abc123": {
                    "display_name": "Test Collection",
                    "storage": "local",
                    "sync": "b2",
                    "local_storage": {
                        "root": self.tempdir.name + "/abc123",
                    },
                },
            },
            # TODO(fyhuang): make this unnecessary
            "server": {
                "inbox": self.tempdir.name + "/inbox",
            },
        }))

        self.workspace = Workspace.load_from_path(self.tempdir.name)
        self.factory = Factory.with_naive_cpools(self.workspace)
        self.factory.first_time_setup()
        self.sync = RemoteSyncB2(self.factory, credentials, "test-bucket", self.sim)
        self.sync._auth_if_needed()
        self.bucket = self.sync.api.create_bucket("test-bucket", "allPrivate")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_no_remote_file(self) -> None:
        self.sync.sync("abc123")
        memory_dest = b2.DownloadDestBytes()
        # will fail with exception if remote file doesn't exist
        self.bucket.download_file_by_name("db/abc123.db", memory_dest)

    def test_with_remote_file(self) -> None:
        # Create other DB with some changes
        other_doc = pb2.Document()
        other_doc.id = "other_doc"
        other_doc.data.main.sdid = ""
        other_doc.creation_time_ms = 0
        other_doc.last_mod_time_ms = 0
        other_doc.needs_review = False
        other_doc.title = "Other Doc"

        other_db_path = Path(self.tempdir.name) / "_other.db"
        with sqlite3.connect(str(other_db_path)) as conn:
            docs_table = ProtoTable(conn, pb2.Document)
            docs_table.first_time_setup()
            other_sdb = SyncedDb(conn, Workspace.new_node_config(), [docs_table])
            other_sdb.first_time_setup()
            
            docs_table.update(other_doc)

        self.bucket.upload_local_file(
            local_file=str(other_db_path),
            file_name="db/abc123.db",
        )

        # Add some new changes to our DB too
        our_doc = pb2.Document()
        our_doc.id = "our_doc"
        our_doc.data.main.sdid = ""
        our_doc.creation_time_ms = 0
        our_doc.last_mod_time_ms = 0
        our_doc.needs_review = False
        our_doc.title = "Our Doc"
        self.factory.new_collection("abc123").docs.update(our_doc)

        # Synchronize
        self.sync.sync("abc123")

        # Check that remote changes made it into our DB
        self.assertEqual(
            other_doc,
            self.factory.new_collection("abc123").docs.get("other_doc"),
        )

        # Check that our DB made it into B2
        memory_dest = b2.DownloadDestBytes()
        self.bucket.download_file_by_name("db/abc123.db", memory_dest)
        self.assertEqual(
            self.workspace.collection_db_path("abc123").read_bytes(),
            memory_dest.get_bytes_written(),
        )
