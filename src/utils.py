import json


def load_table_metadata(file_path):
    """
    Load table metadata from a JSON file to avoid running the extraction pipeline repeatedly.
    """
    with open(file_path, "r") as f:
        saved_tables = json.load(f)
    return saved_tables