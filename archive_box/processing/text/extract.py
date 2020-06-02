# Extract text from documents
from pathlib import Path
from typing import Union

import pdfminer.high_level # type: ignore

def extract_pdf_text(filepath: Path) -> str:
    return pdfminer.high_level.extract_text(str(filepath), maxpages=2)

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
