from src.pymupdf_highlighter.row_highlighter import highlight_sentences_on_page
from src.config import CFG

_pdf_path = "/Users/eduard_babayan/Documents/epam_projects/context_highlighter/Document.pdf"

sentences_to_highlight = [
    "Financial statements"
]

target_page = 20

boxes = highlight_sentences_on_page(
    _pdf_path,
    target_page,
    sentences_to_highlight,
CFG.row_highlighter_pdf_path,
)

print('')