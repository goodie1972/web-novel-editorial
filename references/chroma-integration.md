# Chroma 向量数据库集成方案

本文档定义如何使用 Chroma 向量数据库实现长记忆系统。

---

## 一、架构概述

### 1.1 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    网文编辑部工作流                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │
│  │ 研究员  │───▶│  写手   │───▶│  编辑   │───▶│  总编   │ │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘ │
│       │              │              │              │         │
│       ▼              ▼              ▼              ▼         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Chroma 向量数据库                        │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │   │
│  │  │设定集合 │ │人物集合 │ │章节集合 │ │伏笔集合 │  │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 数据流

```
写入流程：
  章节完成 → 提取关键信息 → 向量化 → 存入Chroma → 更新索引

查询流程：
  写作/审核 → 自然语言查询 → Chroma检索 → 返回相关设定 → 辅助写作
```

---

## 二、数据模型

### 2.1 Collections 设计

| Collection | 用途 | 示例 |
|------------|------|------|
| `world` | 世界观设定 | 等级体系、势力分布、地理设定 |
| `characters` | 人物设定 | 主角、配角、反派的详细设定 |
| `skills` | 技能设定 | 技能名称、威力、进化路线 |
| `chapters` | 章节摘要 | 每章的核心内容、人物、伏笔 |
| `foreshadowing` | 伏笔记录 | 伏笔内容、埋入/回收章节 |
| `plot` | 剧情线 | 主线、支线、情感线发展 |
| `reviews` | 审核记录 | 审核意见、修改建议 |

### 2.2 Document 结构

每个 document 包含：

```python
{
    "id": "char_li_shui_yu_001",           # 唯一标识：类型_名称_序号
    "content": "林诗雨，女，17岁，主角的妹妹...",  # 待向量化的内容
    "metadata": {                           # 元数据（用于过滤）
        "type": "character",               # 类型
        "name": "林诗雨",                   # 名称
        "chapter": 1,                      # 首次出场章节
        "category": "配角",                 # 分类
        "status": "active"                 # 状态
    }
}
```

---

## 三、代码实现

### 3.1 安装依赖

```bash
pip install chromadb sentence-transformers
```

### 3.2 初始化

```python
# chroma_client.py

import chromadb
from chromadb.config import Settings

class ChromaClient:
    def __init__(self, persist_directory="./chroma_data"):
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.init_collections()
    
    def init_collections(self):
        """初始化所有 collections"""
        collections = [
            "world", "characters", "skills", 
            "chapters", "foreshadowing", "plot", "reviews"
        ]
        for name in collections:
            try:
                self.client.get_collection(name)
            except:
                self.client.create_collection(
                    name=name,
                    metadata={"description": f"{name} collection"}
                )
    
    def get_collection(self, name):
        return self.client.get_collection(name)
```

### 3.3 写入数据

```python
# chroma_writer.py

from chroma_client import ChromaClient

class ChromaWriter:
    def __init__(self):
        self.client = ChromaClient()
    
    def add_world_setting(self, content, metadata):
        """写入世界观设定"""
        collection = self.client.get_collection("world")
        doc_id = f"world_{metadata.get('name', 'unnamed')}"
        collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
    
    def add_character(self, name, content, chapter, role):
        """写入人物设定"""
        collection = self.client.get_collection("characters")
        doc_id = f"char_{name}_{chapter}"
        collection.add(
            documents=[content],
            metadatas=[{
                "type": "character",
                "name": name,
                "chapter": chapter,
                "role": role
            }],
            ids=[doc_id]
        )
    
    def add_chapter_summary(self, chapter_num, content, metadata):
        """写入章节摘要"""
        collection = self.client.get_collection("chapters")
        doc_id = f"chapter_{chapter_num:03d}"
        collection.add(
            documents=[content],
            metadatas=[{"chapter": chapter_num, **metadata}],
            ids=[doc_id]
        )
    
    def add_foreshadowing(self, name, content, embed_chapter,回收chapter):
        """写入伏笔"""
        collection = self.client.get_collection("foreshadowing")
        doc_id = f"fs_{name}_{embed_chapter}"
        collection.add(
            documents=[content],
            metadatas=[{
                "type": "foreshadowing",
                "name": name,
                "embed_chapter": embed_chapter,
                "回收_chapter": 回收_chapter,
                "status": "active"
            }],
            ids=[doc_id]
        )
```

