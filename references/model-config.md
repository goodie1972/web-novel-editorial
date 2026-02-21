# 模型提供商配置指南

本文档说明如何配置不同的模型提供商。

---

## 当前配置的提供商 (WolfAI)

基于 `C:\Users\Bobo\.config\oh-my-opencode.json` 配置：

| 角色 | 模型 | 说明 |
|------|------|------|
| 总编 | wolfai/gpt-5.2 | 最强推理，复杂决策 |
| 研究员 | wolfai/glm-4.7 | 性价比高，调研能力 |
| 写手 | wolfai/kimi-k2.5 | 长文本，网文撰写 |
| 编辑 | wolfai/glm-4.7 | 精准审核 |

---

## WolfAI 可用模型

```
wolfai/gpt-5.2              - GPT-5.2 最强
wolfai/gpt-5.3-codex       - GPT-5.3 Codex
wolfai/claude-opus-4-5-thinking - Claude Opus
wolfai/claude-sonnet-4-5   - Claude Sonnet
wolfai/glm-4.7             - GLM-4.7 性价比
wolfai/glm-5               - GLM-5
wolfai/minimax-m2.5        - Minimax M2.5
wolfai/kimi-k2.5           - Kimi K2.5 长文本
wolfai/qwen3-next-80b-a3b-instruct - Qwen3
wolfai/gemini-3-pro        - Gemini 3 Pro
wolfai/grok-code-fast-1    - Grok 快速
```

---

## 如何切换模型

### 直接修改 settings.json

在 `teammates` 中修改对应角色的模型：

```json
{
  "teammates": [
    { "name": "总编", "model": "wolfai/gpt-5.2" },
    { "name": "研究员", "model": "wolfai/glm-4.7" },
    { "name": "写手", "model": "wolfai/kimi-k2.5" },
    { "name": "编辑", "model": "wolfai/glm-4.7" }
  ]
}
```

---

## 推荐配置

### 性价比之选

```json
{
  "teammates": [
    { "name": "总编", "model": "wolfai/glm-4.7" },
    { "name": "研究员", "model": "wolfai/glm-4.7" },
    { "name": "写手", "model": "wolfai/kimi-k2.5" },
    { "name": "编辑", "model": "wolfai/glm-4.7" }
  ]
}
```

### 最强性能

```json
{
  "teammates": [
    { "name": "总编", "model": "wolfai/gpt-5.2" },
    { "name": "研究员", "model": "wolfai/gpt-5.2" },
    { "name": "写手", "model": "wolfai/gpt-5.3-codex" },
    { "name": "编辑", "model": "wolfai/gpt-5.2" }
  ]
}
```

### 长篇网文

```json
{
  "teammates": [
    { "name": "总编", "model": "wolfai/kimi-k2.5" },
    { "name": "研究员", "model": "wolfai/glm-4.7" },
    { "name": "写手", "model": "wolfai/kimi-k2.5" },
    { "name": "编辑", "model": "wolfai/kimi-k2.5" }
  ]
}
```

---

## 角色模型选择

| 角色 | 优先级 | 推荐模型 |
|------|--------|----------|
| 总编 | 推理能力 | gpt-5.2 |
| 写手 | 长文本+创意 | kimi-k2.5 |
| 编辑 | 精准+逻辑 | glm-4.7 |
| 研究员 | 广度+性价比 | glm-4.7 |
