# -*- coding: utf-8 -*-
"""
简化版向量数据库 - 纯 Python 实现
用于网文编辑部长记忆系统
不需要额外依赖，使用 numpy 实现近似搜索
"""

import os
import json
import numpy as np
from pathlib import Path
from datetime import datetime


class SimpleVectorDB:
    """
    简化版向量数据库
    使用 numpy 实现余弦相似度搜索
    """

    def __init__(self, persist_directory="./vector_db"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        # 数据存储
        self.data_file = os.path.join(persist_directory, "data.json")
        self.vectors_file = os.path.join(persist_directory, "vectors.npy")

        # 加载或初始化数据
        self.load_data()

    def load_data(self):
        """加载数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = []

        if os.path.exists(self.vectors_file):
            self.vectors = np.load(self.vectors_file)
        else:
            self.vectors = np.array([])

    def save_data(self):
        """保存数据"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

        if len(self.vectors) > 0:
            np.save(self.vectors_file, self.vectors)

    def _get_embedding(self, text):
        """
        简单的文本向量化
        使用词袋模型 + 字符 n-gram
        """
        # 字符级别的 n-gram
        n = 3
        ngrams = [text[i : i + n] for i in range(len(text) - n + 1)]

        # 统计字符出现频率
        vector = np.zeros(256)  # 使用常见字符范围

        for char in text:
            if ord(char) < 256:
                vector[ord(char)] += 1

        # 添加 n-gram 特征
        ngram_counts = {}
        for ng in ngrams:
            key = hash(ng) % 10000
            ngram_counts[key] = ngram_counts.get(key, 0) + 1

        # 扩展向量
        ngram_vec = np.zeros(10000)
        for k, v in ngram_counts.items():
            ngram_vec[k] = v

        return np.concatenate([vector, ngram_vec])

    def _cosine_similarity(self, v1, v2):
        """计算余弦相似度"""
        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0

        return dot / (norm1 * norm2)

    def add(self, collection, document, metadata=None):
        """添加文档"""
        embedding = self._get_embedding(document)

        entry = {
            "collection": collection,
            "document": document,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }

        self.data.append(entry)

        if len(self.vectors) == 0:
            self.vectors = embedding.reshape(1, -1)
        else:
            self.vectors = np.vstack([self.vectors, embedding])

        self.save_data()

        return len(self.data) - 1

    def search(self, collection, query, n=3, filter_metadata=None):
        """搜索文档"""
        query_embedding = self._get_embedding(query)

        results = []

        for i, entry in enumerate(self.data):
            if entry["collection"] != collection:
                continue

            # 元数据过滤
            if filter_metadata:
                match = True
                for k, v in filter_metadata.items():
                    if entry["metadata"].get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            # 计算相似度
            sim = self._cosine_similarity(query_embedding, self.vectors[i])

            results.append(
                {
                    "id": i,
                    "document": entry["document"],
                    "metadata": entry["metadata"],
                    "score": float(sim),
                }
            )

        # 排序并返回 top n
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:n]

    def get_by_metadata(self, collection, metadata):
        """根据元数据获取文档"""
        results = []

        for i, entry in enumerate(self.data):
            if entry["collection"] != collection:
                continue

            match = True
            for k, v in metadata.items():
                if entry["metadata"].get(k) != v:
                    match = False
                    break

            if match:
                results.append(
                    {
                        "id": i,
                        "document": entry["document"],
                        "metadata": entry["metadata"],
                    }
                )

        return results

    def get_all(self, collection):
        """获取集合中的所有文档"""
        return self.get_by_metadata(collection, {})

    def delete(self, collection, document_id=None, metadata=None):
        """删除文档"""
        if document_id is not None:
            self.data.pop(document_id)
            self.vectors = np.delete(self.vectors, document_id, axis=0)
        elif metadata:
            to_delete = []
            for i, entry in enumerate(self.data):
                if entry["collection"] != collection:
                    continue

                match = True
                for k, v in metadata.items():
                    if entry["metadata"].get(k) != v:
                        match = False
                        break

                if match:
                    to_delete.append(i)

            # 倒序删除
            for i in sorted(to_delete, reverse=True):
                self.data.pop(i)
                self.vectors = np.delete(self.vectors, i, axis=0)

        self.save_data()

    def reset(self):
        """重置数据库"""
        self.data = []
        self.vectors = np.array([])

        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        if os.path.exists(self.vectors_file):
            os.remove(self.vectors_file)


