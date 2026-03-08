# Chapter Aggregator Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为网文编辑 skill 创建章节汇总工具，支持选择章节范围生成汇总 MD 和带侧边栏导航的 HTML。

**Architecture:** Python CLI 工具，扫描项目 chapters 目录，解析 frontmatter 元数据，生成汇总文档和 HTML。

**Tech Stack:** Python 3.8+, 标准库 (argparse, re, yaml, pathlib)

---

## Task 1: Create Project Structure

**Files:**
- Create: `C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/__init__.py`
- Create: `C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/markdown_parser.py`
- Create: `C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/html_generator.py`
- Create: `C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/aggregator.py`
- Create: `C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/cli.py`
- Create: `C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/tests/__init__.py`

**Step 1: Create directory**

```bash
mkdir -p "C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/tests"
```

**Step 2: Create empty __init__.py files**

```bash
touch "C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/__init__.py"
touch "C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/tests/__init__.py"
```

**Step 3: Commit**

```bash
git add code/chapter-aggregator/
git commit -m "feat: create chapter-aggregator project structure"
```

---

## Task 2: Implement markdown_parser.py

**Files:**
- Create: `C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/markdown_parser.py`

**Step 1: Write the test**

```python
# tests/test_markdown_parser.py
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from markdown_parser import Chapter, parse_chapter_file, parse_frontmatter

def test_parse_frontmatter():
    content = '''---
chapter: 1
title: "第一章 穿越"
author_title: "穿越修仙"
draft_time: "2026-03-06 08:00:00"
word_count: 3500
---

正文内容'''
    meta, body = parse_frontmatter(content)
    assert meta['chapter'] == 1
    assert meta['title'] == "第一章 穿越"
    assert "正文内容" in body

def test_parse_chapter_file(tmp_path):
    chapter_file = tmp_path / "chapter_001.md"
    chapter_file.write_text('''---
chapter: 1
title: "第一章"
word_count: 3000
---

正文''')
    
    chapter = parse_chapter_file(chapter_file)
    assert chapter.chapter_num == 1
    assert chapter.title == "第一章"
    assert chapter.word_count == 3000
```

**Step 2: Run test to verify it fails**

```bash
cd "C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code"
pytest chapter-aggregator/tests/test_markdown_parser.py -v
```

Expected: FAIL (module not found)

**Step 3: Write minimal implementation**

```python
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
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        return {}, content
    
    fm_text = match.group(1)
    body = match.group(2).strip()
    
    meta = {}
    for line in fm_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            
            # 转换类型
            if key == 'chapter':
                value = int(value)
            elif key in ('word_count',):
                value = int(value)
            
            meta[key] = value
    
    return meta, body

def parse_chapter_file(file_path: Path) -> Chapter:
    """解析单个章节文件"""
    content = file_path.read_text(encoding='utf-8')
    meta, body = parse_frontmatter(content)
    
    return Chapter(
        chapter_num=meta.get('chapter', 0),
        title=meta.get('title', ''),
        author_title=meta.get('author_title'),
        body=body,
        word_count=meta.get('word_count', 0),
        draft_time=meta.get('draft_time'),
        editor_review_time=meta.get('editor_review_time'),
        final_time=meta.get('final_time'),
        file_path=file_path
    )

def scan_chapters(project_path: Path, start: Optional[int] = None, end: Optional[int] = None, chapters: Optional[list[int]] = None) -> list[Chapter]:
    """扫描项目目录获取章节列表"""
    chapters_dir = project_path / 'chapters'
    
    if not chapters_dir.exists():
        raise FileNotFoundError(f"Chapters directory not found: {chapters_dir}")
    
    # 查找所有 md 文件
    md_files = sorted(chapters_dir.glob('*.md'))
    
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
```

**Step 4: Run test to verify it passes**

```bash
cd "C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code"
pytest chapter-aggregator/tests/test_markdown_parser.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add code/chapter-aggregator/
git commit -m "feat: add markdown_parser module"
```

---

## Task 3: Implement html_generator.py

**Files:**
- Create: `C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/html_generator.py`

**Step 1: Write the test**

```python
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
    assert "3000字" in toc

def test_generate_html():
    chapters = [
        Chapter(1, "第一章", "穿越", "正文内容", 3000, 
               "2026-03-06 08:00", "2026-03-06 09:00", "2026-03-06 10:00",
               file_path=None),
    ]
    html = generate_html(chapters, "我的小说")
    assert "第一章" in html
    assert "穿越" in html
    assert "3000" in html
    assert "sidebar" in html.lower()
```

