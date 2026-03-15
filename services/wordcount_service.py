"""Word count service for web novel chapters"""
import re
from pathlib import Path
from typing import Dict


class WordCountService:
    """Count words in chapter files with proper rules"""

    def count_file(self, file_path: str) -> Dict:
        """Count words in a file

        Rules:
        - Chinese characters: 1 word each
        - Punctuation: 1 word each
        - English words: 1 word each
        - Spaces: not counted
        - Markdown formatting: excluded

        Returns:
            Dict with actual_count, markdown_excluded, details
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract word count from YAML frontmatter if exists
        expected_count = self._extract_expected_word_count(content)

        # Process content
        original_length = len(content)

        # Remove code blocks
        content_no_code = re.sub(r'```[\s\S]*?```', '', content)

        # Remove markdown headers
        content_no_headers = re.sub(r'^#+\s+', '', content_no_code, flags=re.MULTILINE)

        # Remove bold/italic markers
        content_no_formatting = re.sub(r'\*\*|\*|_', '', content_no_headers)

        # Remove links
        content_no_links = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', content_no_formatting)

        # Remove YAML frontmatter
        content_no_yaml = re.sub(r'^---[\s\S]*?^---\n', '', content_no_links, flags=re.MULTILINE)

        # Remove chapter metadata block
        content_clean = re.sub(r'^---[\s\S]*?---$', '', content_no_yaml, flags=re.MULTILINE)

        # Remove extra whitespace for counting
        # Keep newlines for better accuracy
        content_for_counting = content_clean

        # Count Chinese characters
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', content_for_counting)
        chinese_count = len(chinese_chars)

        # Count English letters and numbers (words)
        english_words = re.findall(r'[a-zA-Z0-9]+', content_for_counting)
        english_count = len(english_words)

        # Count punctuation (excluding markdown chars)
        punctuation = re.findall(r'[，。！？；：、『』「」“”‘’（）【】—…]', content_for_counting)
        punctuation_count = len(punctuation)

        # Count英文标点
        english_punctuation = re.findall(r'[.,!?;:()\[\]{}\"\'`]', content_for_counting)
        eng_punct_count = len(english_punctuation)

        # Calculate total
        total_count = chinese_count + english_count + punctuation_count + eng_punct_count

        result = {
            "success": True,
            "filepath": str(file_path),
            "actual_count": total_count,
            "breakdown": {
                "chinese_chars": chinese_count,
                "english_words": english_count,
                "chinese_punctuation": punctuation_count,
                "english_punctuation": eng_punct_count
            },
            "markdown_excluded": original_length - len(content_clean),
            "expected_count": expected_count
        }

        return result

    def _extract_expected_word_count(self, content: str) -> int:
        """Extract expected word count from YAML frontmatter or metadata block"""
        # Try to extract from YAML frontmatter
        match = re.search(r'expected_word_count:\s*(\d+)', content)
        if match:
            return int(match.group(1))

        # Try to extract from metadata block
        match = re.search(r'word_count:\s*(\d+)', content)
        if match:
            return int(match.group(1))

        return 0

    def check_word_count(self, file_path: str, min_words: int = 4000) -> Dict:
        """Check if file meets minimum word count requirement

        Args:
            file_path: Path to chapter file
            min_words: Minimum required words (default 4000)

        Returns:
            Dict with check result
        """
        count_result = self.count_file(file_path)

        if not count_result["success"]:
            return count_result

        actual = count_result["actual_count"]
        expected = count_result.get("expected_count", min_words)

        if actual >= expected:
            check_result = {
                "passed": True,
                "message": f"字数达标：{actual} 字 (要求：≥{expected}字)",
                "actual_count": actual,
                "required_count": expected
            }
        else:
            shortfall = expected - actual
            check_result = {
                "passed": False,
                "message": f"字数不足：{actual} 字 (要求：≥{expected}字)，还需补充 {shortfall} 字",
                "actual_count": actual,
                "required_count": expected,
                "shortfall": shortfall
            }

        count_result.update(check_result)
        return count_result


# Global instance
wordcount_service = WordCountService()
