from src.highlighters.row_highlighter import highlight_sentences_on_page
from src.config import CFG

_pdf_path = "/Users/eduard_babayan/Documents/context_highlighter/Document.pdf"

sentences_to_highlight = [
    "Employer-related common stock funds",
]
target_page = 17

highlight_sentences_on_page(
    _pdf_path, 
    CFG.row_highlighter_pdf_path, 
    target_page,
    sentences_to_highlight
)