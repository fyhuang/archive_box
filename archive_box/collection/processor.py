import os
import sys
import time
import traceback
from typing import Tuple, List
from pathlib import Path

from archive_box import archive_box_pb2 as pb2
from archive_box.collection import Collection
from archive_box.workers import Worker
from archive_box.sdid import StoredDataId, file_to_sdid
from archive_box.storage import LocalFileStorage
from archive_box.search import SearchIndex
from . import document_files
from .processor_state import *

# processing
from archive_box.processing.text import extract, summary
from archive_box.processing.video import transcode
from archive_box.processing.video.config import TargetRepresentation


def sort_transcode_outputs_into_filegroup(filegroup: pb2.FileGroup, outputs: transcode.OutputsDict) -> List[Tuple[StoredDataId, Path]]:
    if len(outputs) == 0:
        return []

    best_output = sorted(set(outputs.keys()) - set("original"))[-1]
    print(best_output)
    if "original" not in outputs:
        # replace the "main" data with the best output
        filegroup.main.sdid = file_to_sdid(outputs[best_output]).to_strid()
        filegroup.main.mime = document_files.guess_mimetype(outputs[best_output])

    # fill in media formats
    files_to_move = []
    filegroup.media_formats.clear()
    for key, value in outputs.items():
        if isinstance(key, TargetRepresentation):
            str_key = key.to_str()
        else:
            str_key = key

        data_id = file_to_sdid(value)
        filegroup.media_formats[str_key].sdid = data_id.to_strid()
        filegroup.media_formats[str_key].mime = document_files.guess_mimetype(value)
        files_to_move.append((data_id, value))

    return files_to_move


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

    # TODO(fyhuang): how to split this up more cleanly and testably?
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
        elif work_item.action == "transcode_video":
            if not document.data.main.mime.startswith("video/"):
                # not a video, nothing to do
                return

            if self.collection.config.transcode is None:
                # no transcoding config
                # TODO(fyhuang): provide a default transcoding config
                print("Warning: video {} can be transcoded but no transcode config".format(work_item.document_id))
                return

            input_path = self.local_store.path_to(StoredDataId.from_strid(document.data.main.sdid))
            output_dir = self.local_store.tempdir / document.data.main.sdid
            os.makedirs(output_dir, exist_ok=True)

            print("Transcoding {}".format(work_item))
            outputs = transcode.transcode_all(input_path, output_dir, self.collection.config.transcode)
            files_to_move = sort_transcode_outputs_into_filegroup(document.data, outputs)
            self.collection.docs.update(document)

            for data_id, path in files_to_move:
                self.local_store.move_inplace(data_id, path)
        else:
            print("Warning: unknown action {} while processing {}".format(work_item.action, work_item.document_id))

    def download_to_cache(self, data_id: StoredDataId) -> None:
        if self.local_store.contains(data_id):
            return

        dest_filename = self.local_store.get_temp_filename()
        self.remote_storage.download_to(data_id, dest_filename)
        self.local_store.move_inplace(data_id, dest_filename)
