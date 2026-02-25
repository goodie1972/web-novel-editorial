# 帮助命令

使用 `/help` 命令查看所有可用命令。

---

## 命令列表

### 模型配置

| 命令 | 说明 | 示例 |
|------|------|------|
| `/help` | 显示帮助信息 | `/help` |
| `/config-model` | 配置角色的大模型 | `/config-model 写手 gpt-4-turbo` |
| `/show-models` | 查看当前模型配置 | `/show-models` |
| `/list-models` | 列出所有可用模型 | `/list-models` |

### 项目管理

| 命令 | 说明 | 示例 |
|------|------|------|
| `/new` | 创建新网文项目 | `/new 都市` |
| `/continue` | 继续当前项目 | `/continue` |
| `/status` | 查看项目进度 | `/status` |

---

## 团队角色

| 角色 | 职责 |
|------|------|
| 总编 | 协调团队、审核内容 |
| 调研员 | 素材调研、资料收集 |
| 写手 | 章节撰写、内容生成 |
| 编辑 | 内容审核、质量把控 |

---

## 快速开始

1. **首次使用**：先配置模型
   ```
   /config-model 总编 claude-opus-4-20250514
   /config-model 调研员 gemini-1.5-pro
   /config-model 写手 gpt-4-turbo
   /config-model 编辑 claude-sonnet-4-20250514
   ```

2. **创建项目**
   ```
   /new 修仙
   ```

3. **查看状态**
   ```
   /status
   ```

---

## 更多帮助

- 查看模型配置：`/show-models`
- 查看可用模型：`/list-models`
- 继续现有项目：`/continue`