### 3.4 查询数据

```python
# chroma_reader.py

from chroma_client import ChromaClient

class ChromaReader:
    def __init__(self):
        self.client = ChromaClient()
    
    def search_world(self, query, n=3):
        """查询世界观设定"""
        collection = self.client.get_collection("world")
        return collection.query(
            query_texts=[query],
            n_results=n
        )
    
    def search_characters(self, query, role=None, n=5):
        """查询人物设定"""
        collection = self.client.get_collection("characters")
        where = {"role": role} if role else None
        return collection.query(
            query_texts=[query],
            n_results=n,
            where=where
        )
    
    def get_character_by_chapter(self, chapter, n=10):
        """获取某章节出场的人物"""
        collection = self.client.get_collection("characters")
        return collection.get(
            where={"chapter": chapter}
        )
    
    def get_foreshadowing_by_chapter(self, chapter, status="active"):
        """获取某章节相关的伏笔"""
        collection = self.client.get_collection("foreshadowing")
        return collection.get(
            where={
                "$or": [
                    {"embed_chapter": chapter},
                    {"回收_chapter": chapter}
                ],
                "status": status
            }
        )
    
    def search_chapters(self, query, n=3):
        """搜索历史章节"""
        collection = self.client.get_collection("chapters")
        return collection.query(
            query_texts=[query],
            n_results=n
        )
```

### 3.5 更新数据

```python
# chroma_updater.py

from chroma_writer import ChromaWriter

class ChromaUpdater:
    def __init__(self):
        self.writer = ChromaWriter()
    
    def 回收_foreshadowing(self, name, chapter):
        """标记伏笔已回收"""
        collection = self.writer.client.get_collection("foreshadowing")
        # 查询并更新状态
        results = collection.get(where={"name": name})
        if results["ids"]:
            collection.update(
                ids=[results["ids"][0]],
                metadatas=[{"status": "recovered", "回收_chapter": chapter}]
            )
    
    def update_character_status(self, name, status):
        """更新人物状态"""
        collection = self.writer.client.get_collection("characters")
        results = collection.get(where={"name": name})
        if results["ids"]:
            collection.update(
                ids=[results["ids"][0]],
                metadatas=[{"status": status}]
            )
```

---

## 四、与工作流集成

### 4.1 章节完成后写入

```python
# 章节完成后自动调用

def on_chapter_complete(chapter_num, chapter_content, summary):
    writer = ChromaWriter()
    
    # 1. 写入章节摘要
    writer.add_chapter_summary(
        chapter_num=chapter_num,
        content=summary["核心内容"],
        metadata={
            "title": summary["标题"],
            "word_count": summary["字数"],
            "main_event": summary["核心事件"],
            "characters": summary["出场人物"],
            "foreshadowing": summary["伏笔"]
        }
    )
    
    # 2. 写入新出现的伏笔
    for fs in summary["新伏笔"]:
        writer.add_foreshadowing(
            name=fs["名称"],
            content=fs["内容"],
            embed_chapter            回收_ch=chapter_num,
apter=fs["计划回收章节"]
        )
    
    # 3. 标记已回收的伏笔
    for fs in summary["回收伏笔"]:
        updater = ChromaUpdater()
        updater.回收_foreshadowing(fs["名称"], chapter_num)
    
    print(f"第{chapter_num}章已存入向量数据库")
```

### 4.2 写作前查询

