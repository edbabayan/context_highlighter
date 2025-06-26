from pathlib import Path

class CFG:
    root = Path(__file__).resolve().parent.parent.absolute()

    temp_dir = root.joinpath("temp")
    temp_pdf_path = temp_dir.joinpath("temp_page.pdf")
    tables_dir = temp_dir.joinpath("tables.json")
    table_images_dir = temp_dir.joinpath("tables_tables.png")

    row_highlighter_pdf_path = root.joinpath("highlighted_row.pdf")