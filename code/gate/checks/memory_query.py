"""
记忆库查询检查器

检查写手/编辑在操作前是否查询了记忆库
"""

import os
from pathlib import Path
from typing import List, Optional


class MemoryQueryChecker:
    """记忆库查询检查器"""
    
    # 必需查询的记忆库文件
    REQUIRED_FILES = {
        "writer": [
            "states.md",        # 人物状态
            "foreshadowing.md",  # 伏笔状态
            "chapters.md",       # 章节摘要
        ],
        "editor": [
            "states.md",         # 人物状态（核对一致性）
            "project.md",        # 项目设定（核对风格）
        ],
        "chief": [
            "chapters.md",      # 章节元数据
            "states.md",        # 人物状态
        ]
    }
    
    def check(self, result, role: str = "writer", chapter: int = 1, project_path: str = None):
        """
        检查是否查询了记忆库
        
        Args:
            result: GateResult 对象
            role: 角色 (writer/editor/chief)
            chapter: 当前章节号
            project_path: 项目路径
        """
        if not project_path:
            result.add_check(
                "记忆库检查",
                False,
                "未提供项目路径"
            )
            return
        
        memory_path = Path(project_path) / "memory"
        
        # 检查查询日志是否存在
        query_log = memory_path / "query_log.md"
        
        if not query_log.exists():
            result.add_check(
                "查询记录",
                False,
                f"未找到查询日志，请先查询记忆库"
            )
            return
        
        # 读取查询日志
        content = query_log.read_text(encoding="utf-8")
        
        # 检查必需的查询项
        required_files = self.REQUIRED_FILES.get(role, [])
        missing_files = []
        
        for filename in required_files:
            if filename not in content:
                missing_files.append(filename)
        
        if missing_files:
            result.add_check(
                "记忆库查询",
                False,
                f"未查询: {', '.join(missing_files)}"
            )
        else:
            result.add_check(
                "记忆库查询",
                True,
                f"已查询{len(required_files)}个记忆库文件"
            )
    
    def log_query(self, project_path: str, role: str, items: List[str]):
        """
        记录查询操作
        
        Args:
            project_path: 项目路径
            role: 角色
            items: 查询的项目列表
        """
        from datetime import datetime
        
        memory_path = Path(project_path) / "memory"
        query_log = memory_path / "query_log.md"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"\n## [{timestamp}] {role} 查询\n"
        log_entry += f"- 查询项目: {', '.join(items)}\n"
        
        # 追加写入
        with open(query_log, "a", encoding="utf-8") as f:
            f.write(log_entry)
    
    def create_query_template(self, project_path: str) -> str:
        """创建查询日志模板"""
        template = """# 记忆库查询日志

## 说明
- 写手每章写作前必须查询
- 编辑审核前必须查询
- 每次查询后自动记录

---

"""
        
        memory_path = Path(project_path) / "memory"
        query_log = memory_path / "query_log.md"
        
        if not query_log.exists():
            query_log.write_text(template, encoding="utf-8")
        
        return str(query_log)