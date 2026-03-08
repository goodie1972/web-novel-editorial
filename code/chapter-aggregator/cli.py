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

    # 选择输出格式
    print("\n请选择输出格式:")
    print("  1. HTML + MD (默认)")
    print("  2. 仅 HTML")
    print("  3. 仅 MD")
    print("  4. 仅 TXT")
    format_choice = input("请选择 (1-4，直接回车默认1): ").strip()

    format_map = {
        "1": "both",
        "2": "html",
        "3": "md",
        "4": "txt",
    }
    fmt = format_map.get(format_choice, "both")

    # 输入起始章节
    start_input = input("请输入起始章节 (直接回车表示第1章): ").strip()
    start = int(start_input) if start_input else None

    # 输入结束章节
    end_input = input("请输入结束章节 (直接回车表示最后章): ").strip()
    end = int(end_input) if end_input else None

    # 执行汇总
    try:
        from aggregator import aggregate

        result = aggregate(project_path, start=start, end=end, format=fmt)

        if fmt == "txt":
            txt_path = result[0]
            print(f"\n汇总完成!")
            print(f"  TXT文件: {txt_path}")
        elif fmt == "md":
            md_path = result[0]
            print(f"\n汇总完成!")
            print(f"  MD文件: {md_path}")
        elif fmt == "html":
            html_path = result[1]
            print(f"\n汇总完成!")
            print(f"  HTML文件: {html_path}")
        else:
            md_path, html_path = result
            print(f"\n汇总完成!")
            print(f"  MD文件: {md_path}")
            print(f"  HTML文件: {html_path}")
    except Exception as e:
        print(f"错误: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="网文章节汇总工具 - 将章节汇总为 MD/HTML/TXT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互模式
  python cli.py

  # HTML + MD (默认)
  python cli.py /path/to/project --start 1 --end 10

  # 仅 HTML
  python cli.py /path/to/project --start 1 --end 10 --format html

  # 仅 MD
  python cli.py /path/to/project --start 1 --end 10 --format md

  # 仅 TXT
  python cli.py /path/to/project --start 1 --end 10 --format txt
  python cli.py /path/to/project --start 1 --end 10 --txt

  # 指定单章/多章
  python cli.py /path/to/project --chapter 5
  python cli.py /path/to/project --chapter 5,7,9

  # 指定输出目录
  python cli.py /path/to/project --start 1 --end 10 --output ./preview/
        """,
    )

    parser.add_argument("project", nargs="?", help="项目路径")
    parser.add_argument("--start", type=int, help="起始章节")
    parser.add_argument("--end", type=int, help="结束章节")
    parser.add_argument("--chapter", type=str, help="指定章节(逗号分隔,如 5,7,9)")
    parser.add_argument("--output", "-o", help="输出目录")
    parser.add_argument(
        "--format",
        "-f",
        choices=["both", "html", "md", "txt"],
        default="both",
        help="输出格式: both(html+md), html, md, txt (默认: both)",
    )
    parser.add_argument(
        "--txt",
        action="store_true",
        dest="to_txt",
        help="输出纯文本TXT格式 (等同于 --format txt)",
    )

    args = parser.parse_args()

    # 处理 --txt 快捷方式
    if args.to_txt:
        args.format = "txt"

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

        result = aggregate(
            args.project,
            output_dir=args.output,
            start=args.start,
            end=args.end,
            chapters=args.chapter,
            format=args.format,
        )

        if args.format == "txt":
            txt_path = result[0]
            print(f"汇总完成!")
            print(f"  TXT文件: {txt_path}")
        elif args.format == "md":
            md_path = result[0]
            print(f"汇总完成!")
            print(f"  MD文件: {md_path}")
        elif args.format == "html":
            html_path = result[1]
            print(f"汇总完成!")
            print(f"  HTML文件: {html_path}")
        else:
            md_path, html_path = result
            print(f"汇总完成!")
            print(f"  MD文件: {md_path}")
            print(f"  HTML文件: {html_path}")

    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
