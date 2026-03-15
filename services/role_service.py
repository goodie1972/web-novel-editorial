"""Role-based routing service for multi-role AI generation"""
from typing import Dict, Optional


class RoleRouter:
    """Route requests to appropriate models based on role"""

    DEFAULT_ROLES = {
        "editor_in_chief": "claude",
        "researcher": "claude",
        "writer": "qwen",
        "editor": "claude"
    }

    def __init__(self, role_models: Optional[Dict] = None):
        self.role_models = role_models or self.DEFAULT_ROLES

    def get_model_for_role(self, role: str) -> str:
        """Get model name for role"""
        return self.role_models.get(role, "claude")

    def update_role_model(self, role: str, model: str) -> None:
        """Update model assignment for role"""
        self.role_models[role] = model
