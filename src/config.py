from pathlib import Path

class CFG:
    root = Path(__file__).resolve().parent.parent.absolute()
    tables_dir = root.joinpath("tables.json")

    row_highlighter_pdf_path = root.joinpath("highlighted_row.pdf")