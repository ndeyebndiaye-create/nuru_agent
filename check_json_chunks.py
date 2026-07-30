import json
from pathlib import Path
from collections import defaultdict

chunks_dir = Path("data/processed/chunks")
file_chunks = defaultdict(int)

for p in chunks_dir.glob("*.json"):
    filename = "_".join(p.stem.split("_")[:-2]) + ".pdf" # rough approximation, might not work for files without two timestamp parts
    # Better to just load the JSON and get the source
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data and isinstance(data, list) and len(data) > 0:
                meta = data[0].get("metadata", {})
                src = meta.get("filename", str(p))
                file_chunks[src] += len(data)
    except Exception as e:
        pass

print(f"Total files with chunks: {len(file_chunks)}")
print("Files with 0 or missing chunks:")
print(len(list(chunks_dir.glob("*.json"))), "total json files")
