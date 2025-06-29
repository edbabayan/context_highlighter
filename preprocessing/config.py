from pathlib import Path

class CFG:
    root = Path(__file__).resolve().parent.parent.absolute()

    data_dir = root.joinpath("data")
