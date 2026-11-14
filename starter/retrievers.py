"""Real TF-IDF, Day 6 pgvector dense retrieval, and rank-based hybrid retrieval.

Dense dependencies are lazy imports: the TF-IDF path needs only stdlib.
Run dense/hybrid with the already configured Day 6 Python environment.
"""
import json
import math
import os
from pathlib import Path

from baseline import TfidfIndex


def check_filters(filters):
    if filters is not None and (not isinstance(filters, dict) or any(
            not isinstance(key, str) or not key or type(value) not in (str, int, bool)
            for key, value in filters.items())):
        raise ValueError("Filters must be an object with string keys and scalar str/int/bool values")


class TfidfRetriever:
    strategy = "tfidf"

    def __init__(self, chunks):
        self.index = TfidfIndex(chunks)
        self.chunk_count = len(chunks)
        self.last_trace = None
        self.configuration = {"method": "TF-IDF cosine", "idf_corpus_chunks": len(chunks),
                              "filter_policy": "Supplied metadata filters applied before top-k"}

    def search(self, query, *, filters=None, top_k=3):
        check_filters(filters)
        ranked = self.index.search(query, top_k=self.chunk_count)
        results = [chunk for chunk in ranked if not filters or all(
            type(chunk["metadata"].get(key)) is type(value) and chunk["metadata"].get(key) == value
            for key, value in filters.items())][:top_k]
        self.last_trace = {"query": query, "filters": filters, "returned": len(results)}
        return results


def rrf_fuse(ranked_lists, *, top_k, rank_constant=60):
    """Sum 1/(constant + one-based rank); raw retriever scores are not added."""
    if rank_constant < 1 or top_k < 1:
        raise ValueError("RRF rank_constant/top_k must be positive")
    merged = {}
    for method, results in ranked_lists.items():
        seen = set()
        for rank, chunk in enumerate(results, 1):
            cid = chunk["id"]
            if cid in seen:
                raise ValueError("Each retriever must return unique chunk IDs")
            seen.add(cid)
            if cid not in merged:
                merged[cid] = {**chunk, "score": 0.0, "strategy": "hybrid",
                               "component_ranks": {}, "component_scores": {}}
            elif any(merged[cid][key] != chunk[key] for key in ("source_id", "source", "page", "text", "metadata")):
                raise ValueError("Same chunk ID has conflicting source data across retrievers")
            merged[cid]["score"] += 1.0 / (rank_constant + rank)
            merged[cid]["component_ranks"][method] = rank
            merged[cid]["component_scores"][method] = chunk["score"]
    return sorted(merged.values(), key=lambda chunk: (-chunk["score"], chunk["id"]))[:top_k]


