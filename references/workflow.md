# 工作流详细说明

本文档包含 web-novel-editorial 的详细工作流程。

---

## Continue 流程（继续当前项目）

### 触发场景

- 项目之前有写作过，需要继续写作
- 会话中断后恢复

### 执行步骤

**步骤1：检查中断记录（必须⭐）**

```
检查项目目录是否存在：
├── memory/handover.md          # 有交接文档？
├── memory/checkpoints/        # 有检查点？
│   └── checkpoint-*.yaml
```

**步骤2：根据检查结果处理**

| 情况 | 处理方式 |
|------|----------|
| 有 handover.md | 读取 handover → 读取最新 checkpoint → 加载记忆库 → 从中断位置继续 |
| 无 handover 但有 checkpoint | 读取最新 checkpoint → 加载记忆库 → 从章节+1继续 |
| 无 handover 无 checkpoint | 读取 memory/* 记忆库文件 → 继续写作 |

**步骤3：继续写作**

```
加载状态 → 写作下一章 → 编辑审核 → 总编确认 → 更新记忆库
```

### 继续前检查清单

- [ ] 已读取 handover.md（如有）
- [ ] 已读取最新 checkpoint（如有）
- [ ] 已加载 memory/states.md 人物状态
- [ ] 已加载 memory/foreshadowing.md 伏笔状态
- [ ] 已加载 memory/chapters.md 章节摘要
- [ ] 已确认当前章节号

---

## Rewrite 流程（改写已有项目）

### 触发场景

- 老项目需要按新要求改写
- 写了一半需要调整方向
- 更换大神风格重写
- 补完未完成的章节

### 与 --new 的区别

| 维度 | --new | --rewrite |
|------|-------|-----------|
| 起点 | 空白 | 已有项目 |
| 设定 | 从零创建 | 读取已有，讨论修改 |
| 风格 | 选择大神 | 可保持或更换 |
| 章节 | 全新创作 | 读一章改一章 |
| 记忆库 | 新建 | 读取已有，更新修改 |

### Rewrite 执行步骤

**步骤1：检查中断记录（必须⭐）**

```
检查项目目录是否存在：
├── memory/handover.md          # 有交接文档？
├── memory/checkpoints/        # 有检查点？
│   └── checkpoint-*.yaml
```

**步骤2：读取已有项目**

```
读取以下文件：
├── 大纲.md                     # 已有大纲
├── 人设.md                     # 已有设定
├── 世界.md                     # 世界观
├── 章节/                       # 已有的章节
│   ├── chapter-001.md
│   └── ...
└── memory/                    # 记忆库
    ├── project.md
    ├── states.md
    └── chapters.md
```

**步骤3：与用户确认改写方向**

| 问题 | 选项 |
|------|------|
| 改写范围 | 全部 / 部分章节 / 从某章开始 |
| 风格调整 | 保持原风格 / 更换大神风格 |
| 剧情调整 | 保持不变 / 小幅调整 / 大幅调整 |

**步骤4：更新记忆库**

根据改写方向，更新 memory/ 目录下的文件。

---

## 记忆库系统（核心⭐）

### 记忆库文件结构

```
项目目录/
├── docs/
│   └── webnovel/
│       └── {项目名}/
│           ├── 大纲.md
│           ├── 人设.md
│           ├── 世界.md
│           └── 章节/
│               └── chapter-XXX.md
└── memory/
    ├── project.md           # 项目信息（题材、大神、目标平台）
    ├── states.md            # 人物状态
    ├── foreshadowing.md    # 伏笔记录
    ├── chapters.md          # 章节摘要
    ├── checkpoints/         # 检查点
    │   └── checkpoint-*.yaml
    └── handover.md          # 中断交接
```

### 核心规则

**必须遵守**：
1. 每章完成后必须更新 chapters.md
2. 每次状态变化必须更新 states.md
3. 每次伏笔变化必须更新 foreshadowing.md
4. 写手写作前必须读取以上文件

### 文件模板

#### project.md

```markdown
# 项目信息

- 题材：[类型]
- 大神风格：[作家名]
- 目标平台：[起点/番茄/七猫]
- 创建时间：[日期]
- 当前章节：[X]
```

#### states.md

```markdown
# 人物状态

## 主角
- 等级/境界：[]
- 实力变化：[]
- 当前位置：[]
- 关键物品：[]

## 主要配角
- 角色1：[状态]
- 角色2：[状态]
```

#### foreshadowing.md

```markdown
# 伏笔记录

## 待回收伏笔
| 伏笔内容 | 埋入章节 | 计划回收 |
|----------|----------|----------|
|          |          |          |

## 已回收伏笔
| 伏笔内容 | 埋入章节 | 回收章节 |
|----------|----------|----------|
|          |          |          |
```

---

## 字数管控机制（严格⭐⭐⭐）

### 核心原则

**严禁虚报字数！所有字数必须由系统自动计算，写手无法干预。**

### 1. 章节元数据定义

每个章节文件头部必须包含预期字数：

```yaml
---
chapter: X
title: 章节标题
expected_word_count: 3000  # 预期字数（必须）
---
```

### 2. 字数计算规则

| 类型 | 计算方式 | 说明 |
|------|----------|------|
| 汉字 | 实际字符数 | 每个汉字算1字 |
| 标点 | 实际字符数 | 英文标点也算 |
| 英文单词 | 实际字符数 | 每个单词算1字 |
| 空格 | 不计入 | 跳过 |

**注意**：Markdown格式标记（如 `**`、`##`）不计入正文字数。

### 3. 字数获取命令

使用以下命令获取真实字数：

```bash
# 方式1：使用内置命令
--wordcount 章节/chaapter-001.md

# 方式2：手动计算
# 在项目中运行字数统计脚本
```

### 4. 章节撰写流程

**步骤1：创建章节时设定预期字数**

```
根据大纲设计，为本章设定预期字数：
- 铺垫章：2500-3000字
- 发展章：3000-3500字
- 高潮章：3500-4500字
- 过渡章：2000-2500字
```

**步骤2：写入章节元数据**

在章节文件头部写入预期字数：

```yaml
---
chapter: 1
title: 第一章 下山
expected_word_count: 3500
---
```

**步骤3：写作时严格控制**

写作过程中注意：
- 不要故意凑字数（水字数会被编辑发现）
- 不要偷工减料（字数不足无法通过审核）
- 专注内容质量

### 5. 审核时字数检查（必须⭐⭐⭐）

**编辑审核时必须执行：**

| 检查项 | 要求 |
|--------|------|
| 实际字数 | >= 预期字数 |
| 水分检测 | 无明显凑字数段落 |
| 质量 | 达标后只看质量 |

**字数检查流程：**

```
1. 读取章节文件
2. 提取 expected_word_count 字段
3. 计算实际字数（排除Markdown格式）
4. 比较：
   - 如果 实际字数 >= 预期字数 → 通过字数检查
   - 如果 实际字数 < 预期字数 → 拒绝 ✗
```

**示例：**

```
章节：chapter-001.md
预期字数：3500
实际字数：3234

结果：字数不足！需要补充266字
```

### 6. 字数不足的处理

| 情况 | 处理方式 |
|------|----------|
| 差200字以内 | 补充内容，通过审核 |
| 差200-500字 | 严重警告，返回修改 |
| 差500字以上 | 拒绝，写手重写 |

### 7. 字数统计脚本

创建一个字数统计脚本 `scripts/wordcount.py`：

```python
import sys
import re

def count_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 去除Markdown格式
    content = re.sub(r'```[\s\S]*?```', '', content)  # 代码块
    content = re.sub(r'#+\s+', '', content)  # 标题标记
    content = re.sub(r'\*\*|\*|_', '', content)  # 加粗斜体
    content = re.sub(r'\[.*?\]\(.*?\)', '', content)  # 链接
    content = re.sub(r'```', '', content)
    
    # 去除空白字符
    content = content.replace(' ', '')
    content = content.replace('\n', '')
    
    # 计算字数
    word_count = len(content)
    return wordname__ == '___count

if __main__':
    file_path = sys.argv[1]
    count = count_words(file_path)
    print(f"实际字数：{count}")
```

### 8. 禁止行为

| 禁止 | 处罚 |
|------|------|
| 虚报字数 | 严重警告 |
| 水字数 | 审核拒绝 |
| 跳过字数检查 | 门禁拦截 |
| 修改元数据虚增 | 团队除名 |

---

## 检查点系统（防中断⭐）

### 触发条件

每完成 **3章** 写作并审核通过后，自动触发检查点保存。

### 检查点内容

```yaml
checkpoint:
  timestamp: "2026-01-01 12:00:00"
  chapter: 3
  project: 项目名
  files:
    - 大纲.md
    - 人设.md
    - 世界.md
    - 章节/chapter-001.md
    - 章节/chapter-002.md
    - 章节/chapter-003.md
  memory:
    - memory/project.md
    - memory/states.md
    - memory/foreshadowing.md
    - memory/chapters.md
```

### 检查点文件位置

```
memory/checkpoints/
├── checkpoint-001.yaml    # 第1-3章
├── checkpoint-002.yaml    # 第4-6章
└── checkpoint-003.yaml    # 第7-9章
```

---

## 交接文档（中断恢复⭐）

### 触发场景

- 会话中断
- 用户离开
- 需要他人接手

### 交接文档模板

```markdown
# 中断交接

## 项目信息
- 项目名：[]
- 题材：[]
- 当前章节：[X]

## 写作进度
- 上一章：chapter-[X]
- 写作状态：[进行中/待审核/已完成]

## 待办事项
- [ ] 待完成内容

## 特殊说明
-

## 记忆库状态
- states.md：已更新/需更新
- foreshadowing.md：已更新/需更新
- chapters.md：已更新/需更新
```

---

## 写作前检查（必须全部勾选）

- [ ] 已读取大纲.md
- [ ] 已读取人设.md
- [ ] 已读取世界.md
- [ ] 已读取上一章 chapter-[X-1].md
- [ ] 已读取 memory/states.md（人物状态）
- [ ] 已读取 memory/foreshadowing.md（伏笔状态）
- [ ] 已读取 memory/chapters.md（章节摘要）
- [ ] 已读取本章细纲（plot-outline/chapter-[X].md）
- [ ] 已确认大神风格提示词

---

## 章节完成后更新（必须全部完成）

1. **更新 memory/chapters.md**
   - 添加本章摘要
   - 记录本章爽点
   - 记录伏笔埋入/回收

2. **更新 memory/states.md**
   - 人物等级/实力变化
   - 物品获取
   - 位置变化

3. **更新 memory/foreshadowing.md**
   - 新埋入的伏笔
   - 回收的伏笔

4. **更新本章节的细纲文件**
   - 记录实际写作与计划的差异