```python
# 写手写作前查询相关设定

def on_write_chapter(chapter_num):
    reader = ChromaReader()
    
    # 1. 查询最近几章的内容
    recent_chapters = reader.search_chapters(
        f"第{chapter_num-3}章到第{chapter_num-1}章的内容",
        n=3
    )
    
    # 2. 查询本章需要出场的人物
    characters = reader.get_character_by_chapter(chapter_num)
    
    # 3. 查询本章相关的伏笔
    foreshadowing = reader.get_foreshadowing_by_chapter(chapter_num)
    
    # 4. 查询世界观设定
    world = reader.search_world(f"第{chapter_num}章涉及的设定")
    
    return {
        "recent_chapters": recent_chapters,
        "characters": characters,
        "foreshadowing": foreshadowing,
        "world": world
    }
```

### 4.3 审核时查询

```python
# 编辑审核时查询一致性

def on_review_chapter(chapter_num, content):
    reader = ChromaReader()
    
    # 1. 查询人物设定进行对比
    all_characters = reader.search_characters(
        f"本章出现的人物",
        n=10
    )
    
    # 2. 查询战力设定
    combat = reader.search_world(f"战力设定", n=3)
    
    # 3. 查询伏笔
    foreshadowing = reader.get_foreshadowing_by_chapter(chapter_num)
    
    # 4. 查询历史章节确认一致性
    history = reader.search_chapters(
        f"与本章相似的情节",
        n=5
    )
    
    return {
        "characters": all_characters,
        "combat": combat,
        "foreshadowing": foreshadowing,
        "history": history
    }
```

---

## 五、向量化模型

### 5.1 模型选择

```python
# embedding_model.py

from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        """
        推荐模型：
        - paraphrase-multilingual-MiniLM-L12-v2: 多语言，轻量效果好
        - paraphrase-multilingual-mpnet-base-v2: 效果更好，但更慢
        - text2vec-base-chinese: 中文专用
        """
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts):
        return self.model.encode(texts)
```

### 5.2 Chroma 配置

```python
# 初始化时指定 embedding function

from chromadb.config import Settings
import chromadb

client = chromadb.PersistentClient(
    path="./chroma_data",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

# 使用多语言模型
collection = client.create_collection(
    name="world",
    embedding_function=EmbeddingModel()
)
```

---

## 六、使用示例

### 6.1 初始化数据库

```python
# init_database.py

from chroma_client import ChromaClient
from chroma_writer import ChromaWriter

def init_project(project_data):
    """初始化项目时调用"""
    writer = ChromaWriter()
    
    # 1. 写入世界观设定
    for setting in project_data["world"]:
        writer.add_world_setting(
            content=setting["内容"],
            metadata={
                "type": "world",
                "name": setting["名称"],
                "category": setting["类别"]
            }
        )
    
    # 2. 写入人物设定
    for char in project_data["characters"]:
        writer.add_character(
            name=char["姓名"],
            content=char["完整设定"],
            chapter=char["首次出场章节"],
            role=char["角色类型"]
        )
    
    # 3. 写入技能设定
    for skill in project_data["skills"]:
        writer.add_skill(
            name=skill["名称"],
            content=skill["完整设定"],
            category=skill["类别"]
        )
    
    print("项目数据已初始化到向量数据库")
```

### 6.2 日常使用

```python
# 1. 写手开始写作第11章前
context = on_write_chapter(11)
print("相关设定：", context)

# 2. 章节完成后
on_chapter_complete(11, content, summary)

# 3. 编辑审核时
review_data = on_review_chapter(11, content)
print("审核参考：", review_data)
```

---

## 七、配置项

### 7.1 环境配置

```json
{
  "chroma": {
    "persist_directory": "./chroma_data",
    "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2"
  }
}
```

### 7.2 在 settings.json 中添加

```json
{
  "long_memory": {
    "enabled": true,
    "type": "chroma",
    "persist_directory": "./chroma_data",
    "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2"
  }
}
```

---

## 八、注意事项

1. **首次写入慢**：第一批数据需要生成向量，耗时较长，后续会缓存
2. **中文支持**：选择多语言模型或中文专用模型
3. **数据备份**：向量数据库需要定期备份
4. **清理策略**：项目结束后可选择保留或清理

---

## 修改记录

| 日期 | 修改人 | 修改内容 |
|------|--------|----------|
| 2026-02-17 | 总编 | 创建Chroma集成方案 |
