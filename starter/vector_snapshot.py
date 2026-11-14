"""Export the authorized Day 6 C vectors or restore them into a fresh database.

Export is read-only. Restore refuses an existing day6_chunks table and never deletes data.
Credentials come from environment/local .env and are not serialized.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(snapshot, chunks):
    expected = {c["id"] for c in chunks}
    rows = snapshot["vectors"]
    if snapshot["dimensions"] != 384 or snapshot["strategy"] != "C":
        raise ValueError("Wrong vector snapshot configuration")
    if len(rows) != len(expected) or {r["id"] for r in rows} != expected:
        raise ValueError("Vector/chunk IDs disagree")
    for row in rows:
        v = row["embedding"]
        if len(v) != 384 or any(type(x) not in (int, float) or not math.isfinite(x) for x in v) or not any(v):
            raise ValueError("Invalid embedding")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("export", "restore"))
    parser.add_argument("--chunks", type=Path, default=ROOT / "starter/data/day6/chunks.json")
    parser.add_argument("--file", type=Path, default=ROOT / "artifacts/day6/vectors.json")
    args = parser.parse_args()
    import psycopg
    from psycopg.types.json import Jsonb
    from dotenv import dotenv_values
    chunks = json.loads(args.chunks.read_text(encoding="utf-8"))
    checksum = hashlib.sha256(args.chunks.read_bytes()).hexdigest()
    provenance = json.loads((args.chunks.parent / "provenance.json").read_text(encoding="utf-8"))
    url = os.getenv("DATABASE_URL")
    if not url and args.action == "export":
        url = dotenv_values(Path(provenance["day6_repository"]) / "starter/.env").get("DATABASE_URL")
    if not url:
        raise ValueError("Set DATABASE_URL to the intended database; restore requires an explicit fresh target")
    if args.action == "export":
        with psycopg.connect(url, options="-c default_transaction_read_only=on") as conn:
            conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            rows = conn.execute("SELECT chunk_id,embedding::text,document_id,source,page,text,metadata FROM day6_chunks WHERE strategy=%s ORDER BY chunk_id", ("C",)).fetchall()
            by_id = {c["id"]: c for c in chunks}
            vectors = []
            for cid, vector, source_id, source, page, text, metadata in rows:
                if by_id.get(cid) != {"id": cid, "source_id": source_id, "source": source, "page": page, "text": text, "metadata": metadata}:
                    raise ValueError("Database differs from frozen corpus")
                vectors.append({"id": cid, "embedding": json.loads(vector)})
        snapshot = {"origin": "Original Day 6 pgvector, strategy C; read-only export", "strategy": "C", "dimensions": 384,
                    "chunks_sha256": checksum, "embedding": provenance["embedding"], "vectors": vectors}
        validate(snapshot, chunks)
        args.file.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")) + "\n"
        if args.file.exists() and args.file.read_text(encoding="utf-8") != serialized:
            raise ValueError("Refusing to replace a different snapshot")
        args.file.write_text(serialized, encoding="utf-8")
    else:
        snapshot = json.loads(args.file.read_text(encoding="utf-8"))
        validate(snapshot, chunks)
        if snapshot["chunks_sha256"] != checksum or snapshot["embedding"] != provenance["embedding"]:
            raise ValueError("Frozen corpus/model checksum mismatch")
        vectors = {r["id"]: r["embedding"] for r in snapshot["vectors"]}
        with psycopg.connect(url) as conn:
            if conn.execute("SELECT to_regclass('public.day6_chunks')").fetchone()[0]:
                raise ValueError("Restore requires a fresh database without day6_chunks; nothing was replaced")
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.execute("""CREATE TABLE day6_chunks (strategy text NOT NULL, chunk_id text NOT NULL,
                document_id text NOT NULL, source text NOT NULL, page integer NOT NULL,
                text text NOT NULL, metadata jsonb NOT NULL, embedding vector(384) NOT NULL,
                PRIMARY KEY(strategy,chunk_id))""")
            with conn.cursor() as cursor:
                cursor.executemany("""INSERT INTO day6_chunks
                    (strategy,chunk_id,document_id,source,page,text,metadata,embedding)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s::vector)""",
                    [("C", c["id"], c["source_id"], c["source"], c["page"], c["text"], Jsonb(c["metadata"]),
                      json.dumps(vectors[c["id"]])) for c in chunks])
    print(f"{args.action}: {len(chunks)} chunks/vectors; corpus SHA256 {checksum}")


if __name__ == "__main__":
    main()
