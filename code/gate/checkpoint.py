"""
检查点生成器

自动生成章节检查点
"""

import os
from pathlib import Path
from datetime import datetime
import yaml


def generate_checkpoint(project_path: str, chapter: int) -> str:
    """
    生成检查点
    
    Args:
        project_path: 项目路径
        chapter: 章节号（3的倍数）
    
    Returns:
        YAML格式的检查点内容
    """
    project_path = Path(project_path)
    memory_path = project_path / "memory"
    chapters_path = project_path / "outputs" / "chapters"
    
    # 收集章节数据
    chapters_data = []
    
    for i in range(1, chapter + 1):
        chapter_file = chapters_path / f"chapter-{i:02d}.md"
        chapter_meta_file = memory_path / "chapters.md"
        
        chapter_info = {
            "chapter": i,
            "file": f"chapter-{i:02d}.md",
            "exists": chapter_file.exists()
        }
        
        # 如果有元数据文件，提取摘要
        if chapter_meta_file.exists():
            try:
                content = chapter_meta_file.read_text(encoding="utf-8")
                # 简单提取（实际应该解析YAML）
                if f"chapter: {i}" in content:
                    # 提取该章节的摘要
                    chapter_info["has_metadata"] = True
                else:
                    chapter_info["has_metadata"] = False
            except:
                chapter_info["has_metadata"] = False
        else:
            chapter_info["has_metadata"] = False
        
        chapters_data.append(chapter_info)
    
    # 读取人物状态
    states_file = memory_path / "states.md"
    characters = []
    
    if states_file.exists():
        try:
            content = states_file.read_text(encoding="utf-8")
            # 简单提取（实际应该解析YAML/markdown表格）
            # 这里做个简化处理
            characters = [{"source": "states.md", "extracted": True}]
        except:
            characters = [{"source": "states.md", "extracted": False}]
    
    # 读取伏笔状态
    foreshadowing_file = memory_path / "foreshadowing.md"
    foreshadowing = []
    
    if foreshadowing_file.exists():
        try:
            content = foreshadowing_file.read_text(encoding="utf-8")
            foreshadowing = [{"source": "foreshadowing.md", "extracted": True}]
        except:
            foreshadowing = [{"source": "foreshadowing.md", "extracted": False}]
    
    # 读取项目信息
    project_file = memory_path / "project.md"
    project_info = {}
    
    if project_file.exists():
        try:
            content = project_file.read_text(encoding="utf-8")
            # 提取关键信息
            for line in content.split('\n'):
                if line.startswith("风格:") or line.startswith("- 风格"):
                    project_info["style"] = line.split(":", 1)[-1].strip()
                elif line.startswith("题材:") or line.startswith("- 题材"):
                    project_info["genre"] = line.split(":", 1)[-1].strip()
        except:
            pass
    
    # 生成检查点
    checkpoint = {
        "chapter": chapter,
        "timestamp": datetime.now().isoformat(),
        "project": project_info.get("genre", "未命名"),
        "style": project_info.get("style", "未指定"),
        "total_chapters": chapter,
        "characters": characters,
        "active_foreshadowing": foreshadowing,
        "recent_chapters": chapters_data[-3:] if len(chapters_data) >= 3 else chapters_data,
    }
    
    # 转换为YAML
    yaml_content = yaml.dump(checkpoint, allow_unicode=True, default_flow_style=False)
    
    header = f"""# 检查点 - 第{chapter}章
# 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# 用于: 意外中断恢复 / 人工交接

"""
    
    return header + yaml_content


def load_checkpoint(checkpoint_path: str) -> dict:
    """
    加载检查点
    
    Args:
        checkpoint_path: 检查点文件路径
    
    Returns:
        检查点数据字典
    """
    with open(checkpoint_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 跳过YAML头部注释
    lines = content.split('\n')
    yaml_lines = []
    in_header = False
    
    for line in lines:
        if line.startswith('#'):
            continue
        yaml_lines.append(line)
    
    yaml_content = '\n'.join(yaml_lines)
    
    return yaml.safe_load(yaml_content)


def list_checkpoints(memory_path: str) -> list:
    """
    列出所有检查点
    
    Args:
        memory_path: 记忆库路径
    
    Returns:
        检查点文件列表
    """
    checkpoint_dir = Path(memory_path) / "checkpoints"
    
    if not checkpoint_dir.exists():
        return []
    
    checkpoints = []
    
    for file in checkpoint_dir.glob("checkpoint-*.yaml"):
        # 提取章节号
        name = file.stem  # checkpoint-003
        chapter = int(name.split('-')[-1])
        
        checkpoints.append({
            "file": str(file),
            "chapter": chapter,
        })
    
    # 按章节号排序
    checkpoints.sort(key=lambda x: x["chapter"])
    
    return checkpoints