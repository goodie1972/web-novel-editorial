# tests/test_markdown_parser.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from markdown_parser import Chapter, parse_chapter_file, parse_frontmatter


def test_parse_frontmatter():
    content = """---
chapter: 1
title: "第一章 穿越"
author_title: "穿越修仙"
draft_time: "2026-03-06 08:00:00"
word_count: 3500
---

正文内容"""
    meta, body = parse_frontmatter(content)
    assert meta["chapter"] == 1
    assert meta["title"] == "第一章 穿越"
    assert "正文内容" in body


def test_parse_chapter_file(tmp_path):
    chapter_file = tmp_path / "chapter_001.md"
    chapter_file.write_text("""---
chapter: 1
title: "第一章"
word_count: 3000
---

正文""")

    chapter = parse_chapter_file(chapter_file)
    assert chapter.chapter_num == 1
    assert chapter.title == "第一章"
    assert chapter.word_count == 3000
