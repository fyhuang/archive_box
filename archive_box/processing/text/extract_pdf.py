import itertools
from pathlib import Path
from typing import Any, Optional, List, NamedTuple

from pdfminer.layout import LAParams, LTContainer, LTPage, LTText, LTImage, LTTextBox # type: ignore
from pdfminer.converter import PDFLayoutAnalyzer # type: ignore
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter # type: ignore
from pdfminer.pdfpage import PDFPage # type: ignore

import enchant # type: ignore


_DICTIONARY = enchant.Dict("en_US")


class TextInfo(NamedTuple):
    text: str
    page_id: Any
    textbox_index: int
    # TODO(fyhuang): info about font size, etc.


class TextBoxConverter(PDFLayoutAnalyzer):
    def __init__(self, resource_mgr, laparams=None, imagewriter=None) -> None:
        PDFLayoutAnalyzer.__init__(self, resource_mgr, pageno=1, laparams=laparams)
        self.imagewriter = imagewriter

        self.curr_text = ""
        self.texts: List[TextInfo] = []
        
    def receive_layout(self, ltpage: LTPage):
        def render(item):
            if isinstance(item, LTContainer):
                for child in item:
                    render(child)
            elif isinstance(item, LTText):
                self.curr_text += item.get_text()
            
            if isinstance(item, LTTextBox):
                if len(self.curr_text) > 0:
                    self.texts.append(TextInfo(
                        self.curr_text, ltpage.pageid, len(self.texts)
                    ))
                self.curr_text = ""
            elif isinstance(item, LTImage):
                if self.imagewriter is not None:
                    self.imagewriter.export_image(item)
        
        render(ltpage)
        return
    
    def render_image(self, name, stream):
        if self.imagewriter is None:
            return
        PDFConverter.render_image(self, name, stream)
        
    def paint_path(self, gstate, stroke, fill, evenoff, path):
        return


def try_join_word(left: str, right: str) -> Optional[str]:
    # remove any hyphens
    if left.endswith('-'):
        left = left[:-1]
    
    # see if combined word is an english word
    combined = left + right
    if _DICTIONARY.check(combined):
        return combined
    else:
        return None


def reconstruct_paragraph(raw_text_block: str) -> str:
    """Reconstruct paragraph from a raw text block produced by pdfminer. Joins lines and un-hyphenates words."""
    result: List[str] = []
    for line in raw_text_block.splitlines():
        words = line.split()
        if len(words) == 0:
            continue
        
        if len(result) == 0:
            result.append(words[0])
        else:
            # try to join the first word of this line with the last word in the result
            joined = try_join_word(result[-1], words[0])
            if joined is not None:
                result.pop()
                result.append(joined)
            else:
                result.append(words[0])
            
        result.extend(words[1:])
    return ' '.join(result)


def extract_pdf_paragraphs(filepath: Path) -> List[str]:
    with filepath.open("rb") as pdf_file:
        resource_mgr = PDFResourceManager()
        converter = TextBoxConverter(resource_mgr, laparams=LAParams())
        interpreter = PDFPageInterpreter(resource_mgr, converter)
        for page in PDFPage.get_pages(pdf_file, maxpages=2, check_extractable=False):
            interpreter.process_page(page)
    
    # extract the text from "converter"
    raw_textboxes = []
    for key, group in itertools.groupby(converter.texts, key=lambda ti: (ti.page_id, ti.textbox_index)):
        raw_textboxes.append(''.join(ti.text for ti in group))

    return [reconstruct_paragraph(raw) for raw in raw_textboxes]
