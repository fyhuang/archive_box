# Extract text from documents
from pathlib import Path
from typing import Optional, Union

from archive_box.collection import document_files

from .extract_pdf import extract_pdf_paragraphs

def extract_pdf_text(filepath: Path) -> str:
    return '\n\n'.join(extract_pdf_paragraphs(filepath))

EXTRACTORS = {
    "application/pdf": extract_pdf_text,
}

def extract_text(input_filepath: Union[str, Path], mimetype: Optional[str] = None) -> str:
    filepath = Path(input_filepath)
    if mimetype is None or len(mimetype) == 0:
        mimetype = document_files.guess_mimetype(filepath)

    if mimetype in EXTRACTORS:
        return EXTRACTORS[mimetype](filepath)
    else:
        raise NotImplementedError("Cannot extract text from document of type {}".format(mimetype))
