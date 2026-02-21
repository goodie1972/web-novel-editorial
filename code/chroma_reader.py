# -*- coding: utf-8 -*-
"""
Chroma 向量数据库读取器
用于网文编辑部长记忆系统
"""

from chroma_client import ChromaClient


class ChromaReader:
    """Chroma 数据读取器"""

    def __init__(self, persist_directory="./chroma_data"):
        self.client = ChromaClient(persist_directory)

    # ========== 世界观查询 ==========

    def search_world(self, query, n=3, category=None):
        """查询世界观设定"""
        where = {"category": category} if category else None
        return self.client.query(
            collection_name="world", query_texts=[query], n_results=n, where=where
        )

    def get_world_by_category(self, category):
        """按类别获取世界观设定"""
        return self.client.get(collection_name="world", where={"category": category})

    # ========== 人物查询 ==========

    def search_characters(self, query, n=5, role=None):
        """查询人物设定"""
        where = {"role": role} if role else None
        return self.client.query(
            collection_name="characters", query_texts=[query], n_results=n, where=where
        )

    def get_character_by_name(self, name):
        """按名称获取人物"""
        return self.client.get(collection_name="characters", where={"name": name})

    def get_character_by_chapter(self, chapter):
        """获取某章节出场的人物"""
        # Chroma 不支持范围查询，这里需要获取所有后过滤
        results = self.client.get(collection_name="characters")

        matched = []
        if results and results["metadatas"]:
            for i, meta in enumerate(results["metadatas"]):
                if meta.get("chapter") == chapter:
                    matched.append(
                        {
                            "id": results["ids"][i],
                            "document": results["documents"][i],
                            "metadata": meta,
                        }
                    )

        return matched

    def get_all_characters(self):
        """获取所有人物"""
        return self.client.get(collection_name="characters")

    # ========== 技能查询 ==========

    def search_skills(self, query, n=5, owner=None):
        """查询技能设定"""
        where = {"owner": owner} if owner else None
        return self.client.query(
            collection_name="skills", query_texts=[query], n_results=n, where=where
        )

    def get_skill_by_name(self, name):
        """按名称获取技能"""
        return self.client.get(collection_name="skills", where={"name": name})

    # ========== 章节查询 ==========

    def search_chapters(self, query, n=3):
        """搜索历史章节"""
        return self.client.query(
            collection_name="chapters", query_texts=[query], n_results=n
        )

    def get_chapter(self, chapter_num):
        """获取指定章节"""
        return self.client.get(
            collection_name="chapters", where={"chapter": chapter_num}
        )

    def get_recent_chapters(self, n=5):
        """获取最近的n章"""
        results = self.client.get(collection_name="chapters")

        if not results or not results["metadatas"]:
            return []

        # 按章节号排序
        chapters = []
        for i, meta in enumerate(results["metadatas"]):
            chapters.append(
                {
                    "id": results["ids"][i],
                    "document": results["documents"][i],
                    "metadata": meta,
                }
            )

        chapters.sort(key=lambda x: x["metadata"].get("chapter", 0), reverse=True)
        return chapters[:n]

    # ========== 伏笔查询 ==========

    def get_foreshadowing_by_chapter(self, chapter):
        """获取某章节相关的伏笔（埋入或回收）"""
        results = self.client.get(collection_name="foreshadowing")

        if not results or not results["metadatas"]:
            return []

        matched = []
        for i, meta in enumerate(results["metadatas"]):
            if (
                meta.get("embed_chapter") == chapter
                or meta.get("recover_chapter") == chapter
            ):
                matched.append(
                    {
                        "id": results["ids"][i],
                        "document": results["documents"][i],
                        "metadata": meta,
                    }
                )

        return matched

    def get_active_foreshadowing(self):
        """获取所有未回收的伏笔"""
        return self.client.get(
            collection_name="foreshadowing", where={"status": "active"}
        )

    def get_all_foreshadowing(self):
        """获取所有伏笔"""
        return self.client.get(collection_name="foreshadowing")

    # ========== 剧情查询 ==========

    def search_plot(self, query, n=5, plot_type=None):
        """查询剧情线"""
        where = {"plot_type": plot_type} if plot_type else None
        return self.client.query(
            collection_name="plot", query_texts=[query], n_results=n, where=where
        )

    def get_plot_by_chapter(self, chapter):
        """获取某章节的剧情点"""
        return self.client.get(collection_name="plot", where={"chapter": chapter})

    # ========== 审核查询 ==========

    def get_review_by_chapter(self, chapter_num):
        """获取某章节的审核记录"""
        return self.client.get(
            collection_name="reviews", where={"chapter": chapter_num}
        )


class ContextBuilder:
    """上下文构建器 - 用于写作/审核时快速构建上下文"""

    def __init__(self, persist_directory="./chroma_data"):
        self.reader = ChromaReader(persist_directory)

    def build_write_context(self, chapter_num):
        """构建写作上下文"""
        context = {
            "chapter": chapter_num,
            "recent_chapters": [],
            "characters_appearing": [],
            "foreshadowing": [],
            "world_settings": [],
        }

        # 1. 获取最近章节
        recent = self.reader.get_recent_chapters(n=3)
        context["recent_chapters"] = recent

        # 2. 获取本章出场人物
        chars = self.reader.get_character_by_chapter(chapter_num)
        context["characters_appearing"] = chars

        # 3. 获取本章相关伏笔
        fs = self.reader.get_foreshadowing_by_chapter(chapter_num)
        context["foreshadowing"] = fs

        # 4. 获取活跃伏笔（需要记住的）
        active_fs = self.reader.get_active_foreshadowing()
        context["active_foreshadowing"] = active_fs

        return context

    def build_review_context(self, chapter_num):
        """构建审核上下文"""
        context = {
            "chapter": chapter_num,
            "all_characters": [],
            "foreshadowing": [],
            "world_settings": [],
            "previous_chapters": [],
        }

        # 1. 获取所有人物设定
        chars = self.reader.get_all_characters()
        context["all_characters"] = chars

        # 2. 获取伏笔
        fs = self.reader.get_foreshadowing_by_chapter(chapter_num)
        context["foreshadowing"] = fs

        # 3. 获取最近章节
        recent = self.reader.get_recent_chapters(n=3)
        context["previous_chapters"] = recent

        return context


if __name__ == "__main__":
    # 测试读取
    reader = ChromaReader("./chroma_data")

    # 测试查询
    result = reader.search_characters("林诗雨")
    print("查询结果:", result)
