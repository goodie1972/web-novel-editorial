# 检查点与交接命令

## continue 命令

### 功能
继续当前项目的写作，自动检查中断记录。

### 执行流程

**步骤1：检查中断记录**

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

**步骤3：继续前检查清单**

- [ ] 已读取 handover.md（如有）
- [ ] 已读取最新 checkpoint（如有）
- [ ] 已加载 memory/states.md 人物状态
- [ ] 已加载 memory/foreshadowing.md 伏笔状态
- [ ] 已加载 memory/chapters.md 章节摘要
- [ ] 已确认当前章节号

---

## checkpoint 命令

### 功能
保存当前项目状态到检查点文件，用于意外中断恢复。

### 前提条件
3章审核全部通过（总编统一审核）

### 触发时机
- 自动：每完成 3 章（审核通过后）
- 手动：`--checkpoint`

### 执行流程

**步骤1：确认审核通过**

总编确认3章全部通过后才能执行 checkpoint

**步骤2：收集检查点数据**

```
读取 memory/states.yaml → 人物状态快照
读取 memory/foreshadowing.yaml → 活跃伏笔
读取 memory/chapters.yaml → 最近3章摘要
读取大纲进度 → 当前写作进度
```

**步骤3：保存检查点文件**

```
memory/checkpoints/checkpoint-{章节号}.yaml
```

### 保存内容
- 当前章节号
- 3章审核状态（每章的draft_time, editor_review_time, final_time, word_count, author_title）
- 3章统一审核状态
- 人物状态快照
- 活跃伏笔列表
- 最近3章摘要
- 大纲进度

---

## resume 命令

### 功能
从指定检查点恢复项目状态，继续写作。

### 用法
```
--resume checkpoint-003
```

### 恢复流程
1. 读取检查点文件 `memory/checkpoints/checkpoint-003.yaml`
2. 加载人物状态到 memory/states.md
3. 加载伏笔状态到 memory/foreshadowing.md
4. 加载章节摘要到 memory/chapters.md
5. 确认当前是第4章（章节号+1）
6. 从第4章开始继续写作

---

## handover 命令

### 功能
生成交接文档，用于人工接手或意外中断恢复。

### 触发时机
- 长时间暂停前
- 会话可能中断前
- 用户要求人工接手时

### 输出
`memory/handover.md`

### 内容结构
- 基本信息（章节、风格、路径）
- 人物当前状态
- 活跃伏笔列表
- 写作进度（已完成/待完成）
- 本章写作中状态（如果中断时正在写）
- 3章审核状态（如有）

---

## 使用场景

| 场景 | 命令 |
|------|------|
| 继续之前中断的项目 | --continue |
| 每3章自动保存 | 自动触发 checkpoint（审核通过后） |
| 长时间写作前手动保存 | --checkpoint |
| 从指定检查点恢复 | --resume checkpoint-003 |
| 人工接手项目 | --handover |
| 查看有哪些检查点 | --status |

---

## 恢复时的上下文清理

恢复后，建议清理上下文：
1. 不再传递历史章节全文
2. 只传递最近 3 章摘要
3. 人物状态从检查点加载
4. 伏笔状态从检查点加载
