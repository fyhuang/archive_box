from pathlib import Path
from typing import Union, Optional, List

from archive_box import archive_box_pb2 as pb2
from archive_box.sdid import StoredDataId

from archive_box.processing.text import extract


_EXT_TO_MIMETYPE = {
        ".aac": "audio/aac",
        ".avi": "video/x-msvideo",
        ".epub": "application/epub+zip",
        ".gif": "image/gif",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".mov": "video/quicktime",
        ".mp3": "audio/mpeg",
        ".mp4": "video/mp4",
        ".mpeg": "video/mpeg",
        ".mkv": "video/webm", # TODO(fyhuang): not sure if this is 100% accurate
        ".oga": "audio/ogg",
        ".ogv": "video/ogg",
        ".opus": "audio/opus",
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
        ".ts": "video/mp2t",
        ".wav": "audio/wav",
        ".weba": "audio/webm",
        ".webm": "video/webm",
        ".webp": "image/webp",
        ".wmv": "video/x-ms-wmv",
}


def guess_mimetype(filepath: Union[str, Path]) -> str:
    # TODO(fyhuang): for containers (mp4/mkv), be smarter about whether they contain video or audio
    ext = Path(filepath).suffix.lower()
    return _EXT_TO_MIMETYPE[ext]


def list_data_ids_from_file_group(file_group: pb2.FileGroup) -> List[StoredDataId]:
    result = [StoredDataId.from_strid(file_group.main.sdid)]
    if file_group.HasField("thumbnail"):
        result.append(StoredDataId.from_strid(file_group.thumbnail.sdid))
    if file_group.HasField("preview"):
        result.append(StoredDataId.from_strid(file_group.preview.sdid))
    return result


def list_data_ids(doc: pb2.Document) -> List[StoredDataId]:
    return list_data_ids_from_file_group(doc.data)


def summarizable_text_data(doc: pb2.Document) -> Optional[pb2.FilePointer]:
    if doc.data.main.mime in extract.EXTRACTORS.keys():
        return doc.data.main
    return None