class NovelVectorDB:
    """
    网文专用向量数据库
    封装了 collections 的概念
    """

    def __init__(self, persist_directory="./vector_db"):
        self.db = SimpleVectorDB(persist_directory)

        # Collections
        self.COLLECTIONS = {
            "world": "世界观设定",
            "characters": "人物设定",
            "skills": "技能设定",
            "chapters": "章节摘要",
            "foreshadowing": "伏笔记录",
            "plot": "剧情线",
            "reviews": "审核记录",
        }

    # ========== 世界观 ==========

    def add_world(self, name, content, category):
        """添加世界观设定"""
        return self.db.add(
            "world", content, {"type": "world", "name": name, "category": category}
        )

    def search_world(self, query, n=3, category=None):
        """搜索世界观"""
        return self.db.search(
            "world", query, n, {"category": category} if category else None
        )

    # ========== 人物 ==========

    def add_character(self, name, content, chapter, role):
        """添加人物"""
        return self.db.add(
            "characters",
            content,
            {"type": "character", "name": name, "chapter": chapter, "role": role},
        )

    def search_characters(self, query, n=5, role=None):
        """搜索人物"""
        return self.db.search("characters", query, n, {"role": role} if role else None)

    def get_character_by_chapter(self, chapter):
        """获取某章节出场的人物"""
        return self.db.get_by_metadata("characters", {"chapter": chapter})

    def get_all_characters(self):
        """获取所有人物"""
        return self.db.get_all("characters")

    # ========== 技能 ==========

    def add_skill(self, name, content, category, owner=None):
        """添加技能"""
        return self.db.add(
            "skills",
            content,
            {"type": "skill", "name": name, "category": category, "owner": owner},
        )

    def search_skills(self, query, n=5, owner=None):
        """搜索技能"""
        return self.db.search("skills", query, n, {"owner": owner} if owner else None)

    # ========== 章节 ==========

    def add_chapter_summary(self, chapter_num, content, metadata):
        """添加章节摘要"""
        return self.db.add("chapters", content, {"chapter": chapter_num, **metadata})

    def get_chapter(self, chapter_num):
        """获取章节"""
        results = self.db.get_by_metadata("chapters", {"chapter": chapter_num})
        return results[0] if results else None

    def get_recent_chapters(self, n=5):
        """获取最近章节"""
        all_chapters = self.db.get_all("chapters")

        # 按章节号排序
        chapters = [(r, r["metadata"].get("chapter", 0)) for r in all_chapters]
        chapters.sort(key=lambda x: x[1], reverse=True)

        return [r[0] for r in chapters[:n]]

    def search_chapters(self, query, n=3):
        """搜索章节"""
        return self.db.search("chapters", query, n)

    # ========== 伏笔 ==========

    def add_foreshadowing(self, name, content, embed_chapter, recover_chapter):
        """添加伏笔"""
        return self.db.add(
            "foreshadowing",
            content,
            {
                "type": "foreshadowing",
                "name": name,
                "embed_chapter": embed_chapter,
                "recover_chapter": recover_chapter,
                "status": "active",
            },
        )

    def get_foreshadowing_by_chapter(self, chapter):
        """获取某章节相关的伏笔"""
        all_fs = self.db.get_all("foreshadowing")

        results = []
        for fs in all_fs:
            meta = fs["metadata"]
            if (
                meta.get("embed_chapter") == chapter
                or meta.get("recover_chapter") == chapter
            ):
                results.append(fs)

        return results

    def get_active_foreshadowing(self):
        """获取活跃伏笔"""
        return self.db.get_by_metadata("foreshadowing", {"status": "active"})

    def recover_foreshadowing(self, name, chapter):
        """标记伏笔已回收"""
        all_fs = self.db.get_by_metadata("foreshadowing", {"name": name})

        for fs in all_fs:
            # 重新添加（更新）伏笔状态
            # 注意：简化版不支持更新，这里需要删除后重新添加
            pass

    # ========== 剧情 ==========

    def add_plot_point(self, name, content, chapter, plot_type="main"):
        """添加剧情点"""
        return self.db.add(
            "plot",
            content,
            {"type": "plot", "name": name, "chapter": chapter, "plot_type": plot_type},
        )

    def search_plot(self, query, n=5, plot_type=None):
        """搜索剧情"""
        return self.db.search(
            "plot", query, n, {"plot_type": plot_type} if plot_type else None
        )

    # ========== 审核 ==========

    def add_review(self, chapter_num, content, result, issues=None):
        """添加审核记录"""
        return self.db.add(
            "reviews",
            content,
            {
                "type": "review",
                "chapter": chapter_num,
                "result": result,
                "issues": issues or [],
            },
        )

    def get_review(self, chapter_num):
        """获取审核记录"""
        results = self.db.get_by_metadata("reviews", {"chapter": chapter_num})
        return results[0] if results else None


if __name__ == "__main__":
    # 测试
    db = NovelVectorDB("./test_vector_db")

    # 添加测试数据
    db.add_character(
        "林诗雨",
        "林诗雨，女，17岁，主角的妹妹，学生，活泼可爱，表面大大咧咧但实际关心哥哥，隐藏血脉（后续觉醒）",
        chapter=1,
        role="女主",
    )

    db.add_character(
        "叶尘",
        "叶尘，男，18岁，主角，江城大学学生，性格杀伐果断，金手指：超能进化系统",
        chapter=1,
        role="主角",
    )

    # 搜索
    print("搜索结果：")
    results = db.search_characters("妹妹")
    for r in results:
        print(f"  - {r['metadata']['name']}: {r['score']:.3f}")
