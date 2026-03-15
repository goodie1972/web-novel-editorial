"""Checkpoint service for web novel projects"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class CheckpointService:
    """Manage checkpoints for project interruption recovery"""

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.checkpoint_dir = self.project_path / "memory" / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def create_checkpoint(self, chapter_start: int, chapter_end: int,
                         files: List[Dict], memory_files: List[str]) -> Dict:
        """Create a checkpoint for specified chapters

        Args:
            chapter_start: Start chapter number
            chapter_end: End chapter number
            files: List of files to save {relative_path, content}
            memory_files: List of memory file names to save

        Returns:
            Checkpoint metadata
        """
        checkpoint_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        checkpoint_data = {
            "id": checkpoint_id,
            "timestamp": timestamp,
            "chapter_start": chapter_start,
            "chapter_end": chapter_end,
            "files": files,
            "memory_files": memory_files
        }

        # Save checkpoint file
        checkpoint_file = self.checkpoint_dir / f"checkpoint-{chapter_start:03d}-{chapter_end:03d}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

        return checkpoint_data

    def get_latest_checkpoint(self) -> Optional[Dict]:
        """Get the most recent checkpoint"""
        checkpoints = self.list_checkpoints()
        if not checkpoints:
            return None
        return checkpoints[0]  # Sorted by chapter range, last is latest

    def get_checkpoint_by_chapter(self, chapter_num: int) -> Optional[Dict]:
        """Get checkpoint that contains specified chapter"""
        checkpoints = self.list_checkpoints()
        for cp in checkpoints:
            if cp["chapter_start"] <= chapter_num <= cp["chapter_end"]:
                return cp
        return None

    def list_checkpoints(self) -> List[Dict]:
        """List all checkpoints, sorted by chapter range (latest first)"""
        checkpoints = []
        for checkpoint_file in self.checkpoint_dir.glob("checkpoint-*.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    cp = json.load(f)
                    checkpoints.append(cp)
            except Exception:
                continue

        # Sort by chapter_end descending (latest first)
        checkpoints.sort(key=lambda x: x["chapter_end"], reverse=True)
        return checkpoints

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint"""
        for checkpoint_file in self.checkpoint_dir.glob("checkpoint-*.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    cp = json.load(f)
                    if cp["id"] == checkpoint_id:
                        checkpoint_file.unlink()
                        return True
            except Exception:
                continue
        return False

    def clear_checkpoints(self, keep_latest: int = 1) -> int:
        """Clear old checkpoints, keeping latest N

        Args:
            keep_latest: Number of latest checkpoints to keep

        Returns:
            Number of checkpoints deleted
        """
        checkpoints = self.list_checkpoints()
        deleted = 0

        if len(checkpoints) > keep_latest:
            for cp in checkpoints[keep_latest:]:
                for checkpoint_file in self.checkpoint_dir.glob("checkpoint-*.json"):
                    try:
                        with open(checkpoint_file, 'r', encoding='utf-8') as f:
                            stored_cp = json.load(f)
                            if stored_cp["id"] == cp["id"]:
                                checkpoint_file.unlink()
                                deleted += 1
                                break
                    except Exception:
                        continue

        return deleted


# For backward compatibility with older project structure
class LegacyCheckpointService:
    """Legacy checkpoint service using YAML format"""

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.checkpoint_dir = self.project_path / "memory" / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def create_checkpoint_yaml(self, chapter_count: int, project_name: str,
                               files: List[str], memory_files: List[str]) -> Dict:
        """Create checkpoint in YAML-compatible format

        Args:
            chapter_count: Number of chapters completed
            project_name: Name of the project
            files: List of chapter files
            memory_files: List of memory files

        Returns:
            Checkpoint metadata
        """
        checkpoint_id = str(uuid.uuid4())[:8]
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        checkpoint_data = {
            "checkpoint": {
                "id": checkpoint_id,
                "timestamp": timestamp,
                "chapter": chapter_count,
                "project": project_name,
                "files": files,
                "memory": memory_files
            }
        }

        checkpoint_file = self.checkpoint_dir / f"checkpoint-{checkpoint_id}.yaml"
        # Save as JSON for consistency
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

        return checkpoint_data
