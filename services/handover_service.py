"""Handover service for project interruption recovery"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class HandoverService:
    """Manage handover documents for project interruption recovery"""

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.memory_path = self.project_path / "memory"
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.handover_file = self.memory_path / "handover.md"

    def create_handover(self, current_chapter: int, next_tasks: List[str],
                       special_notes: str = "", interrupted: bool = True) -> Dict:
        """Create a handover document

        Args:
            current_chapter: Current chapter number
            next_tasks: List of tasks to complete
            special_notes: Special notes for next session
            interrupted: Whether this is an unexpected interruption

        Returns:
            Handover metadata
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        date_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

        handover_content = f"""# 中断交接

## 项目信息
- 项目名：{self.project_path.name}
- 题材：{self._get_genre_from_project() or '未指定'}
- 当前章节：第 {current_chapter} 章
- 生成时间：{date_str}

## 写作进度
- 上一章：chapter-{current_chapter:03d}.md
- 写作状态：{'中断中' if interrupted else '进行中'}
- 完成章节：{current_chapter - 1} 章

## 待办事项
"""

        for i, task in enumerate(next_tasks, 1):
            handover_content += f"- [ ] {task}\n"

        handover_content += f"""
## 特殊说明
{special_notes or '无特殊说明'}

## 记忆库状态
- states.md：{'已更新' if (self.memory_path / 'states.md').exists() else '需更新'}
- foreshadowing.md：{'已更新' if (self.memory_path / 'foreshadowing.md').exists() else '需更新'}
- chapters.md：{'已更新' if (self.memory_path / 'chapters.md').exists() else '需更新'}

## 检查点
- 最新检查点：{self._get_latest_checkpoint_info() or '无'}
"""

        # Save handover file
        with open(self.handover_file, 'w', encoding='utf-8') as f:
            f.write(handover_content)

        return {
            "success": True,
            "file": str(self.handover_file),
            "timestamp": timestamp,
            "current_chapter": current_chapter
        }

    def _get_genre_from_project(self) -> str:
        """Get genre from project metadata"""
        project_file = self.project_path / "project.json"
        if project_file.exists():
            with open(project_file, 'r', encoding='utf-8') as f:
                project = json.load(f)
            return project.get("settings", {}).get("genre", "")
        return ""

    def _get_latest_checkpoint_info(self) -> str:
        """Get latest checkpoint information"""
        checkpoint_dir = self.memory_path / "checkpoints"
        if not checkpoint_dir.exists():
            return ""

        checkpoints = list(checkpoint_dir.glob("checkpoint-*.json"))
        if not checkpoints:
            return ""

        # Get the latest checkpoint (highest chapter range)
        checkpoints.sort(key=lambda x: int(x.stem.split('-')[-1]), reverse=True)
        latest = checkpoints[0].stem  # checkpoint-001-003 -> checkpoint-001-003

        return latest

    def read_handover(self) -> Optional[Dict]:
        """Read existing handover document"""
        if not self.handover_file.exists():
            return None

        with open(self.handover_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "success": True,
            "content": content,
            "file": str(self.handover_file)
        }

    def clear_handover(self) -> bool:
        """Delete handover document (used when resume completed)"""
        if self.handover_file.exists():
            self.handover_file.unlink()
            return True
        return False

    def get_resume_context(self) -> Dict:
        """Get context for resuming work

        Returns context including:
        - Last checkpoints
        - Last handover notes
        - Current project state
        """
        context = {
            "handover": None,
            "checkpoint": None,
            "project": None
        }

        # Read handover if exists
        handover = self.read_handover()
        if handover:
            context["handover"] = handover

        # Get latest checkpoint
        from services.checkpoint_service import CheckpointService
        checkpoint_service = CheckpointService(self.project_path)
        latest_cp = checkpoint_service.get_latest_checkpoint()
        if latest_cp:
            context["checkpoint"] = latest_cp

        # Get project info
        project_file = self.project_path / "project.json"
        if project_file.exists():
            with open(project_file, 'r', encoding='utf-8') as f:
                context["project"] = json.load(f)

        return context
