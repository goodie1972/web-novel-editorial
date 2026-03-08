# 交接文档 - {项目名称}

> 生成时间：{timestamp}
> 当前章节：第 {chapter} 章

---

## 基本信息

| 项目 | 内容 |
|------|------|
| 项目名称 | {project} |
| 题材 | {genre} |
| 大神风格 | {author_style} |
| 项目路径 | {project_path} |
| 当前章节 | 第 {chapter} 章 |

---

## 人物状态（当前）

### 主角
- 境界：{level}
- 位置：{location}
- 物品：{inventory}
- 状态：{status}

### 其他人物
{personnel_status}

---

## 活跃伏笔

| ID | 伏笔名称 | 状态 | 埋入章节 | 预期回收 |
|----|----------|------|----------|----------|
| fp-001 | 神秘玉佩 | 已埋入 | 第3章 | 第15章 |
| fp-002 | 身世之谜 | 已埋入 | 第2章 | 第30章 |

{foreshadowing_table}

---

## 写作进度

- **已完成**：第1-{completed}章
- **待完成**：从第{next}章开始

---

## 本章写作中

> 如果中断时正在写某一章，填写以下内容

- 当前正在写：第 {current} 章
- 本章标题：{chapter_title}
- 本章细纲：
  - 事件1
  - 事件2
  - 事件3
- 已完成部分：{completed_part}
- 待完成部分：{pending_part}

---

## 特殊注意事项

### 战力体系
- {combat_notes}

### 伏笔进度
- {foreshadowing_notes}

### 高潮安排
- {climax_notes}

### 其他
- {other_notes}

---

## 恢复指引

1. 读取本交接文档
2. 读取最近检查点 `memory/checkpoints/checkpoint-{chapter}.yaml`
3. 加载人物状态到 `memory/states.md`
4. 加载伏笔状态到 `memory/foreshadowing.md`
5. 从第 {next} 章继续写作

---

## 联系方式（如需人工协助）

{contact_info}
