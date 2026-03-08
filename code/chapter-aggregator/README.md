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
