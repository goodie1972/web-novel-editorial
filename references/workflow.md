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