**Step 2: Run test to verify it fails**

Expected: FAIL (module not found)

**Step 3: Write implementation**

```python
# html_generator.py
import html
from typing import List
from markdown_parser import Chapter

def generate_toc(chapters: List[Chapter]) -> str:
    """生成侧边栏目录 HTML"""
    toc_items = []
    for ch in chapters:
        author_title = ch.author_title or ch.title
        toc_items.append(f'''
        <li>
            <a href="#chapter-{ch.chapter_num}">
                <span class="chapter-num">第{ch.chapter_num}章</span>
                <span class="chapter-title">{html.escape(author_title)}</span>
                <span class="word-count">{ch.word_count}字</span>
            </a>
        </li>''')
    
    return '\n'.join(toc_items)

def generate_chapter_content(chapters: List[Chapter]) -> str:
    """生成章节内容 HTML"""
    items = []
    for ch in chapters:
        author_title = ch.author_title or ch.title
        
        # 元数据行
        meta_parts = [f"第{ch.chapter_num}章"]
        if ch.author_title:
            meta_parts.append(f"「{html.escape(ch.author_title)}」")
        meta_parts.append(f"{ch.word_count}字")
        
        meta_html = f'''
        <div class="chapter-meta">
            <span class="meta-main">{" ".join(meta_parts)}</span>
            <span class="meta-times">
                {f"初稿: {ch.draft_time}" if ch.draft_time else ""}
                {f"审核: {ch.editor_review_time}" if ch.editor_review_time else ""}
                {f"完稿: {ch.final_time}" if ch.final_time else ""}
            </span>
        </div>'''
        
        # 简单转换：换行转 <br>
        body_html = html.escape(ch.body).replace('\n\n', '</p><p>').replace('\n', '<br>')
        
        items.append(f'''
        <section id="chapter-{ch.chapter_num}" class="chapter">
            <h2 class="chapter-title">{html.escape(ch.title)}</h2>
            {meta_html}
            <div class="chapter-body">
                <p>{body_html}</p>
            </div>
        </section>''')
    
    return '\n'.join(items)

def generate_html(chapters: List[Chapter], project_title: str = "小说") -> str:
    """生成完整的 HTML 页面"""
    toc = generate_toc(chapters)
    content = generate_chapter_content(chapters)
    
    total_words = sum(ch.word_count for ch in chapters)
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(project_title)}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.8;
            color: #333;
        }}
        .container {{
            display: flex;
            min-height: 100vh;
        }}
        .sidebar {{
            width: 280px;
            background: #f5f5f5;
            border-right: 1px solid #ddd;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            padding: 20px 0;
        }}
        .sidebar h3 {{
            padding: 0 20px 15px;
            border-bottom: 1px solid #ddd;
            margin-bottom: 10px;
            font-size: 16px;
            color: #666;
        }}
        .sidebar ul {{
            list-style: none;
        }}
        .sidebar li a {{
            display: block;
            padding: 10px 20px;
            text-decoration: none;
            color: #333;
            border-left: 3px solid transparent;
            transition: all 0.2s;
        }}
        .sidebar li a:hover {{
            background: #e8e8e8;
            border-left-color: #007bff;
        }}
        .chapter-num {{
            font-size: 12px;
            color: #999;
            margin-right: 8px;
        }}
        .chapter-title {{
            font-size: 14px;
            font-weight: 500;
        }}
        .word-count {{
            font-size: 12px;
            color: #999;
            float: right;
        }}
        .main-content {{
            flex: 1;
            margin-left: 280px;
            padding: 40px 60px;
            max-width: 900px;
        }}
        .chapter {{
            margin-bottom: 60px;
            padding-bottom: 40px;
            border-bottom: 1px solid #eee;
        }}
        .chapter-title {{
            font-size: 24px;
            margin-bottom: 15px;
            color: #222;
        }}
        .chapter-meta {{
            font-size: 13px;
            color: #666;
            margin-bottom: 20px;
            padding: 10px 15px;
            background: #f9f9f9;
            border-radius: 4px;
        }}
        .meta-main {{
            font-weight: 500;
        }}
        .meta-times {{
            display: block;
            margin-top: 5px;
            font-size: 12px;
            color: #999;
        }}
        .chapter-body {{
            font-size: 16px;
            text-align: justify;
        }}
        .chapter-body p {{
            margin-bottom: 1em;
        }}
        .stats {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #fff;
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <aside class="sidebar">
            <h3>目录 ({len(chapters)}章/{total_words}字)</h3>
            <ul>
                {toc}
            </ul>
        </aside>
        <main class="main-content">
            {content}
        </main>
    </div>
    <div class="stats">
        共 {len(chapters)} 章 | {total_words} 字
    </div>
</body>
</html>'''
```

