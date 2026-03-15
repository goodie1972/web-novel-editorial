"""Project management service for web novel editorial system"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ProjectManager:
    """Manage web novel projects with directory structure and metadata"""

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.projects_dir = self.base_dir / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def create_project(self, name: str, mode: str = "professional", settings: Optional[Dict] = None) -> Dict:
        """Create new project with directory structure"""
        project_id = str(uuid.uuid4())
        project_path = self.projects_dir / project_id

        # Create directory structure
        (project_path / "memory").mkdir(parents=True, exist_ok=True)
        (project_path / "outputs").mkdir(parents=True, exist_ok=True)
        (project_path / "outputs" / "stage4_settings").mkdir(parents=True, exist_ok=True)
        (project_path / "outputs" / "stage5_chapters").mkdir(parents=True, exist_ok=True)
        (project_path / "outputs" / "stage6_feedback").mkdir(parents=True, exist_ok=True)

        # Initialize memory collections
        collections = ["world", "characters", "skills", "chapters", "foreshadowing", "plot", "reviews"]
        for collection in collections:
            with open(project_path / "memory" / f"{collection}.json", "w", encoding="utf-8") as f:
                json.dump({"documents": []}, f, ensure_ascii=False, indent=2)

        # Create project metadata
        now = datetime.utcnow().isoformat() + "Z"
        project_data = {
            "id": project_id,
            "name": name,
            "mode": mode,
            "created_at": now,
            "updated_at": now,
            "current_stage": 1,
            "settings": settings or {},
            "stages": {}
        }

        self._save_project_file(project_id, project_data)
        return project_data

    def list_projects(self) -> List[Dict]:
        """List all projects with metadata"""
        projects = []
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                try:
                    project_data = self.load_project(project_dir.name)
                    projects.append({
                        "id": project_data["id"],
                        "name": project_data["name"],
                        "mode": project_data["mode"],
                        "current_stage": project_data.get("current_stage", 1),
                        "created_at": project_data["created_at"],
                        "updated_at": project_data["updated_at"]
                    })
                except Exception:
                    continue
        return sorted(projects, key=lambda x: x["updated_at"], reverse=True)

    def load_project(self, project_id: str) -> Dict:
        """Load project data"""
        project_file = self.projects_dir / project_id / "project.json"
        if not project_file.exists():
            raise FileNotFoundError(f"Project {project_id} not found")

        with open(project_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_project(self, project_id: str, data: Dict) -> None:
        """Save project data"""
        data["updated_at"] = datetime.utcnow().isoformat() + "Z"
        self._save_project_file(project_id, data)

    def update_stage(self, project_id: str, stage_num: int, status: str, data: Dict) -> None:
        """Update stage status and data"""
        project_data = self.load_project(project_id)

        if str(stage_num) not in project_data["stages"]:
            project_data["stages"][str(stage_num)] = {
                "status": status,
                "started_at": datetime.utcnow().isoformat() + "Z",
                "data": data,
                "quality_gate_passed": False
            }
        else:
            project_data["stages"][str(stage_num)]["status"] = status
            project_data["stages"][str(stage_num)]["data"] = data

        if status == "completed":
            project_data["stages"][str(stage_num)]["completed_at"] = datetime.utcnow().isoformat() + "Z"
            project_data["current_stage"] = stage_num + 1

        self.save_project(project_id, project_data)

    def check_quality_gate(self, project_id: str, stage_num: int) -> Dict:
        """Check if quality gate requirements met"""
        project_data = self.load_project(project_id)
        stage_data = project_data["stages"].get(str(stage_num), {})

        passed = False
        message = ""

        if stage_num == 1:
            passed = bool(stage_data.get("data", {}).get("requirements"))
            message = "需求确认完成" if passed else "请填写需求"
        elif stage_num == 3:
            core_elements = stage_data.get("data", {}).get("core_elements", {})
            completed = core_elements.get("completed_count", 0)
            passed = completed >= 12
            message = f"已完成 {completed}/12 核心要素" if not passed else "12核心要素已完成"
        else:
            passed = stage_data.get("status") == "completed"
            message = "阶段已完成" if passed else "阶段未完成"

        return {"passed": passed, "message": message}

    def _save_project_file(self, project_id: str, data: Dict) -> None:
        """Save project.json file"""
        project_file = self.projects_dir / project_id / "project.json"
        with open(project_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
