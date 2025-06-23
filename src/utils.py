import json

def load_table_metadata(file_path):
    with open(file_path, "r") as f:
        saved_tables = json.load(f)
    return saved_tables