**Step 4: Run test to verify it passes**

```bash
cd "C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code"
pytest chapter-aggregator/tests/test_html_generator.py -v
```

**Step 5: Commit**

```bash
git add code/chapter-aggregator/
git commit -m "feat: add html_generator module"
```

---

## Task 4: Implement aggregator.py

**Files:**
- Create: `C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/aggregator.py`

**Step 1: Write the test**

```python
# tests/test_aggregator.py
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aggregator import generate_summary_markdown

def test_generate_summary_markdown(tmp_path):
    from markdown_parser import Chapter
    
    chapters = [
        Chapter(1, "第一章 穿越", "穿越修仙", "正文1", 3000, 
               "2026-03-06 08:00", "2026-03-06 09:00", "2026-03-06 10:00"),
        Chapter(2, "第二章 入世", "入世修炼", "正文2", 3500,
               "2026-03-06 11:00", "2026-03-06 12:00", "2026-03-06 13:00"),
    ]
    
    md = generate_summary_markdown(chapters, "我的小说")
    assert "我的小说" in md
    assert "第一章 穿越" in md
    assert "穿越修仙" in md
    assert "3000" in md
    assert "2026-03-06 10:00" in md
```

**Step 2: Run test to verify it fails**

Expected: FAIL

**Step 3: Write implementation**

```python
# aggregator.py
import html
from pathlib import Path
from typing import Optional, List
from markdown_parser import Chapter, scan_chapters

def generate_summary_markdown(chapters: List[Chapter], project_title: str = "小说") -> str:
    """生成汇总的 Markdown 文档"""
    lines = [f"# {project_title}\n"]
    lines.append(f"> 共 {len(chapters)} 章 | {sum(c.word_count for c in chapters)} 字\n")
    lines.append("---\n")
    
    for ch in chapters:
        author_title = ch.author_title or ch.title
        
        lines.append(f"## 第{ch.chapter_num}章 {ch.title}")
        if ch.author_title:
            lines.append(f"**章节名**: 「{ch.author_title}」")
        lines.append(f"- 字数: {ch.word_count}")
        if ch.draft_time:
            lines.append(f"- 初稿: {ch.draft_time}")
        if ch.editor_review_time:
            lines.append(f"- 审核: {ch.editor_review_time}")
        if ch.final_time:
            lines.append(f"- 完稿: {ch.final_time}")
        lines.append("")
        lines.append(ch.body)
        lines.append("\n---\n")
    
    return '\n'.join(lines)

def aggregate(
    project_path: str,
    output_dir: Optional[str] = None,
    start: Optional[int] = None,
    end: Optional[int] = None,
    chapters: Optional[str] = None
) -> tuple[str, str]:
    """执行汇总操作，返回 (md_path, html_path)"""
    project = Path(project_path)
    
    if not project.exists():
        raise FileNotFoundError(f"Project not found: {project_path}")
    
    # 解析章节范围
    chapter_list = None
    if chapters:
        chapter_list = [int(x.strip()) for x in chapters.split(',')]
    
    # 扫描章节
    chapter_objs = scan_chapters(project, start, end, chapter_list)
    
    if not chapter_objs:
        raise ValueError("No chapters found in specified range")
    
    # 读取项目标题
    project_title = project.name
    
    # 生成输出
    if output_dir:
        output = Path(output_dir)
    else:
        output = project / 'output'
    output.mkdir(exist_ok=True)
    
    # 生成 MD
    md_content = generate_summary_markdown(chapter_objs, project_title)
    md_path = output / 'summary.md'
    md_path.write_text(md_content, encoding='utf-8')
    
    # 生成 HTML
    from html_generator import generate_html
    html_content = generate_html(chapter_objs, project_title)
    html_path = output / 'summary.html'
    html_path.write_text(html_content, encoding='utf-8')
    
    return str(md_path), str(html_path)
```

**Step 4: Run test to verify it passes**

