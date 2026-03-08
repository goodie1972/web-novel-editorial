# markdown_parser.py
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Chapter:
    chapter_num: int
    title: str
    author_title: Optional[str]
    body: str
    word_count: int
    draft_time: Optional[str] = None
    editor_review_time: Optional[str] = None
    final_time: Optional[str] = None
    file_path: Optional[Path] = None


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 frontmatter 元数据和正文"""
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    fm_text = match.group(1)
    body = match.group(2).strip()

    meta = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            # 转换类型
            if key == "chapter":
                value = int(value)
            elif key in ("word_count",):
                value = int(value)

            meta[key] = value

    return meta, body


def parse_chapter_file(file_path: Path) -> Chapter:
    """解析单个章节文件"""
    content = file_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    # 如果没有frontmatter，尝试从文件名提取章节号
    chapter_num = meta.get("chapter", 0)
    if chapter_num == 0:
        # 从文件名提取，如 chapter-001.md -> 1
        match = re.search(r"chapter[-_]?(\d+)", file_path.name, re.IGNORECASE)
        if match:
            chapter_num = int(match.group(1))

    # 如果title为空，尝试从正文第一行提取
    title = meta.get("title", "")
    if not title and body:
        # 第一行通常是 # 第X章 标题
        first_line = body.strip().split("\n")[0] if body.strip() else ""
        match = re.match(r"#\s*第[一二三四五六七八九十百千\d]+章\s*(.*)", first_line)
        if match:
            title = match.group(1).strip()
        else:
            # 直接使用第一行作为标题
            title = first_line.lstrip("#").strip()

    return Chapter(
        chapter_num=chapter_num,
        title=title,
        author_title=meta.get("author_title"),
        body=body,
        word_count=meta.get("word_count", len(body)),
        draft_time=meta.get("draft_time"),
        editor_review_time=meta.get("editor_review_time"),
        final_time=meta.get("final_time"),
        file_path=file_path,
    )


def scan_chapters(
    project_path: Path,
    start: Optional[int] = None,
    end: Optional[int] = None,
    chapters: Optional[list[int]] = None,
) -> list[Chapter]:
    """扫描项目目录获取章节列表"""
    chapters_dir = project_path / "chapters"

    if not chapters_dir.exists():
        raise FileNotFoundError(f"Chapters directory not found: {chapters_dir}")

    # 查找所有 md 文件
    md_files = sorted(chapters_dir.glob("*.md"))

    result = []
    for f in md_files:
        try:
            chapter = parse_chapter_file(f)

            # 过滤范围
            if start and chapter.chapter_num < start:
                continue
            if end and chapter.chapter_num > end:
                continue
            if chapters and chapter.chapter_num not in chapters:
                continue

            result.append(chapter)
        except Exception:
            continue

    return sorted(result, key=lambda x: x.chapter_num)
