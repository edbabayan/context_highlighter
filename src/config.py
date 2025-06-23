from pathlib import Path

class CFG:
    root = Path(__file__).resolve().parent.parent.absolute()
    tables_dir = root.joinpath("tables.json")
