import json, pathlib

def write_json(listings, path):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(listings, f, indent=2)
