# tests/test_html_generator.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from markdown_parser import Chapter
from html_generator import generate_html, generate_toc


def test_generate_toc():
    chapters = [
        Chapter(1, "第一章", None, "body", 3000, file_path=None),
        Chapter(2, "第二章", None, "body", 3500, file_path=None),
    ]
    toc = generate_toc(chapters)
    assert "第一章" in toc
    assert "3000" in toc


def test_generate_html():
    chapters = [
        Chapter(
            1,
            "第一章",
            "穿越",
            "正文内容",
            3000,
            "2026-03-06 08:00",
            "2026-03-06 09:00",
            "2026-03-06 10:00",
            file_path=None,
        ),
    ]
    html = generate_html(chapters, "我的小说")
    assert "第一章" in html
    assert "穿越" in html
    assert "3000" in html
    assert "sidebar" in html.lower()
