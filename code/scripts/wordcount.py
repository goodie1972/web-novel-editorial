#!/usr/bin/env python3
"""
字数统计脚本
计算章节文件的实际字数（排除Markdown格式）
"""

import sys
import re
import yaml
import os


def extract_frontmatter(content):
    """提取并解析YAML前置元数据"""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2]
            try:
                meta = yaml.safe_load(frontmatter)
                return meta, body
            except:
                return {}, content
    return {}, content


def count_words(content):
    """计算实际字数（排除Markdown格式）"""
    # 去除代码块
    content = re.sub(r"```[\s\S]*?```", "", content)
    content = re.sub(r"```", "", content)

    # 去除标题标记
    content = re.sub(r"^#+\s+", "", content, flags=re.MULTILINE)

    # 去除加粗斜体标记
    content = re.sub(r"\*\*|\*", "", content)
    content = re.sub(r"_{2,}", "", content)

    # 去除链接
    content = re.sub(r"\[.*?\]\(.*?\)", "", content)

    # 去除图片
    content = re.sub(r"!\[.*?\]\(.*?\)", "", content)

    # 去除HTML标签
    content = re.sub(r"<[^>]+>", "", content)

    # 去除水平线
    content = re.sub(r"^---+$", "", content, flags=re.MULTILINE)

    # 去除列表标记
    content = re.sub(r"^[\s]*[-*+]\s+", "", content, flags=re.MULTILINE)
    content = re.sub(r"^[\s]*\d+\.\s+", "", content, flags=re.MULTILINE)

    # 去除多余空白
    content = re.sub(r"\n{3,}", "\n\n", content)

    # 去除空格（中文不需要空格分隔）
    content = content.replace(" ", "")

    # 计算字数
    word_count = len(content)
    return word_count


def check_wordcount(file_path):
    """检查章节字数"""
    if not os.path.exists(file_path):
        print(f"错误：文件不存在 - {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取元数据
    meta, body = extract_frontmatter(content)

    # 计算实际字数
    actual_count = count_words(body)

    # 获取预期字数
    expected_count = meta.get("expected_word_count", 0)

    print(f"=" * 40)
    print(f"章节文件：{os.path.basename(file_path)}")
    print(f"=" * 40)
    print(f"预期字数：{expected_count}")
    print(f"实际字数：{actual_count}")
    print(f"=" * 40)

    if expected_count > 0:
        diff = actual_count - expected_count
        if diff >= 0:
            print(f"✅ 通过！超出 {diff} 字")
            return True
        else:
            print(f"❌ 字数不足！还差 {abs(diff)} 字")
            return False
    else:
        print(f"⚠️ 未设定预期字数")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python wordcount.py <章节文件路径>")
        sys.exit(1)

    file_path = sys.argv[1]
    check_wordcount(file_path)
