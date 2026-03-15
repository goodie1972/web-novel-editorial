"""Style library service for author style management"""
import json
from pathlib import Path
from typing import Dict, List


class StyleLibrary:
    """Manage author styles by genre"""

    def __init__(self, styles_file: Path):
        self.styles_file = Path(styles_file)
        self.styles = self._load_styles()

    def get_styles_by_genre(self, genre: str) -> List[Dict]:
        """Get applicable styles for genre"""
        return self.styles.get(genre, [])

    def get_all_genres(self) -> List[str]:
        """Get all available genres"""
        return list(self.styles.keys())

    def get_style_prompt(self, genre: str, style_name: str) -> str:
        """Get style application prompt"""
        styles = self.get_styles_by_genre(genre)
        for style in styles:
            if style["name"] == style_name:
                return style.get("prompt", "")
        return ""

    def _load_styles(self) -> Dict:
        """Load styles from JSON file"""
        if not self.styles_file.exists():
            return {}

        with open(self.styles_file, "r", encoding="utf-8") as f:
            return json.load(f)
