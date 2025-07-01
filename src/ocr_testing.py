from src.ocr_highlighter.ocr_highlighter import highlight_sentences_with_ocr
from src.config import CFG


_pdf_path = "/Users/eduard_babayan/Documents/epam_projects/context_highlighter/Document.pdf"

sentences_to_highlight = [
    "402",
]

target_page = 8

boxes = highlight_sentences_with_ocr(
    _pdf_path,
    target_page,
    sentences_to_highlight,
    table=True,
    table_index=0,
    output_path=CFG.row_highlighter_pdf_path,
)

print('')