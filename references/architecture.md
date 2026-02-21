# 系统架构与特色功能

## 文件结构详解

```
skills/web-novel-editorial/
├── SKILL.md                    # 入口文件
├── CLAUDE.md                   # 总编配置（核心工作流）
├── SOUL.md                     # 团队文化
├── USER.md                     # 主编画像
├── CONVENTIONS.md              # 项目规范
├── settings.json               # Agent Teams 配置
├── skills/                     # 角色技能包
│   ├── researcher-skill/       # 研究员
│   ├── writer-skill/           # 写手
│   └── editor-skill/           # 编辑
├── templates/                  # 输出模板
├── references/                 # 参考文档
├── monitoring/                 # LLM 监控
└── state/                      # 状态持久化
```

---

## 特色功能

### 1. 角色模型绑定

不同角色可使用不同模型，在 `settings.json` 中配置：

| 角色 | 推荐模型 | 理由 |
|------|----------|------|
| 总编 | Claude Opus / GPT-5.2 | 最强推理 |
| 研究员 | GPT-5.2 / GLM-4.7 | 调研能力 |
| 写手 | Kimi K2.5 | 长文本写作 |
| 编辑 | GLM-4.7 | 审核精度 |

详见 [model-config.md](model-config.md)

### 2. 自动学习升级

- 项目完成后自动复盘
- 识别反复出现的问题
- 提取成功经验沉淀到 references/

详见 [learning-system.md](learning-system.md)

### 3. 创意建议输出

研究员产出包括：
- 书名建议（多选项）
- 核心卖点设计
- 人设详细建议
- 爽点布局规划

详见 [creative-suggestions.md](creative-suggestions.md)

### 4. LLM 使用监控

- Token 用量统计
- 成本计算与预警
- 异常监控

详见 [../monitoring/monitor.md](../monitoring/monitor.md)

### 5. 流程状态持久化

- 检查点机制
- 决策记录
- 快速恢复

详见 [../state/state-manager.md](../state/state-manager.md)

### 6. Chroma 向量数据库

- 设定/人物/章节向量化
- 语义检索
- 一致性保障

详见 [chroma-integration.md](chroma-integration.md)

---

## 配置说明

### settings.json 结构

```json
{
  "enableAgentTeams": true,
  "teammateMode": "manual",
  "strictMode": true,
  "modelConfig": { ... },
  "teammates": [ ... ],
  "qualityGates": { ... },
  "longMemory": { ... },
  "readerFeedback": { ... }
}
```

### 质量门配置

| 阶段 | 审批人 | 必需产出 |
|------|--------|----------|
| 需求确认 | 总编 | requirements.md |
| 研究审批 | 总编 | research-brief + creative-suggestions |
| 全员讨论 | 全员 | discussion-XX.md |
| 设定定稿 | 总编+用户 | outline + world + characters + skills |
| 章节审核 | 编辑+总编 | 每5章审核 + 双重确认 |
| 终审交付 | 总编+用户 | 全文审核 |

---

## 修改记录

| 日期 | 修改人 | 修改内容 |
|------|--------|----------|
| 2026-02-18 | 总编 | 从 SKILL.md 提取架构文档 |
