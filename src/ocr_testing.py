from src.ocr_highlighter.ocr_highlighter import highlight_sentences_with_ocr
from src.config import CFG

_pdf_path = "/Users/eduard_babayan/Documents/context_highlighter/Document.pdf"

sentences_to_highlight = [
    "WINSLOW MS LGCP GRTH",
]

target_page = 22

highlight_sentences_with_ocr(
    _pdf_path, 
    CFG.row_highlighter_pdf_path,
    target_page,
    sentences_to_highlight
)
