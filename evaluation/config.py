from pathlib import Path

class CFG:
    root = Path(__file__).resolve().parent.parent.absolute()

    data_dir = root.joinpath("data")
    pdf_dir = data_dir.joinpath("pdfs")
    json_dir = data_dir.joinpath("json_files")
    
    # Output directories
    processed_json_dir = data_dir.joinpath("processed_json")
