from src.pymupdf_highlighter.row_highlighter import highlight_sentences_on_page
from src.config import CFG

_pdf_path = "/Users/eduard_babayan/Documents/epam_projects/context_highlighter/data/pdfs/02-15-2024-FR-(Final).pdf"

sentences_to_highlight = [
    "Disaster Assistance Loans - SBA",
    "270.7"
]

target_page = 91

boxes = highlight_sentences_on_page(
    _pdf_path, 
    CFG.row_highlighter_pdf_path, 
    target_page,
    sentences_to_highlight
)

print('')