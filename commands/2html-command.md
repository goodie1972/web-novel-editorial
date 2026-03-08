# --2html 命令

## 功能

将指定项目的章节汇总转换为 HTML 文件，方便预览。

## 使用流程

**步骤1：确认项目来源**

```
请问是当前打开的项目还是其他项目？
- 当前项目
- 其他项目（需要输入项目路径或名称）
```

**步骤2：根据选择处理**

| 情况 | 处理 |
|------|------|
| 当前项目 | 使用当前项目路径 |
| 其他项目 | 让用户输入项目名称/路径 |

**步骤3：询问章节范围**

```
请输入起始章节号：1
请输入结束章节号：3
```

（直接回车使用默认值：起始=第1章，结束=最后一章）

**步骤4：执行转换**

调用 chapter-aggregator 工具：
```bash
python chapter-aggregator/cli.py {项目路径} --start {起始} --end {结束}
```

**步骤5：输出结果**

```
✅ 转换完成！
  HTML文件：{项目路径}/output/summary.html
  预览：打开 HTML 文件即可查看
```

---

## 执行示例

```
> --2html
请问是当前打开的项目还是其他项目？(当前/其他): 当前
请输入起始章节号（直接回车表示第1章）: 1
请输入结束章节号（直接回车表示最后章）: 3
✅ 转换完成！
  HTML文件：D:\docs\webnovel\myproject\output\summary.html
```

---

## 技术实现

调用 `code/chapter-aggregator/cli.py`：

```python
import subprocess
import sys

def run_2html():
    # 步骤1：确认项目
    project_choice = input("请问是当前打开的项目还是其他项目？(当前/其他): ")
    
    if project_choice.strip() == "当前":
        # 使用当前项目路径
        project_path = get_current_project_path()
    else:
        # 让用户输入项目名称
        project_name = input("请输入项目名称: ")
        project_path = find_project_path(project_name)
    
    # 步骤2：确认章节范围
    start = input("请输入起始章节号（直接回车表示第1章）: ")
    end = input("请输入结束章节号（直接回车表示最后章）: ")
    
    start = int(start) if start else None
    end = int(end) if end else None
    
    # 步骤3：执行转换
    cmd = [
        sys.executable,
        "chapter-aggregator/cli.py",
        project_path,
    ]
    if start:
        cmd.extend(["--start", str(start)])
    if end:
        cmd.extend(["--end", str(end)])
    
    subprocess.run(cmd)
```

---

## 输出文件

转换后的文件保存在项目目录下：
```
{项目}/
└── output/
    ├── summary.md      # 汇总的 Markdown（可选）
    └── summary.html    # 带侧边栏导航的 HTML
```

---

## HTML 功能

- 侧边栏目录：显示所有章节标题、章节名、字数
- 点击跳转：点击目录项跳转到对应章节
- 元数据显示：章节名、字数、初稿时间、审核时间、完稿时间
- 统计信息：右下角显示总章节数、总字数
