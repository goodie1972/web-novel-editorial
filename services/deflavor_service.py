"""AI de-flavoring service for pattern detection"""
import json
import re
from pathlib import Path
from typing import Dict, List


class AIDeflavoringService:
    """Detect and score AI writing patterns"""

    def __init__(self, patterns_file: Path):
        self.patterns_file = Path(patterns_file)
        self.patterns = self._load_patterns()

    def analyze_text(self, text: str) -> Dict:
        """Detect AI patterns and calculate score"""
        detected = []
        pattern_counts = {}

        for pattern in self.patterns:
            count = len(re.findall(pattern["regex"], text))
            if count > 0:
                detected.append({
                    "pattern": pattern["name"],
                    "category": pattern["category"],
                    "count": count,
                    "suggestion": pattern["suggestion"]
                })
                pattern_counts[pattern["name"]] = count

        score = self.calculate_quality_score(pattern_counts, len(text))
        suggestions = self.suggest_improvements(detected)

        return {
            "score": score,
            "detected_patterns": detected,
            "suggestions": suggestions
        }

    def calculate_quality_score(self, pattern_counts: Dict, text_length: int) -> int:
        """Score 0-100 based on pattern density"""
        if text_length == 0:
            return 100

        total_patterns = sum(pattern_counts.values())
        density = (total_patterns / text_length) * 1000

        if density == 0:
            return 100
        elif density < 1:
            return 90
        elif density < 3:
            return 75
        elif density < 5:
            return 60
        elif density < 10:
            return 40
        else:
            return 20

    def suggest_improvements(self, detected_patterns: List[Dict]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        for pattern in detected_patterns[:5]:
            suggestions.append(f"{pattern['pattern']}: {pattern['suggestion']}")
        return suggestions

    def _load_patterns(self) -> List[Dict]:
        """Load patterns from JSON file"""
        if not self.patterns_file.exists():
            return []

        with open(self.patterns_file, "r", encoding="utf-8") as f:
            return json.load(f)
