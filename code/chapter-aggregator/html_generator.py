# html_generator.py
import html as html_escape
from typing import List
from markdown_parser import Chapter


def generate_toc(chapters: List[Chapter]) -> str:
    """生成侧边栏目录 HTML"""
    toc_items = []
    for ch in chapters:
        author_title = ch.author_title or ch.title
        toc_items.append(f"""
        <li>
            <a href="#chapter-{ch.chapter_num}">
                <span class="chapter-num">第{ch.chapter_num}章</span>
                <span class="chapter-title">{html_escape.escape(author_title)}</span>
                <span class="word-count">{ch.word_count}字</span>
            </a>
        </li>""")

    return "\n".join(toc_items)


def generate_chapter_content(chapters: List[Chapter]) -> str:
    """生成章节内容 HTML"""
    items = []
    for ch in chapters:
        author_title = ch.author_title or ch.title

        # 元数据行
        meta_parts = [f"第{ch.chapter_num}章"]
        if ch.author_title:
            meta_parts.append(f"「{html_escape.escape(ch.author_title)}」")
        meta_parts.append(f"{ch.word_count}字")

        meta_html = f"""
        <div class="chapter-meta">
            <span class="meta-main">{" ".join(meta_parts)}</span>
            <span class="meta-times">
                {f"初稿: {ch.draft_time}" if ch.draft_time else ""}
                {f"审核: {ch.editor_review_time}" if ch.editor_review_time else ""}
                {f"完稿: {ch.final_time}" if ch.final_time else ""}
            </span>
        </div>"""

        # 简单转换：换行转 <br>
        body_html = (
            html_escape.escape(ch.body).replace("\n\n", "</p><p>").replace("\n", "<br>")
        )

        items.append(f"""
        <section id="chapter-{ch.chapter_num}" class="chapter">
            <h2 class="chapter-title">{html_escape.escape(ch.title)}</h2>
            {meta_html}
            <div class="chapter-body">
                <p>{body_html}</p>
            </div>
        </section>""")

    return "\n".join(items)


def generate_html(chapters: List[Chapter], project_title: str = "小说") -> str:
    """生成完整的 HTML 页面"""
    toc = generate_toc(chapters)
    content = generate_chapter_content(chapters)

    total_words = sum(ch.word_count for ch in chapters)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_escape.escape(project_title)}</title>
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
        .chapter-title-main {{
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
</html>"""
