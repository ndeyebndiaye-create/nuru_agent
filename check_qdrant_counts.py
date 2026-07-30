import sys
from pathlib import Path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from qdrant_client import QdrantClient
client = QdrantClient(url="http://localhost:6333")
collection_name = "nuru_maths"
try:
    count = client.count(collection_name)
    print(f"Total points: {count.count}")
    
    # We can fetch some points to see the files
    offset = None
    filenames = set()
    while True:
        res = client.scroll(collection_name=collection_name, limit=1000, with_payload=True, with_vectors=False, offset=offset)
        points, offset = res
        for point in points:
            meta = point.payload.get("metadata", {})
            filename = meta.get("filename")
            if filename:
                filenames.add(filename)
        if offset is None:
            break
    print(f"Unique files indexed: {len(filenames)}")
    print(f"Files: {sorted(list(filenames))[:5]} ...")
except Exception as e:
    print(f"Error: {e}")
