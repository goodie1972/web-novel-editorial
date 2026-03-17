"""Memory management service for web novel editorial system"""
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class MemoryManager:
    """SQLite-based memory system for web novel editorial"""

    COLLECTIONS = ["world", "characters", "skills", "chapters", "foreshadowing", "plot", "reviews", "discussions", "confirmed"]

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.memory_path = self.project_path / "memory"
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.memory_path / "memory.db"
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with memories table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    collection TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP
                )
            """)
            # Create index for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_collection ON memories(collection)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)
            """)
            conn.commit()

    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def add_document(self, collection: str, title: str, content: str, metadata: Optional[Dict] = None) -> str:
        """Add document to collection"""
        if collection not in self.COLLECTIONS:
            raise ValueError(f"Invalid collection: {collection}")

        doc_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"
        metadata_json = json.dumps(metadata or {}, ensure_ascii=False)

        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO memories (id, collection, title, content, metadata, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (doc_id, collection, title, content, metadata_json, created_at)
            )
            conn.commit()

        return doc_id

    def query_documents(self, collection: str, query_text: Optional[str] = None, filters: Optional[Dict] = None) -> List[Dict]:
        """Query documents with simple text search"""
        if collection not in self.COLLECTIONS:
            raise ValueError(f"Invalid collection: {collection}")

        # Build query
        sql = "SELECT id, collection, title, content, metadata, created_at FROM memories WHERE collection = ?"
        params = [collection]

        # Text search in title or content
        if query_text:
            sql += " AND (LOWER(title) LIKE ? OR LOWER(content) LIKE ?)"
            query_pattern = f"%{query_text.lower()}%"
            params.extend([query_pattern, query_pattern])

        # Filter by metadata
        if filters:
            for key, value in filters.items():
                # Use JSON_EXTRACT for SQLite 3.38+
                sql += f" AND json_extract(metadata, '$.{key}') = ?"
                params.append(str(value))

        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()

        documents = []
        for row in rows:
            doc = dict(row)
            if doc.get("metadata"):
                try:
                    doc["metadata"] = json.loads(doc["metadata"])
                except json.JSONDecodeError:
                    doc["metadata"] = {}
            documents.append(doc)

        return documents

    def get_all(self, collection: str) -> List[Dict]:
        """Get all documents in collection"""
        if collection not in self.COLLECTIONS:
            raise ValueError(f"Invalid collection: {collection}")

        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, collection, title, content, metadata, created_at FROM memories WHERE collection = ?",
                (collection,)
            )
            rows = cursor.fetchall()

        documents = []
        for row in rows:
            doc = dict(row)
            if doc.get("metadata"):
                try:
                    doc["metadata"] = json.loads(doc["metadata"])
                except json.JSONDecodeError:
                    doc["metadata"] = {}
            documents.append(doc)

        return documents

    def update_document(self, collection: str, doc_id: str, updates: Dict) -> None:
        """Update existing document"""
        if collection not in self.COLLECTIONS:
            raise ValueError(f"Invalid collection: {collection}")

        with self._get_connection() as conn:
            # Get current document
            cursor = conn.execute(
                "SELECT id, collection, title, content, metadata, created_at FROM memories WHERE id = ?",
                (doc_id,)
            )
            row = cursor.fetchone()
            if not row:
                return

            doc = dict(row)
            # Apply updates
            doc.update(updates)

            # Update metadata if needed
            metadata = doc.get("metadata", {})
            if isinstance(metadata, dict):
                metadata_json = json.dumps(metadata, ensure_ascii=False)
            else:
                metadata_json = json.dumps({}, ensure_ascii=False)

            conn.execute(
                "UPDATE memories SET title = ?, content = ?, metadata = ? WHERE id = ?",
                (doc["title"], doc["content"], metadata_json, doc_id)
            )
            conn.commit()

    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document"""
        if collection not in self.COLLECTIONS:
            raise ValueError(f"Invalid collection: {collection}")

        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM memories WHERE id = ? AND collection = ?",
                (doc_id, collection)
            )
            conn.commit()
            return cursor.rowcount > 0

    def clear_collection(self, collection: str) -> int:
        """Clear all documents from a collection, returns count of deleted docs"""
        if collection not in self.COLLECTIONS:
            raise ValueError(f"Invalid collection: {collection}")

        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM memories WHERE collection = ?",
                (collection,)
            )
            count = cursor.fetchone()[0]

            conn.execute(
                "DELETE FROM memories WHERE collection = ?",
                (collection,)
            )
            conn.commit()

            return count
