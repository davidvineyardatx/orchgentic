from pathlib import Path
import sqlite3
import json
import math
from datetime import datetime

class LocalKnowledgeStore:
    def __init__(self, db_path: str = "memory/orchgentic.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    chunk TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    metadata TEXT,
                    timestamp TEXT NOT NULL
                )
            ''')
            conn.commit()

    def add(self, source: str, chunk: str, embedding: list[float], metadata: dict | None = None):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO knowledge_chunks(source, chunk, embedding, metadata, timestamp) VALUES (?, ?, ?, ?, ?)",
                (source, chunk, json.dumps(embedding), json.dumps(metadata or {}), datetime.utcnow().isoformat())
            )
            conn.commit()

    def list_sources(self):
        with self._connect() as conn:
            return conn.execute(
                "SELECT source, COUNT(*) FROM knowledge_chunks GROUP BY source ORDER BY source"
            ).fetchall()

    def clear(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM knowledge_chunks")
            conn.commit()

    def search(self, query_embedding: list[float], limit: int = 5):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, source, chunk, embedding, metadata, timestamp FROM knowledge_chunks"
            ).fetchall()

        scored = []
        for row in rows:
            embedding = json.loads(row[3])
            scored.append((self._cosine(query_embedding, embedding), row))

        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[:limit]

    def _cosine(self, a: list[float], b: list[float]) -> float:
        if not a or not b:
            return 0.0

        n = min(len(a), len(b))
        dot = sum(a[i] * b[i] for i in range(n))
        na = math.sqrt(sum(a[i] * a[i] for i in range(n))) or 1.0
        nb = math.sqrt(sum(b[i] * b[i] for i in range(n))) or 1.0
        return dot / (na * nb)
