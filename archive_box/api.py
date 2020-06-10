import shutil
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional, List, Dict

from . import storage, scanner
from .collection import Collection, ProcessorState
from .sdid import file_to_sdid


class ArchiveBoxApi(object):
    def __init__(self,
            collection: Collection,
            processor_state: ProcessorState,
            local_store: storage.LocalFileStorage,
            ) -> None:
        self.collection = collection
        self.processor_state = processor_state
        self.local_store = local_store

    def _add_from_store(self, sdid: str, orig_filename: str) -> None:
        doc_id = self.collection.add_document(sdid, orig_filename)
        self.first_time_process(doc_id)

    def add_document_from_file(self, filepath: Path, base_path: Optional[Path] = None) -> None:
        if base_path is None:
            base_path = Path(filepath.anchor)

        sdid = file_to_sdid(filepath)
        self.local_store.upload(sdid, filepath)
        self._add_from_store(sdid, str(filepath.relative_to(base_path)))

    def add_document_from_url(self, url: str) -> None:
        dest_filename = self.local_store.get_temp_filename()
        with urllib.request.urlopen(url) as response:
            with dest_filename.open('wb') as f:
                shutil.copyfileobj(response, f)

        # TODO(fyhuang): use filename from Content-Disposition if there is one
        url_components = urllib.parse.urlparse(url)

        sdid = file_to_sdid(dest_filename)
        self.local_store.move_inplace(sdid, dest_filename)
        # TODO(fyhuang): include any document metadata fields from the caller
        self._add_from_store(sdid, Path(url_components.path).name)

    def create_document(self,
            urls_or_paths: List[str],
            document_info: Dict[str, str],
            user_metadat: Dict[str, str],
            # for local files, the base directory which original filenames will be calculated relative to
            base_path: Optional[Path] = None,
            ) -> None:
        pass

    def first_time_process(self, doc_id: str) -> None:
        self.processor_state.add_work_item(doc_id, "transcode_video") # transcode first, in case user doesn't want to keep original
        self.processor_state.add_work_item(doc_id, "upload")
        self.processor_state.add_work_item(doc_id, "auto_summarize")
        self.processor_state.add_work_item(doc_id, "index_for_search")

    def reprocess(self, doc_id: str) -> None:
        self.processor_state.add_work_item(doc_id, "auto_summarize")
        self.processor_state.add_work_item(doc_id, "index_for_search")