class Day6DenseRetriever:
    strategy = "dense"

    def __init__(self, chunks, *, provenance_path, day6=None):
        try:
            import psycopg
            from psycopg.rows import dict_row
            from psycopg.types.json import Jsonb
            from dotenv import dotenv_values
        except ImportError as error:
            raise RuntimeError("Use the Day 6 .venv Python: psycopg and python-dotenv are required") from error
        self.Jsonb = Jsonb
        provenance = json.loads(Path(provenance_path).read_text(encoding="utf-8"))
        repository = Path(day6 or os.getenv("DAY6_REPOSITORY") or provenance["day6_repository"]).resolve()
        if not (repository / "artifacts/strategies.json").is_file():
            repository = repository / "K5-L3-Day06-DataIngestionEngineering-main"
        model_info = provenance["embedding"]
        self.index_strategy = provenance["strategy"]
        self.dimensions = model_info["dimensions"]
        self.chunks = {chunk["id"]: chunk for chunk in chunks}
        self.last_trace = None
        self.connection = None
        url = os.getenv("DATABASE_URL") or dotenv_values(repository / "starter/.env").get("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL missing in the Day 6 starter/.env")
        try:
            self.connection = psycopg.connect(url, connect_timeout=10, row_factory=dict_row,
                autocommit=True, options="-c default_transaction_read_only=on")
        except psycopg.Error:
            raise RuntimeError("Cannot connect to Day 6 PostgreSQL. Check Docker and Day 6 starter/.env.") from None
        try:
            self.connection.execute("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            rows = self.connection.execute("""SELECT chunk_id AS id, document_id AS source_id,
                source,page,text,metadata,vector_dims(embedding) AS dimensions
                FROM day6_chunks WHERE strategy=%s ORDER BY chunk_id""", (self.index_strategy,)).fetchall()
            if len(rows) != len(chunks) or {row["id"] for row in rows} != set(self.chunks):
                raise ValueError("Database snapshot IDs/count differ from the frozen Day 7 corpus")
            for row in rows:
                if row["dimensions"] != self.dimensions or any(row[key] != self.chunks[row["id"]][key]
                        for key in ("source_id", "source", "page", "text", "metadata")):
                    raise ValueError("Database chunk content/metadata/dimensions differ from the frozen corpus")

            model_folder = "models--" + model_info["model"].replace("/", "--")
            locations = [repository.parent / ".cache/embedding/models", repository / "starter/.cache/embedding/models"]
            snapshot = next((base / model_folder / "snapshots" / model_info["revision"] for base in locations
                             if (base / model_folder / "snapshots" / model_info["revision"]).is_dir()), None)
            if os.getenv("EMBEDDING_SNAPSHOT"):
                snapshot = Path(os.environ["EMBEDDING_SNAPSHOT"]).resolve()
                if not snapshot.is_dir():
                    raise RuntimeError("EMBEDDING_SNAPSHOT directory missing")
            if snapshot is None:
                raise RuntimeError("Pinned Day 6 model snapshot missing. Restore the original Day 6 model cache.")
            # Use only existing local weights. Any Hugging Face cache writes go
            # into Day 7, rather than the original Day 6 model/cache directories.
            workspace_cache = Path(__file__).resolve().parent / "data/hf_cache"
            workspace_cache.mkdir(parents=True, exist_ok=True)
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["HF_HOME"] = str(workspace_cache)
            try:
                import torch
                from sentence_transformers import SentenceTransformer
            except ImportError as error:
                raise RuntimeError("Use the Day 6 .venv Python: torch and sentence-transformers are required") from error
            torch.set_num_threads(4)
            torch.manual_seed(42)
            self.model = SentenceTransformer(str(snapshot), device="cpu", local_files_only=True,
                                            trust_remote_code=False, cache_folder=str(workspace_cache))
            if self.model.get_sentence_embedding_dimension() != self.dimensions:
                raise ValueError("Query model dimension differs from the Day 6 vector index")
            self.max_tokens = self.model.max_seq_length
            # Verify deterministic, label-independent samples of stored document
            # vectors against actual pinned-model embeddings, not just dimensions.
            sample_ids = sorted(self.chunks)
            sample_ids = [sample_ids[i] for i in sorted({0, len(sample_ids)//2, len(sample_ids)-1})]
            sample_vectors = self._embed([self.chunks[cid]["text"] for cid in sample_ids])
            differences = []
            for cid, vector in zip(sample_ids, sample_vectors):
                stored = self.connection.execute("SELECT embedding::text AS vector FROM day6_chunks WHERE strategy=%s AND chunk_id=%s",
                                                 (self.index_strategy, cid)).fetchone()
                stored_vector = json.loads(stored["vector"])
                difference = max(abs(a-b) for a, b in zip(stored_vector, vector))
                if len(stored_vector) != len(vector) or difference > 0.0001:
                    raise ValueError("Stored document vectors are incompatible with the pinned query model")
                differences.append(difference)
            self.configuration = {"method": "Exact pgvector cosine", "day6_strategy": self.index_strategy,
                "corpus_chunks_verified": len(rows), "embedding": model_info, "device": "cpu",
                "local_weights_only": True, "document_vector_check_samples": len(sample_ids),
                "document_vector_max_abs_difference": max(differences),
                "document_vector_check_tolerance": 0.0001, "database_read_only": True,
                "database_snapshot": "repeatable read", "query_embedding_cache": False,
                "filter_policy": "Supplied metadata filters applied in SQL before top-k"}
        except BaseException:
            self.close()
            raise

    def _embed(self, texts):
        lengths = [len(ids) for ids in self.model.tokenizer(texts, truncation=False, add_special_tokens=True)["input_ids"]]
        if any(length > self.max_tokens for length in lengths):
            raise ValueError(f"Input exceeds pinned model's {self.max_tokens} token limit; truncation refused")
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True).tolist()

    def search(self, query, *, filters=None, top_k=3):
        check_filters(filters)
        if not query.strip() or not 1 <= top_k <= 100:
            raise ValueError("A nonempty query and top_k in 1..100 are required")
        vector = self._embed([query])[0]
        if len(vector) != self.dimensions or not all(math.isfinite(value) for value in vector) or not any(vector):
            raise ValueError("Invalid real query embedding")
        literal = "[" + ",".join(str(value) for value in vector) + "]"
        sql = """SELECT chunk_id AS id, document_id AS source_id, source,page,text,metadata,
            1-(embedding <=> %s::vector) AS score FROM day6_chunks WHERE strategy=%s"""
        args = [literal, self.index_strategy]
        if filters:
            sql += " AND metadata @> %s"
            args.append(self.Jsonb(filters))
        sql += " ORDER BY embedding <=> %s::vector,chunk_id LIMIT %s"
        args.extend([literal, top_k])
        results = [dict(row) for row in self.connection.execute(sql, args).fetchall()]
        for row in results:
            row["strategy"] = "dense"
        self.last_trace = {"query": query, "filters": filters, "requested_top_k": top_k,
                           "returned": len(results), "embedding_dimensions": len(vector)}
        return results

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None


class HybridRetriever:
    strategy = "hybrid"

    def __init__(self, dense, lexical, *, candidate_k=20, rank_constant=60):
        if not 1 <= candidate_k <= 100 or rank_constant < 1:
            raise ValueError("candidate_k must be in 1..100 and rank_constant must be positive")
        self.dense = dense
        self.lexical = lexical
        self.candidate_k = candidate_k
        self.rank_constant = rank_constant
        self.last_trace = None
        self.configuration = {"method": "Dense + TF-IDF reciprocal rank fusion", "candidate_k_per_method": candidate_k,
                              "rank_constant": rank_constant, "dense": dense.configuration, "lexical": lexical.configuration}

    def search(self, query, *, filters=None, top_k=3):
        if top_k > self.candidate_k:
            raise ValueError("Hybrid candidate_k must be >= output top_k")
        dense = self.dense.search(query, filters=filters, top_k=self.candidate_k)
        lexical = self.lexical.search(query, filters=filters, top_k=self.candidate_k)
        self.last_trace = {"query": query, "filters": filters,
                           "candidate_k_per_method": self.candidate_k, "rank_constant": self.rank_constant,
                           "dense_candidates": [{**row, "rank": rank} for rank, row in enumerate(dense, 1)],
                           "tfidf_candidates": [{**row, "rank": rank} for rank, row in enumerate(lexical, 1)]}
        return rrf_fuse({"dense": dense, "tfidf": lexical}, top_k=top_k, rank_constant=self.rank_constant)

    def close(self):
        self.dense.close()
