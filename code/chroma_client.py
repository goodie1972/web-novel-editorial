# -*- coding: utf-8 -*-
"""
Chroma 向量数据库客户端
用于网文编辑部的长记忆系统
"""

import chromadb
from chromadb.config import Settings
import os


class ChromaClient:
    """Chroma 向量数据库客户端"""

    def __init__(self, persist_directory="./chroma_data"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_directory, settings=Settings(anonymized_telemetry=False)
        )
        self.collections = {}
        self.init_collections()

    def init_collections(self):
        """初始化所有 collections"""
        collection_configs = {
            "world": "世界观设定",
            "characters": "人物设定",
            "skills": "技能设定",
            "chapters": "章节摘要",
            "foreshadowing": "伏笔记录",
            "plot": "剧情线",
            "reviews": "审核记录",
        }

        for name, desc in collection_configs.items():
            try:
                self.collections[name] = self.client.get_collection(name)
            except:
                self.collections[name] = self.client.create_collection(
                    name=name, metadata={"description": desc}
                )

    def get_collection(self, name):
        """获取指定的 collection"""
        if name not in self.collections:
            self.init_collections()
        return self.collections[name]

    def add(self, collection_name, documents, metadatas=None, ids=None):
        """添加文档到 collection"""
        collection = self.get_collection(collection_name)

        if ids is None:
            ids = [f"{collection_name}_{i}" for i in range(len(documents))]

        collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query(self, collection_name, query_texts, n_results=3, where=None):
        """查询文档"""
        collection = self.get_collection(collection_name)

        return collection.query(
            query_texts=query_texts, n_results=n_results, where=where
        )

    def get(self, collection_name, where=None, where_document=None, ids=None):
        """获取文档"""
        collection = self.get_collection(collection_name)

        return collection.get(where=where, where_document=where_document, ids=ids)

    def update(self, collection_name, ids, documents=None, metadatas=None):
        """更新文档"""
        collection = self.get_collection(collection_name)

        collection.update(ids=ids, documents=documents, metadatas=metadatas)

    def reset(self):
        """重置所有数据（谨慎使用）"""
        self.client.reset()


if __name__ == "__main__":
    # 测试连接
    client = ChromaClient("./chroma_data")
    print("Chroma 连接成功！")
    print("Collections:", list(client.collections.keys()))
