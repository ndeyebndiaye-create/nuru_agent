import json
from pathlib import Path

chunks_dir = Path("data/processed/chunks")

latest_chunks = {}
for p in chunks_dir.glob("*.json"):
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            src = data.get("source")
            timestamp = data.get("timestamp")
            chunks = data.get("chunks", [])
            
            if src not in latest_chunks or timestamp > latest_chunks[src]["timestamp"]:
                latest_chunks[src] = {
                    "timestamp": timestamp,
                    "count": len(chunks),
                    "file": str(p)
                }
    except Exception as e:
        pass

total_chunks = sum(x["count"] for x in latest_chunks.values())
print(f"Total unique files processed: {len(latest_chunks)}")
print(f"Total chunks across latest files: {total_chunks}")

zero_chunk_files = [src for src, info in latest_chunks.items() if info["count"] == 0]
print(f"Files with 0 chunks: {len(zero_chunk_files)}")
for f in zero_chunk_files[:5]:
    print(f"- {f}")
