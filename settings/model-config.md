# Agent团队模型配置

本文档记录团队各成员角色所使用的大模型配置。

---

## 配置流程

### 首次配置（在新机器上首次使用）

**当 skill 启动时，需要检查配置：**

1. **检查 settings.json** 中的 `modelConfig.roles` 是否已配置
2. **检查 model-config.md** 中的角色模型分配是否完成
3. **如果未配置**：
   - 读取 `C:\Users\Bobo\.config\opencode\opencode.json` 获取可用模型列表
   - 从 `settings.json` 的 `modelProvider.availableModels` 交叉验证
   - 用选择方式让用户为每个角色选择模型
   - 将选择结果写入 `settings.json` 的 `modelConfig.roles`
   - 将选择结果写入本文件的角色模型分配部分

---

## 角色对应

| 配置角色 | 实际角色 | 说明 |
|----------|----------|------|
| 总编 | 总编 | 协调团队、审核内容 |
| 研究员 | 调研员 | 素材调研、资料收集 |
| 写手 | 写手 | 章节撰写、内容生成 |
| 编辑 | 编辑 | 内容审核、质量把控 |

---

## 可用模型列表（从 opencode.json 读取）

从 `C:\Users\Bobo\.config\opencode\opencode.json` 的 `provider.wolfai.models` 读取：

| 模型ID | 显示名称 |
|--------|----------|
| gpt-5.2-codex | GPT-5.2-Codex |
| gpt-5.2-codex-high | GPT-5.2-High |
| gpt-5.2 | GPT-5.2 |
| gpt-5.3-codex | GPT-5.3-Codex |
| gpt-5.3-codex-high | GPT-5.3-Codex-High |
| claude-sonnet-4-5-20250929 | Claude-4.5-Sonnet |
| gemini-3-pro-preview | Gemini-3-Pro |
| claude-opus-4-5-20251101-thinking | Claude-Opus4-5-Thinking |
| claude-opus-4-6-thinking | Claude-Opus-4.6-Thinking |
| claude-opus-4-6-20260205 | Claude-Opus-4.6 |
| grok-code-fast-1 | Grok-Code-Fast-1 |
| glm-4.7 | GLM-4.7 |
| minimax-m2.5 | Minimax-M2.5 |
| glm-5 | GLM-5 |
| minimax-m2.1 | Minimax-M2.1 |
| kimi-k2-0905 | Kimi-K2-0905 |
| kimi-k2.5 | Kimi-K2.5 |
| qwen3-next-80b-a3b-instruct | Qwen3-Next-80B-A3B-Instruct |
| qwen3-next-80b-a3b-thinking | Qwen3-Next-80B-A3B-Thinking |

---

## 角色模型分配

| 角色 | 模型ID | 模型全称 |
|------|--------|----------|
| 总编 | [待配置] | - |
| 调研员 | [待配置] | - |
| 写手 | [待配置] | - |
| 编辑 | [待配置] | - |

---

## 配置命令

| 命令 | 说明 |
|------|------|
| `/show-models` | 查看当前模型配置 |
| `/list-models` | 列出可用模型列表 |

---

## 修改记录

| 日期 | 修改人 | 修改内容 |
|------|--------|----------|
| 2026-02-25 | 总编 | 创建模型配置文件 |
| 2026-02-27 | 总编 | 添加首次配置流程说明 |