```bash
cd "C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code"
pytest chapter-aggregator/tests/test_aggregator.py -v
```

**Step 5: Commit**

```bash
git add code/chapter-aggregator/
git commit -m "feat: add aggregator module"
```

---

## Task 5: Implement cli.py

**Files:**
- Create: `C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/cli.py`

**Step 1: Write implementation**

```python
#!/usr/bin/env python3
# cli.py
import argparse
import sys
from pathlib import Path

def interactive_mode():
    """交互模式"""
    print("=" * 50)
    print("章节汇总工具 - 交互模式")
    print("=" * 50)
    
    # 输入项目路径
    project_path = input("请输入项目路径: ").strip()
    if not project_path:
        print("错误: 项目路径不能为空")
        return
    
    if not Path(project_path).exists():
        print(f"错误: 路径不存在: {project_path}")
        return
    
    # 输入起始章节
    start_input = input("请输入起始章节 (直接回车表示第1章): ").strip()
    start = int(start_input) if start_input else None
    
    # 输入结束章节
    end_input = input("请输入结束章节 (直接回车表示最后章): ").strip()
    end = int(end_input) if end_input else None
    
    # 执行汇总
    try:
        from aggregator import aggregate
        md_path, html_path = aggregate(project_path, start=start, end=end)
        print(f"\n汇总完成!")
        print(f"  MD文件: {md_path}")
        print(f"  HTML文件: {html_path}")
    except Exception as e:
        print(f"错误: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="网文章节汇总工具 - 将章节汇总为 MD 和 HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python cli.py /path/to/project
  python cli.py /path/to/project --start 5 --end 10
  python cli.py /path/to/project --chapter 5
  python cli.py /path/to/project --chapter 5,7,9
  python cli.py /path/to/project --output ./preview/
  python cli.py  # 交互模式
        '''
    )
    
    parser.add_argument('project', nargs='?', help='项目路径')
    parser.add_argument('--start', type=int, help='起始章节')
    parser.add_argument('--end', type=int, help='结束章节')
    parser.add_argument('--chapter', type=str, help='指定章节(逗号分隔,如 5,7,9)')
    parser.add_argument('--output', '-o', help='输出目录')
    
    args = parser.parse_args()
    
    # 无参数时进入交互模式
    if not args.project:
        interactive_mode()
        return
    
    # 验证项目路径
    if not Path(args.project).exists():
        print(f"错误: 路径不存在: {args.project}")
        sys.exit(1)
    
    try:
        from aggregator import aggregate
        md_path, html_path = aggregate(
            args.project,
            output_dir=args.output,
            start=args.start,
            end=args.end,
            chapters=args.chapter
        )
        
        print(f"汇总完成!")
        print(f"  MD文件: {md_path}")
        print(f"  HTML文件: {html_path}")
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**Step 2: Test manually**

```bash
cd "C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code"
python chapter-aggregator/cli.py --help
```

Expected: 显示帮助信息

**Step 3: Commit**

```bash
git add code/chapter-aggregator/
git commit -m "feat: add CLI interface"
```

---

## Task 6: Add README and Final Commit

**Files:**
- Create: `C:/Users/Admin/.config/opencode/skills/web-novel-editorial/code/chapter-aggregator/README.md`

**Step 1: Create README**

```markdown
# Chapter Aggregator

网文章节汇总工具 - 将章节汇总为 MD 和 HTML

## 功能

- 扫描项目 chapters 目录
- 支持指定章节范围 `--start 5 --end 10`
- 支持指定单章或多章 `--chapter 5` 或 `--chapter 5,7,9`
- 生成汇总 MD 文件
- 生成带侧边栏导航的 HTML 文件

## 使用方法

```bash
# 汇总全部章节
python cli.py /path/to/project

# 汇总第5-10章
python cli.py /path/to/project --start 5 --end 10

# 汇总单章
python cli.py /path/to/project --chapter 5

# 汇总指定多章
python cli.py /path/to/project --chapter 5,7,9

# 指定输出目录
python cli.py /path/to/project --output ./preview/

# 交互模式
python cli.py
```

## 输出

- `output/summary.md` - 汇总的 Markdown 文件
- `output/summary.html` - 带导航的 HTML 文件

## 依赖

- Python 3.8+
- 无需额外依赖（仅使用标准库）
```

**Step 2: Commit**

```bash
git add code/chapter-aggregator/
git commit -m "feat: add chapter-aggregator tool"
```
