# aggregator.py
from pathlib import Path
from typing import Optional, List
from markdown_parser import Chapter, scan_chapters


def generate_summary_markdown(
    chapters: List[Chapter], project_title: str = "小说"
) -> str:
    """生成汇总的 Markdown 文档"""
    lines = [f"# {project_title}\n"]
    lines.append(
        f"> 共 {len(chapters)} 章 | {sum(c.word_count for c in chapters)} 字\n"
    )
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

    return "\n".join(lines)


def generate_txt(chapters: List[Chapter], project_title: str = "小说") -> str:
    """生成纯文本 TXT 文档"""
    lines = []
    lines.append(project_title)
    lines.append("=" * 50)
    lines.append(f"共 {len(chapters)} 章 | {sum(c.word_count for c in chapters)} 字")
    lines.append("=" * 50)
    lines.append("")

    for ch in chapters:
        author_title = ch.author_title or ch.title
        lines.append(f"第{ch.chapter_num}章 {ch.title}")
        if ch.author_title:
            lines.append(f"「{ch.author_title}」")
        lines.append("-" * 30)
        lines.append(ch.body)
        lines.append("")
        lines.append("")

    return "\n".join(lines)


def aggregate(
    project_path: str,
    output_dir: Optional[str] = None,
    start: Optional[int] = None,
    end: Optional[int] = None,
    chapters: Optional[str] = None,
    format: str = "both",
) -> tuple[str, str]:
    """执行汇总操作，返回 (md_path, html_path) 或 (txt_path, md_path)"""
    project = Path(project_path)

    if not project.exists():
        raise FileNotFoundError(f"Project not found: {project_path}")

    # 解析章节范围
    chapter_list = None
    if chapters:
        chapter_list = [int(x.strip()) for x in chapters.split(",")]

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
        output = project / "output"
    output.mkdir(exist_ok=True)

    if format == "txt":
        # 只生成 TXT
        txt_content = generate_txt(chapter_objs, project_title)
        txt_path = output / "summary.txt"
        txt_path.write_text(txt_content, encoding="utf-8")
        return str(txt_path), ""

    # 生成 MD
    md_content = generate_summary_markdown(chapter_objs, project_title)
    md_path = output / "summary.md"
    md_path.write_text(md_content, encoding="utf-8")

    if format == "md":
        return str(md_path), ""

    # 生成 HTML (默认)
    from html_generator import generate_html

    html_content = generate_html(chapter_objs, project_title)
    html_path = output / "summary.html"
    html_path.write_text(html_content, encoding="utf-8")

    return str(md_path), str(html_path)
