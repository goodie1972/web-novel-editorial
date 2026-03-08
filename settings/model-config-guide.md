# 模型配置指南

## 首次配置流程

**当 skill 启动时，按以下步骤配置：**

```
1. 检查 settings.json 中的 modelConfig.roles 是否有配置
2. 检查 settings/model-config.md 中的角色模型分配是否完成
3. 如果未配置：
   - 读取 opencode.json 获取可用模型列表
   - 列出可用模型，让用户一一选择
   - 将选择写入 settings.json 和 model-config.md
```

## 配置命令

| 命令 | 说明 |
|------|------|
| `--onboard` | 首次配置模型 + 创建项目目录 |
| `--config-model [角色] [模型]` | 更改单个角色的模型 |
| `--show-models` | 查看当前模型配置 |
| `--list-models` | 列出所有可用模型 |

## 批量初始化

使用 `--onboard` 命令重新配置所有角色：

```
--onboard
```

系统会：
1. 创建项目目录（用户文档目录下的 webnovel 文件夹）
2. 读取 opencode.json 中的可用模型列表
3. 依次询问每个角色选择哪个模型（总编→调研员→写手→编辑）
4. 自动保存到 settings.json 和 model-config.md

**注意**：运行此命令会引导您为所有角色依次选择模型，不管之前是否有配置。按 `esc` 取消。

## 更改模型配置

已有配置后，使用 `--config-model` 命令更改：

```
--config-model 总编 claude-opus-4-6-thinking
--config-model 调研员 gpt-5.2
--config-model 写手 kimi-k2.5
--config-model 编辑 glm-4.7
```

## 配置位置

- **可用模型来源**：`opencode.json` → `provider.wolfai.models`
- **配置存储**：`settings.json` → `modelConfig.roles`

## 首次配置提示

**当检测到模型未配置时，提示用户：**

```
⚠️ 模型配置未完成！

请运行 --onboard 进行批量初始化配置

或者手动为各角色选择大模型：
--config-model 总编 [模型]
--config-model 调研员 [模型]
--config-model 写手 [模型]
--config-model 编辑 [模型]
```

## 角色说明

| 角色 | 职责 | 建议模型级别 |
|------|------|--------------|
| 总编 | 协调团队、审核内容、双重确认 | Opus/Sonnet |
| 调研员 | 素材调研、读者反馈 | Sonnet |
| 写手 | 章节撰写 | Sonnet/Haiku |
| 编辑 | 内容审核、AI去味 | Sonnet |