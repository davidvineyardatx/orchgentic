from orchgentic.knowledge.chunker import chunk_text
from orchgentic.knowledge.loaders import load_text
from orchgentic.knowledge.local_store import LocalKnowledgeStore
from orchgentic.knowledge.zilliz_store import ZillizKnowledgeStore

class KnowledgeManager:
    def __init__(
        self,
        provider,
        store: str = "local",
        db_path: str = "memory/orchgentic.db",
        collection: str = "orchgentic_knowledge"
    ):
        self.provider = provider
        self.store_type = store
        self.store = ZillizKnowledgeStore(collection) if store == "zilliz" else LocalKnowledgeStore(db_path)

    async def ingest_file(self, path: str, metadata: dict | None = None) -> int:
        text = load_text(path)
        chunks = chunk_text(text)

        for chunk in chunks:
            embedding = await self.provider.embed(chunk)
            self.store.add(path, chunk, embedding, metadata or {})

        return len(chunks)

    async def search(self, query: str, limit: int = 5):
        embedding = await self.provider.embed(query)
        return self.store.search(embedding, limit)

    async def context_for_query(self, query: str, limit: int = 5) -> str:
        results = await self.search(query, limit)

        if not results:
            return ""

        parts = []
        for score, row in results:
            _id, source, chunk, _embedding, _metadata, _timestamp = row
            parts.append(f"Source: {source}\nScore: {score:.3f}\n{chunk}")

        return "\n\n---\n\n".join(parts)

    def list_sources(self):
        return self.store.list_sources()

    def clear(self):
        self.store.clear()
