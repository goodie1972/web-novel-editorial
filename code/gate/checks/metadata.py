"""
元数据检查器

检查章节文件末尾是否包含必需的元数据
"""

import re
from typing import List, Optional


class MetadataChecker:
    """章节元数据检查器 - 元数据在章节末尾"""
    
    # 写手填写字段（提交初稿时）
    WRITER_FIELDS = [
        "chapter",      # 章节号
        "title",       # 章节大纲标题
        "author_title",  # 作者自拟标题
        "draft_time",  # 初稿时间
        "draft_word_count",  # 写手估算的字数
    ]
    
    # 编辑填写字段（审核完成后）
    EDITOR_FIELDS = [
        "editor_review_time",  # 编辑审核时间
        "editor_word_count",   # 编辑复核的实际字数
    ]
    
    # 总编填写字段（确认完成后）
    EDITOR_CHIEF_FIELDS = [
        "final_time",          # 总编确认时间
        "final_word_count",    # 总编核实的最终字数（必须统计）
    ]
    
    # 必需字段（写手必须提供）
    REQUIRED_FIELDS = WRITER_FIELDS
    
    def check(self, content: str, result, strict: bool = True, role: str = "writer"):
        """
        检查元数据
        
        Args:
            content: 章节文件内容
            result: GateResult 对象
            strict: 是否检查所有字段（False则只检查基础字段）
            role: 检查角色 - "writer"(写手), "editor"(编辑), "editor_chief"(总编)
        """
        # 提取末尾的 YAML 元数据
        metadata = self._extract_metadata_from_end(content)
        
        if not metadata:
            result.add_check(
                "元数据",
                False,
                "未找到章节末尾的元数据块"
            )
            return
        
        # 根据角色检查不同字段
        if role == "writer":
            self._check_writer_fields(metadata, result)
        elif role == "editor":
            self._check_editor_fields(metadata, result)
        elif role == "editor_chief":
            self._check_editor_chief_fields(metadata, result)
        
        # 严格模式：检查所有字段
        if strict:
            all_fields = self.WRITER_FIELDS + self.EDITOR_FIELDS + self.EDITOR_CHIEF_FIELDS
            missing = []
            for field in all_fields:
                if field not in metadata or not metadata[field]:
                    missing.append(field)
            
            if missing:
                result.add_check(
                    "完整元数据",
                    False,
                    f"缺少字段: {', '.join(missing)}"
                )
            else:
                result.add_check(
                    "完整元数据",
                    True,
                    f"字数:{metadata.get('final_word_count', metadata.get('editor_word_count', metadata.get('draft_word_count', '?')))}"
                )
    
    def _check_writer_fields(self, metadata: dict, result):
        """检查写手字段"""
        missing = []
        for field in self.WRITER_FIELDS:
            if field not in metadata or not metadata[field]:
                missing.append(field)
        
        if missing:
            result.add_check(
                "写手元数据",
                False,
                f"缺少字段: {', '.join(missing)}"
            )
        else:
            result.add_check(
                "写手元数据",
                True,
                f"章节{metadata.get('chapter', '?')}"
            )
    
    def _check_editor_fields(self, metadata: dict, result):
        """检查编辑字段"""
        # 检查写手字段是否存在
        missing = []
        for field in self.WRITER_FIELDS:
            if field not in metadata or not metadata[field]:
                missing.append(field)
        
        if missing:
            result.add_check(
                "写手字段",
                False,
                f"缺少字段: {', '.join(missing)}"
            )
            return
        
        # 检查编辑字段
        editor_missing = []
        for field in self.EDITOR_FIELDS:
            if field not in metadata or not metadata[field]:
                editor_missing.append(field)
        
        if editor_missing:
            result.add_check(
                "编辑元数据",
                False,
                f"缺少字段: {', '.join(editor_missing)}"
            )
        else:
            result.add_check(
                "编辑元数据",
                True,
                f"字数:{metadata.get('editor_word_count', '?')}"
            )
    
    def _check_editor_chief_fields(self, metadata: dict, result):
        """检查总编字段"""
        # 检查必要字段
        base_fields = self.WRITER_FIELDS + self.EDITOR_FIELDS
        missing = []
        for field in base_fields:
            if field not in metadata or not metadata[field]:
                missing.append(field)
        
        if missing:
            result.add_check(
                "必要字段",
                False,
                f"缺少字段: {', '.join(missing)}"
            )
            return
        
        # 检查总编字段
        chief_missing = []
        for field in self.EDITOR_CHIEF_FIELDS:
            if field not in metadata or not metadata[field]:
                chief_missing.append(field)
        
        if chief_missing:
            result.add_check(
                "总编元数据",
                False,
                f"缺少字段: {', '.join(chief_missing)}"
            )
        else:
            result.add_check(
                "总编元数据",
                True,
                f"字数:{metadata.get('final_word_count', '?')}"
            )
    
    def _extract_metadata_from_end(self, content: str) -> dict:
        """从内容末尾提取 YAML 元数据"""
        # 匹配末尾的 --- 包裹的元数据块
        pattern = r'---\s*\n(.*?)\n---'
        
        # 从末尾匹配
        matches = list(re.finditer(pattern, content, re.DOTALL))
        
        if not matches:
            return {}
        
        # 取最后一个匹配（章节末尾的元数据）
        last_match = matches[-1]
        metadata_block = last_match.group(1)
        
        metadata = {}
        for line in metadata_block.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')
        
        return metadata
    
    def _extract_metadata(self, content: str) -> dict:
        """从内容中提取 YAML 元数据（兼容旧版本-开头）"""
        # 匹配开头或末尾的元数据块
        pattern = r'^---\s*\n(.*?)\n---'
        match = re.match(pattern, content, re.DOTALL)
        
        if not match:
            # 尝试从末尾提取
            return self._extract_metadata_from_end(content)
        
        metadata_block = match.group(1)
        metadata = {}
        
        for line in metadata_block.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')
        
        return metadata
    
    def generate_template(self, chapter: int, title: str = "", author_title: str = "") -> str:
        """生成章节模板（元数据在末尾）"""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f'''# {title}

（章节内容...）

---

## 元数据

```yaml
chapter: {chapter}
title: "{title}"
author_title: "{author_title}"
draft_time: "{now}"
draft_word_count: 0  # 写手填写（估算）
editor_review_time: ""  # 编辑填写
editor_word_count: 0  # 编辑填写（实际统计）
final_time: ""  # 总编填写
final_word_count: 0  # 总编填写（实际统计）
```

'''