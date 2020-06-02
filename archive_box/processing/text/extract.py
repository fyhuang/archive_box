# Extract text from documents
from pathlib import Path
from typing import Union

from .extract_pdf import extract_pdf_paragraphs

def extract_pdf_text(filepath: Path) -> str:
    return '\n\n'.join(extract_pdf_paragraphs(filepath))

_EXTRACTORS = {
    ".pdf": extract_pdf_text,
}

def extract_text(input_filepath: Union[str, Path]) -> str:
    filepath = Path(input_filepath)
    ext = filepath.suffix
    if ext in _EXTRACTORS:
        return _EXTRACTORS[ext](filepath)
    else:
        return ""
