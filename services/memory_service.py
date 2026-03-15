"""Memory management service for web novel editorial system"""
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional


class MemoryManager:
    """Simple JSON-based memory system for 7 collections"""

    COLLECTIONS = ["world", "characters", "skills", "chapters", "foreshadowing", "plot", "reviews"]

    def __init__(self, project_path: Path):
        self.memory_path = Path(project_path) / "memory"
        self.memory_path.mkdir(parents=True, exist_ok=True)

    def add_document(self, collection: str, title: str, content: str, metadata: Optional[Dict] = None) -> str:
        """Add document to collection"""
        if collection not in self.COLLECTIONS:
            raise ValueError(f"Invalid collection: {collection}")

        doc_id = str(uuid.uuid4())
        doc = {
            "id": doc_id,
            "title": title,
            "content": content,
            "metadata": metadata or {}
        }

        collection_file = self.memory_path / f"{collection}.json"
        data = self._load_collection(collection)
        data["documents"].append(doc)
        self._save_collection(collection, data)

        return doc_id

    def query_documents(self, collection: str, query_text: Optional[str] = None, filters: Optional[Dict] = None) -> List[Dict]:
        """Query documents with simple text search"""
        if collection not in self.COLLECTIONS:
            raise ValueError(f"Invalid collection: {collection}")

        data = self._load_collection(collection)
        documents = data["documents"]

        if query_text:
            query_lower = query_text.lower()
            documents = [
                doc for doc in documents
                if query_lower in doc["title"].lower() or query_lower in doc["content"].lower()
            ]

        if filters:
            for key, value in filters.items():
                documents = [doc for doc in documents if doc.get("metadata", {}).get(key) == value]

        return documents

    def get_all(self, collection: str) -> List[Dict]:
        """Get all documents in collection"""
        if collection not in self.COLLECTIONS:
            raise ValueError(f"Invalid collection: {collection}")

        data = self._load_collection(collection)
        return data["documents"]

    def update_document(self, collection: str, doc_id: str, updates: Dict) -> None:
        """Update existing document"""
        if collection not in self.COLLECTIONS:
            raise ValueError(f"Invalid collection: {collection}")

        data = self._load_collection(collection)
        for doc in data["documents"]:
            if doc["id"] == doc_id:
                doc.update(updates)
                break

        self._save_collection(collection, data)

    def _load_collection(self, collection: str) -> Dict:
        """Load collection file"""
        collection_file = self.memory_path / f"{collection}.json"
        if not collection_file.exists():
            return {"documents": []}

        with open(collection_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_collection(self, collection: str, data: Dict) -> None:
        """Save collection file"""
        collection_file = self.memory_path / f"{collection}.json"
        with open(collection_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
