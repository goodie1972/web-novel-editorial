# -*- coding: utf-8 -*-
"""
Chroma 向量数据库写入器
用于网文编辑部长记忆系统
"""

from chroma_client import ChromaClient


class ChromaWriter:
    """Chroma 数据写入器"""

    def __init__(self, persist_directory="./chroma_data"):
        self.client = ChromaClient(persist_directory)

    # ========== 世界观设定 ==========

    def add_world_setting(self, content, name, category):
        """写入世界观设定"""
        self.client.add(
            collection_name="world",
            documents=[content],
            metadatas=[{"type": "world", "name": name, "category": category}],
            ids=[f"world_{name}"],
        )

    # ========== 人物设定 ==========

    def add_character(self, name, content, chapter, role, status="active"):
        """写入人物设定"""
        self.client.add(
            collection_name="characters",
            documents=[content],
            metadatas=[
                {
                    "type": "character",
                    "name": name,
                    "chapter": chapter,
                    "role": role,
                    "status": status,
                }
            ],
            ids=[f"char_{name}_{chapter}"],
        )

    # ========== 技能设定 ==========

    def add_skill(self, name, content, category, owner=None):
        """写入技能设定"""
        self.client.add(
            collection_name="skills",
            documents=[content],
            metadatas=[
                {"type": "skill", "name": name, "category": category, "owner": owner}
            ],
            ids=[f"skill_{name}"],
        )

    # ========== 章节摘要 ==========

    def add_chapter_summary(self, chapter_num, content, metadata):
        """写入章节摘要"""
        self.client.add(
            collection_name="chapters",
            documents=[content],
            metadatas=[{"chapter": chapter_num, **metadata}],
            ids=[f"chapter_{chapter_num:03d}"],
        )

    # ========== 伏笔 ==========

    def add_foreshadowing(
        self, name, content, embed_chapter, recover_chapter, status="active"
    ):
        """写入伏笔"""
        self.client.add(
            collection_name="foreshadowing",
            documents=[content],
            metadatas=[
                {
                    "type": "foreshadowing",
                    "name": name,
                    "embed_chapter": embed_chapter,
                    "recover_chapter": recover_chapter,
                    "status": status,
                }
            ],
            ids=[f"fs_{name}_{embed_chapter}"],
        )

    # ========== 剧情线 ==========

    def add_plot_point(self, name, content, chapter, plot_type="main"):
        """写入剧情点"""
        self.client.add(
            collection_name="plot",
            documents=[content],
            metadatas=[
                {
                    "type": "plot",
                    "name": name,
                    "chapter": chapter,
                    "plot_type": plot_type,
                }
            ],
            ids=[f"plot_{name}_{chapter}"],
        )

    # ========== 审核记录 ==========

    def add_review(self, chapter_num, content, result, issues=None):
        """写入审核记录"""
        self.client.add(
            collection_name="reviews",
            documents=[content],
            metadatas=[
                {
                    "type": "review",
                    "chapter": chapter_num,
                    "result": result,
                    "issues": issues or [],
                }
            ],
            ids=[f"review_{chapter_num:03d}"],
        )


class ChromaUpdater:
    """Chroma 数据更新器"""

    def __init__(self, persist_directory="./chroma_data"):
        self.client = ChromaClient(persist_directory)

    def recover_foreshadowing(self, name, chapter):
        """标记伏笔已回收"""
        collection = self.client.get_collection("foreshadowing")
        results = collection.get(where={"name": name})

        if results and results["ids"]:
            collection.update(
                ids=[results["ids"][0]],
                metadatas=[{"status": "recovered", "recover_chapter": chapter}],
            )

    def update_character_status(self, name, status):
        """更新人物状态"""
        collection = self.client.get_collection("characters")
        results = collection.get(where={"name": name})

        if results and results["ids"]:
            collection.update(ids=[results["ids"][0]], metadatas=[{"status": status}])

    def update_chapter_metadata(self, chapter_num, metadata):
        """更新章节元数据"""
        collection = self.client.get_collection("chapters")
        results = collection.get(where={"chapter": chapter_num})

        if results and results["ids"]:
            collection.update(ids=[results["ids"][0]], metadatas=[metadata])


if __name__ == "__main__":
    # 测试写入
    writer = ChromaWriter("./chroma_data")

    # 写入测试人物
    writer.add_character(
        name="林诗雨",
        content="林诗雨，女，17岁，主角的妹妹，学生，活泼可爱，表面大大咧咧但实际关心哥哥，隐藏血脉（后续觉醒）",
        chapter=1,
        role="配角",
    )

    print("测试数据写入成功！")
