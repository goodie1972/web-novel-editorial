# 帮助命令 - web-novel-editorial

**当前 Skill**: 网文编辑部 (web-novel-editorial)

> 💡 提示：进入 skill 后，命令栏会显示当前所在的 skill 名称

---

使用 `--help` 命令查看所有可用命令。

---

## 命令列表

### 模型配置

| 命令 | 说明 |
|------|------|
| `--help` | 显示帮助信息 |
| `--onboard` | 首次使用，批量初始化所有角色的模型 |
| `--config-model [角色] [模型]` | 更改单个角色的模型 |
| `--show-models` | 查看当前模型配置 |
| `--list-models` | 列出所有可用模型 |

### 项目管理

| 命令 | 说明 |
|------|------|
| `--new` | 创建新网文项目 |
| `--continue` | 继续当前项目 |
| `--status` | 查看项目进度 |

---

## 团队角色

| 角色 | 职责 |
|------|------|
| 总编 | 协调团队、审核内容 |
| 调研员 | 素材调研、资料收集 |
| 写手 | 章节撰写、内容生成 |
| 编辑 | 内容审核、质量把控 |

---

## 模型配置

### 批量初始化 - 重新配置所有角色

```
--onboard
```

运行此命令会引导您为所有角色（总编→调研员→写手→编辑）依次选择模型，按 `esc` 取消。

### 单独更改

```
--config-model 总编 claude-opus-4-6-thinking
--config-model 调研员 gpt-5.2
--config-model 写手 kimi-k2.5
--config-model 编辑 glm-4.7
```

### 查看配置

```
--show-models   # 查看当前配置
--list-models  # 列出可用模型

### 更改模型配置

已有配置后，使用 `--config-model` 命令更改：

```
--config-model 总编 claude-opus-4-6-thinking
--config-model 调研员 gpt-5.2
--config-model 写手 kimi-k2.5
--config-model 编辑 glm-4.7
```

---

## 快速开始

1. **首次使用**：系统会自动提示配置模型

2. **创建项目**
   > --new 修仙
   > 项目将创建在 `Documents/webnovel/` 目录下

3. **查看状态**
   > --status

---

## 项目位置

所有小说项目都创建在用户文档目录下的 `webnovel/` 子目录中（Windows: `C:\Users\[用户名]\Documents\webnovel\`），结构如下：

```
Documents/webnovel/
├── 项目名称/
│   ├──大纲.md
│   ├──人设.md
│   ├──世界.md
│   └──章节/
│       ├── chapter-001.md
│       └── ...
```
