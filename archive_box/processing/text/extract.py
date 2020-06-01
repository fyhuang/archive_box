# Extract text from documents
from pathlib import Path

import pdfminer.high_level # type: ignore

def extract_pdf_text(filepath: Path) -> str:
    return pdfminer.high_level.extract_text(filepath)

_EXTRACTORS = {
    ".pdf": extract_pdf_text,
}

def extract_text(filepath: Path) -> str:
    ext = filepath.suffix
    if ext in _EXTRACTORS:
        return _EXTRACTORS[ext](filepath)
    else:
        return ""
