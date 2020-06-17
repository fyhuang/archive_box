import functools
import datetime
import shutil
import urllib.parse
from pathlib import Path
from typing import cast, Optional, Union, Tuple, List, Set, Dict

import requests

from . import util, storage, scanner
from . import archive_box_pb2 as pb2
from .collection import Collection, ProcessorState, document_files
from .sdid import file_to_sdid


def _now_ms() -> int:
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000.0)


def _is_url(url_or_path: Union[Path, str]) -> bool:
    if isinstance(url_or_path, Path):
        return False
    if "://" in url_or_path:
        return True
    return False


class ArchiveBoxApi(object):
    def __init__(self,
            collection: Collection,
            processor_state: ProcessorState,
            local_store: storage.LocalFileStorage,
            ) -> None:
        self.collection = collection
        self.processor_state = processor_state
        self.local_store = local_store

    # TODO(fyhuang): break these out into a "Loader" class?
    def put_url_into_store(self, url) -> Tuple[str, str, str]:
        dest_filename = self.local_store.get_temp_filename()

        response = requests.get(url)
        orig_mime = response.headers["Content-Type"].partition(';')[0]
        with dest_filename.open('wb') as f:
            for chunk in response.iter_content(1024 * 1024):
                f.write(chunk)

        # TODO(fyhuang): use filename from Content-Disposition if there is one
        url_components = urllib.parse.urlparse(url)

        sdid = file_to_sdid(dest_filename)
        self.local_store.move_inplace(sdid, dest_filename)
        return sdid, Path(url_components.path).name, orig_mime

    def put_local_file_into_store(self, base_path: Optional[Path], filepath: Union[str, Path]) -> Tuple[str, str, str]:
        filepath = Path(filepath)
        if base_path is None:
            base_path = Path(filepath.anchor)

        sdid = file_to_sdid(filepath)
        self.local_store.upload(sdid, filepath)
        return sdid, str(filepath.relative_to(base_path)), document_files.guess_mimetype(filepath)

    def create_document(self,
            url_or_path: Union[str, Path],
            needs_review: bool = True,
            doc_title: Optional[str] = None,
            doc_tags: Set[str] = set(),
            doc_description: str = "",
            user_metadata: Dict[str, str] = {},
            orig_url: Optional[str] = None,
            # for local files, the base directory which original filenames will be calculated relative to
            base_path: Optional[Path] = None,
            skip_duplicates: bool = True,
            ) -> Optional[str]:

        if _is_url(url_or_path):
            put_file_func = self.put_url_into_store
        else:
            put_file_func = functools.partial(self.put_local_file_into_store, base_path)

        if orig_url is None:
            # generate the original URL from url_or_path
            if _is_url(url_or_path):
                orig_url = cast(str, url_or_path)
            else:
                orig_url = Path(url_or_path).resolve().as_uri()

        # optionally check for duplicates
        if skip_duplicates:
            # TODO(fyhuang): index
            other_docs = self.collection.docs.queryall(filter=lambda d: d.orig_url == orig_url)
            if len(other_docs) > 0:
                return None

        # download the file and create the document
        sdid, orig_filename, orig_mime = put_file_func(url_or_path)

        document = pb2.Document()
        document.id = util.new_id()
        document.data.main.sdid = sdid
        document.data.main.mime = orig_mime
    
        document.needs_review = needs_review
        document.creation_time_ms = _now_ms()
        document.last_mod_time_ms = _now_ms()

        document.orig_filename = orig_filename
        document.orig_url = orig_url
    
        if doc_title is not None:
            document.title = doc_title
        else:
            document.title = orig_filename

        document.tags.extend(doc_tags)
        document.description = doc_description
        document.metadata.update(user_metadata)

        self.collection.docs.update(document)
        self.first_time_process(document.id)
        return document.id


    def first_time_process(self, doc_id: str) -> None:
        self.processor_state.add_work_item(doc_id, "transcode_video") # transcode first, in case user doesn't want to keep original
        self.processor_state.add_work_item(doc_id, "upload")
        self.processor_state.add_work_item(doc_id, "auto_summarize")
        self.processor_state.add_work_item(doc_id, "index_for_search")

    def reprocess(self, doc_id: str) -> None:
        # TODO(fyhuang): re-transcode video in case the original is still around
        self.processor_state.add_work_item(doc_id, "auto_summarize")
        self.processor_state.add_work_item(doc_id, "index_for_search")
