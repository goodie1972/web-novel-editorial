#!/usr/bin/env python3
"""
Memory Migration Script - Migrate JSON files to SQLite
将旧的 JSON 文件记忆库迁移到新的 SQLite 数据库
"""

import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime


def migrate_project(project_id: str, base_dir: Path = None):
    """Migrate a single project from JSON to SQLite"""
    if base_dir is None:
        base_dir = Path(__file__).parent.parent / "data"

    project_path = base_dir / "projects" / project_id
    memory_path = project_path / "memory"

    if not project_path.exists():
        print(f"❌ 项目不存在: {project_id}")
        return False

    # Check if SQLite database already exists
    db_path = memory_path / "memory.db"
    if db_path.exists():
        print(f"⚠️  数据库已存在: {db_path}")
        choice = input("是否覆盖? (y/N): ").strip().lower()
        if choice != 'y':
            print("已取消")
            return False

    # Connect to new SQLite database
    conn = sqlite3.connect(db_path)
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_collection ON memories(collection)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)")

    # JSON collections to migrate
    json_collections = ["world", "characters", "skills", "chapters", "foreshadowing", "plot", "reviews", "discussions", "confirmed"]

    migrated_count = 0
    for collection in json_collections:
        json_file = memory_path / f"{collection}.json"
        if not json_file.exists():
            continue

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            documents = data.get("documents", [])
            if not documents:
                continue

            # Migrate each document
            for doc in documents:
                doc_id = doc.get("id", str(hash(doc.get("title", "") + doc.get("content", ""))))
                if not doc_id.startswith("-"):
                    doc_id = str(hash(doc_id))

                collection_name = collection
                title = doc.get("title", "未命名")
                content = doc.get("content", "")
                metadata = json.dumps(doc.get("metadata", {}), ensure_ascii=False)
                created_at = doc.get("metadata", {}).get("timestamp", datetime.utcnow().isoformat() + "Z")

                conn.execute(
                    "INSERT OR REPLACE INTO memories (id, collection, title, content, metadata, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (doc_id, collection_name, title, content, metadata, created_at)
                )
                migrated_count += 1

            print(f"✅ 迁移 {collection}: {len(documents)} 条记录")

        except Exception as e:
            print(f"❌ 迁移 {collection} 失败: {e}")

    conn.commit()
    conn.close()

    print(f"\n🎉 迁移完成！共迁移 {migrated_count} 条记录")
    print(f"数据库位置: {db_path}")

    # Show backup recommendation
    print("\n📝 建议：旧的 JSON 文件已保留作为备份")
    print(f"   备份位置: {memory_path}/*.json")

    return True


def bulk_migrate(base_dir: Path = None):
    """Migrate all projects in the base directory"""
    if base_dir is None:
        base_dir = Path(__file__).parent.parent / "data"

    projects_dir = base_dir / "projects"

    if not projects_dir.exists():
        print(f"❌ 项目目录不存在: {projects_dir}")
        return

    projects = [d for d in projects_dir.iterdir() if d.is_dir() and (d / "project.json").exists()]

    if not projects:
        print("❌ 没有找到项目")
        return

    print(f"找到 {len(projects)} 个项目\n")

    for project_dir in projects:
        project_id = project_dir.name
        print(f"\n{'='*50}")
        print(f"正在迁移: {project_id}")
        print(f"{'='*50}")
        migrate_project(project_id, base_dir)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python migrate_memory.py <project_id>  # 迁移单个项目")
        print("  python migrate_memory.py --all          # 迁移所有项目")
        print("  python migrate_memory.py --help         # 显示此帮助")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "--all":
        base_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        bulk_migrate(base_dir)
    elif command == "--help":
        print("用法:")
        print("  python migrate_memory.py <project_id>  # 迁移单个项目")
        print("  python migrate_memory.py --all          # 迁移所有项目")
        print("  python migrate_memory.py --help         # 显示此帮助")
    else:
        project_id = sys.argv[1]
        base_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        migrate_project(project_id, base_dir)
