import os
from orchgentic.core.exceptions import KnowledgeError

class ZillizKnowledgeStore:
    def __init__(self, collection: str = "orchgentic_knowledge"):
        try:
            from pymilvus import MilvusClient
        except ImportError as exc:
            raise KnowledgeError("Zilliz support requires: pip install -e '.[zilliz]'") from exc

        uri = os.getenv("ZILLIZ_URI")
        token = os.getenv("ZILLIZ_TOKEN")

        if not uri or not token:
            raise KnowledgeError("ZILLIZ_URI and ZILLIZ_TOKEN must be set.")

        self.collection = os.getenv("ZILLIZ_COLLECTION", collection)
        self.client = MilvusClient(uri=uri, token=token)

        if not self.client.has_collection(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                dimension=64,
                metric_type="COSINE"
            )

    def add(self, source: str, chunk: str, embedding: list[float], metadata: dict | None = None):
        self.client.insert(
            collection_name=self.collection,
            data=[{
                "vector": embedding,
                "source": source,
                "chunk": chunk,
                "metadata": metadata or {}
            }]
        )

    def search(self, query_embedding: list[float], limit: int = 5):
        results = self.client.search(
            collection_name=self.collection,
            data=[query_embedding],
            limit=limit,
            output_fields=["source", "chunk", "metadata"]
        )

        output = []
        for hit in results[0]:
            entity = hit.get("entity", {})
            output.append((
                hit.get("distance", 0.0),
                (None, entity.get("source"), entity.get("chunk"), None, entity.get("metadata"), None)
            ))

        return output

    def list_sources(self):
        # Minimal adapter method for interface compatibility.
        # Collection aggregation will be expanded in a later sprint.
        return []

    def clear(self):
        if self.client.has_collection(self.collection):
            self.client.drop_collection(self.collection)
