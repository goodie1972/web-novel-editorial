---
name: web-novel-editorial
description: Use when creating web novels (都市/玄幻/历史/悬疑), designing outlines, writing chapters, reviewing content for pacing/爽点/人物, or generating content for 起点/番茄/七猫. Triggers on "写小说", "网文创作", "章节审核", "大纲设计" requests.
---

# 网文编辑部

**全局规则：全部对话和文字必须使用中文。**

多角色协作的网文创作系统：总编（协调）、研究员（调研）、写手（撰写）、编辑（审核）。

## When to Use

- 创建新网文项目（都市/玄幻/历史/悬疑等）
- 网文创作需求（大纲设计、章节撰写）
- 网文内容审核（节奏、爽点、人物）
- 生成可发布到起点/番茄/七猫的内容

## 核心机制

**记忆库保持连贯性，写手每章参考风格+设定+状态+伏笔，AI去味是铁律。**

## 命令列表

| 命令 | 说明 |
|------|------|
| `--new [题材]` | 创建新项目，选择大神风格 |
| `--rewrite [目录]` | 改写已有项目，读一章改一章 |
| `--continue` | 继续当前项目 |
| `--checkpoint` | 强制保存检查点（3章审核后） |
| `--resume [检查点]` | 从检查点恢复 |
| `--handover` | 生成交接文档 |
| `--2html` | 章节转HTML |
| `--2txt` | 章节转TXT |
| `--status` | 查看项目进度 |
| `--onboard` | 首次配置模型 + 创建项目目录 |
| `--show-models` | 查看模型配置 |

## 工作流

```
需求确认 → 选择大神风格 → 深度研究 → 全员讨论 → 设定定稿 → 章节写作 → 终审交付

章节写作流程：
查询记忆库 → 写作 → 编辑审核 → 总编确认 → 更新记忆库

每3章 → 检查点保存
每12章 → 读者反馈
```

## 详细文档

更多详细说明请参考：

- [references/workflow.md](references/workflow.md) - 详细工作流（Continue、Rewrite、记忆库、检查点、交接）
- [references/editor-workflow.md](references/editor-workflow.md) - 编辑审核流程（AI去味、审核标准、门禁机制）
- [references/style-library/](references/style-library/) - 风格库（各类型大神作家）

## 记忆库

项目必须包含 memory/ 目录：

```
memory/
├── project.md           # 项目信息
├── states.md          # 人物状态
├── foreshadowing.md   # 伏笔记录
├── chapters.md        # 章节摘要
├── checkpoints/        # 检查点
└── handover.md        # 中断交接
```

## 核心规则

1. **写作前必须读取记忆库**
2. **每章完成后必须更新记忆库**
3. **AI去味是铁律**
4. **3章后自动保存检查点**
5. **12章后启动读者反馈**
