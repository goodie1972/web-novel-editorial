# tests/test_aggregator.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aggregator import generate_summary_markdown


def test_generate_summary_markdown(tmp_path):
    from markdown_parser import Chapter

    chapters = [
        Chapter(
            1,
            "第一章 穿越",
            "穿越修仙",
            "正文1",
            3000,
            "2026-03-06 08:00",
            "2026-03-06 09:00",
            "2026-03-06 10:00",
        ),
        Chapter(
            2,
            "第二章 入世",
            "入世修炼",
            "正文2",
            3500,
            "2026-03-06 11:00",
            "2026-03-06 12:00",
            "2026-03-06 13:00",
        ),
    ]

    md = generate_summary_markdown(chapters, "我的小说")
    assert "我的小说" in md
    assert "第一章 穿越" in md
    assert "穿越修仙" in md
    assert "3000" in md
    assert "2026-03-06 10:00" in md
