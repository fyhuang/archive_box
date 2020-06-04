import sys
import time
import traceback

from archive_box import archive_box_pb2 as pb2
from archive_box.collection import Collection
from archive_box.workers import Worker
from archive_box.sdid import StoredDataId
from archive_box.storage import LocalFileStorage
from archive_box.search import SearchIndex
from . import document_files
from .processor_state import *

# processing
from archive_box.processing.text import extract, summary

class ProcessorWorker(Worker):
    def __init__(self,
            state: ProcessorState,
            collection: Collection,
            local_store: LocalFileStorage,
            # TODO(fyhuang): generalize this storage
            remote_storage: LocalFileStorage,
            search_index: SearchIndex,
            ) -> None:
        Worker.__init__(self)
        self.state = state
        self.collection = collection
        self.local_store = local_store
        self.remote_storage = remote_storage
        self.search_index = search_index

    def run(self) -> None:
        while not self.should_quit():
            if self.state.peek_next_item() is None:
                self.state.wait_for_work(timeout=30.0)
            self.dequeue_and_process()

    def stop(self) -> None:
        Worker.stop(self)
        # TODO(fyhuang): encapsulate this better?
        with self.state.cv:
            self.state.cv.notify_all()

    def dequeue_and_process(self) -> None:
        next_item = self.state.peek_next_item()
        if next_item is None:
            return

        print("Processing {}".format(next_item))
        try:
            self.process_one(next_item)
            print("Done processing {}".format(next_item))
            self.state.delete_item(next_item)
        except Exception:
            print("Exception while processing {}".format(next_item))
            traceback.print_exc()
            time.sleep(5)

    def process_one(self, work_item: WorkItem) -> None:
        document: Optional[pb2.Document] = self.collection.docs.get(work_item.document_id)
        if document is None:
            raise RuntimeError("Document doesn't exist: {}".format(work_item.document_id))

        if work_item.action == "upload":
            for data_id in document_files.list_data_ids(document):
                self.remote_storage.upload(data_id, self.local_store.path_to(data_id))
        elif work_item.action == "auto_summarize":
            summary_fp = document_files.summarizable_text_data(document)
            if summary_fp is None:
                # not summarizable; nothing to do
                return
            summary_sdid = StoredDataId.from_strid(summary_fp.sdid)
            self.download_to_cache(summary_sdid)

            extracted_text = extract.extract_text(self.local_store.path_to(summary_sdid), summary_fp.mime)

            # TODO(fyhuang): it would be better if this were transactional
            document.auto_summary = summary.text_to_summary(extracted_text)
            document.auto_keywords[:] = summary.text_to_keywords(extracted_text)
            self.collection.docs.update(document)
        elif work_item.action == "index_for_search":
            self.search_index.update_index(document)
        else:
            print("Warning: unknown action {} while processing {}".format(work_item.action, work_item.document_id))

    def download_to_cache(self, data_id: StoredDataId) -> None:
        if self.local_store.contains(data_id):
            return

        dest_filename = self.local_store.get_temp_filename()
        self.remote_storage.download_to(data_id, dest_filename)
        self.local_store.move_inplace(data_id, dest_filename)
