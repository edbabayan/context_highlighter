from src.highlighters.row_highlighter import highlight_phrase_in_table, get_table_info_for_page
from src.config import CFG

_pdf_path = "/Users/eduard_babayan/Documents/context_highlighter/Document.pdf"

target_phrase = "Employer-related common stock funds"
target_page = 17
table_index = 0  # First table on the page (top-left)


# Show table info for the target page
get_table_info_for_page(CFG.tables_dir, target_page)

# Highlight phrase in the specified table
highlight_phrase_in_table(
    _pdf_path, 
    CFG.row_highlighter_pdf_path, 
    target_page,
    target_phrase.strip(),
    table_index,
    CFG.tables_dir
)