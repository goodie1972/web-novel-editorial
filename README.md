# AI 网文编辑部 📖

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个基于 Web 的智能小说创作辅助系统，集成多阶段工作流、角色管理、记忆库和多模型 AI 支持。

## 🚀 主要特性

- ✅ **六阶段创作工作流** - 从创意构思到最终润色的完整流程
- ✅ **智能角色管理** - 主角/配角/群众三分类管理，支持 AI 批量生成
- ✅ **多模型支持** - Claude / Qwen / ChatGPT / DeepSeek / Gemini / 自定义模型
- ✅ **SQLite 记忆库** - 持久化存储创作素材和背景设定
- ✅ **角色配置系统** - 多角色预设，灵活切换不同创作风格
- ✅ **项目管理** - "我的作品"列表，支持项目切换和持久化
- ✅ **配置持久化** - 模型选择、参数设置自动保存

## 📦 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
copy .env.example .env
# 编辑 .env，填入你的 API 密钥
```

### 3. 启动服务

```bash
python app.py
```

访问：**http://localhost:60001**

## 🔐 环境配置

在 `.env` 中配置必需的 API 密钥：

```env
# AI 模型 API 密钥（至少配置一个）
CLAUDE_API_KEY=your-claude-api-key
QWEN_API_KEY=your-qwen-api-key
CHATGPT_API_KEY=your-chatgpt-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
GEMINI_API_KEY=your-gemini-api-key

# 服务器配置
PORT=60001
FLASK_DEBUG=False

# 安全配置（可选）
ALLOWED_API_KEYS=key1,key2,key3
```

## 🎯 支持的 AI 模型

| 模型 | 提供商 | 特点 |
|------|--------|------|
| **Claude 3.5 Sonnet** | Anthropic | 高性能写作模型 |
| **Qwen2.5 72B** | 阿里巴巴 | 高性价比开源模型 |
| **GPT-4** | OpenAI | 经典大模型 |
| **DeepSeek Chat** | 深度求索 | 高效率模型 |
| **Gemini** | Google | 多模态模型 |
| **自定义模型** | 任意 OpenAI 兼容接口 | 灵活配置 |

## 📂 项目结构

```
ai-web-novel-editorial/
├── app.py                      # Flask 主应用
├── requirements.txt            # Python 依赖
├── .env.example               # 环境变量模板
├── .gitignore                 # Git 忽略配置
├── README.md                  # 项目文档
├── templates/                 # HTML 模板
│   ├── index.html             # 欢迎页
│   ├── professional.html      # 专业模式主界面
│   ├── api-info.html          # API 信息页
│   └── mindmap.html           # 思维导图
├── static/                    # 前端静态资源
│   ├── workflow-manager.js    # 工作流管理
│   ├── memory-client.js       # 记忆库客户端
│   └── style.css              # 样式文件
├── services/                  # 业务逻辑层
│   ├── project_service.py     # 项目管理
│   ├── memory_service.py      # 记忆库服务
│   └── ai_service.py          # AI 调用服务
├── data/                      # 数据存储
│   └── projects/              # 项目数据
│       └── {project_id}/
│           ├── project.json   # 项目元数据
│           ├── memory.db      # SQLite 记忆库
│           └── outputs/       # 输出文件
└── tests/                     # 测试脚本
```

## 🎮 使用指南

### 六阶段创作工作流

1. **Stage 1: 创意构思**
   - 输入创意点子
   - AI 辅助完善和扩展

2. **Stage 2: 世界构建**
   - 设定世界观、背景
   - 管理记忆库文档

3. **Stage 3: 项目讨论**
   - AI 角色扮演讨论
   - 生成讨论总结

4. **Stage 4: 角色设定**
   - 三分类角色管理（主角/配角/群众）
   - AI 批量生成角色
   - 编辑角色详情

5. **Stage 5: 情节大纲**
   - 生成故事大纲
   - 设计章节结构

6. **Stage 6: 正文创作**
   - 章节内容生成
   - AI 润色和优化

### 角色管理

- **三分类展示** - 主角、配角、群众分别显示
- **AI 批量生成** - 每个分类独立生成按钮
- **角色详情** - 点击卡牌查看/编辑详情
- **保存/删除** - 带确认对话框，防止误操作

### 记忆库系统

- **SQLite 存储** - 数据持久化，重启不丢失
- **文档管理** - 支持添加、编辑、删除记忆文档
- **检索引用** - AI 创作时自动引用相关内容

## 🔧 技术栈

### 后端
- **Flask** - Web 框架
- **Flask-CORS** - 跨域支持
- **Anthropic SDK** - Claude 官方 SDK
- **OpenAI SDK** - OpenAI 兼容接口
- **python-dotenv** - 环境变量管理

### 前端
- **原生 JavaScript** - 交互逻辑
- **CSS3** - 样式设计
- **SortableJS** - 拖拽排序

### 数据存储
- **SQLite** - 记忆库和项目数据
- **JSON** - 项目元数据

## 🔒 安全建议

### 生产环境推荐配置

1. **API 密钥验证**
   ```env
   ALLOWED_API_KEYS=your-secure-key-1,your-key-2
   ```

2. **限制 CORS**
   - 在 `app.py` 中修改 CORS 配置
   - 指定允许的域名

3. **使用 HTTPS**
   - 通过 Nginx 反向代理
   - 或使用 Cloudflare

4. **环境变量安全**
   - `.env` 文件已添加到 `.gitignore`
   - 请勿提交到 Git 仓库

## 🐛 常见问题

### Q: API 调用失败怎么办？
- 检查 API 密钥是否正确配置
- 确认网络连接正常
- 查看日志输出获取详细错误

### Q: 如何添加新的模型？
在界面的模型配置面板中，使用"自定义模型"选项添加 OpenAI 兼容接口。

### Q: 端口被占用怎么办？
修改 `.env` 中的 `PORT` 变量，或启动时指定端口 `python app.py --port 8080`。

## 📊 更新日志

### v7.0 (2025.3.26)
- ✅ 全新角色管理系统 - 主角/配角/群众三分类
- ✅ SQLite 记忆库替换 JSON 存储
- ✅ 项目持久化与"我的作品"列表
- ✅ 多角色配置系统
- ✅ 配置自动保存/加载

### v6.2 (2025.3.4)
- ✅ 实现真实 API 模型列表获取
- ✅ 添加模型类型分类
- ✅ 新增配置保存/加载功能
- ✅ 优化模型选择界面

### v6.0 (2025.3.1)
- ✅ 项目重新命名：ai-web-novel-editorial
- ✅ 安全增强：环境变量 + API 密钥验证
- ✅ 统一接口：所有模型使用统一 API

## 📄 许可证

MIT License - 详情见 [LICENSE](LICENSE)

## 👨‍💻 作者

- GitHub: [goodie1972](https://github.com/goodie1972)
- 项目主页: https://github.com/goodie1972/web-novel-editorial

## 🙏 致谢

感谢所有使用和反馈问题的用户！

## 📖 相关链接

- [项目主页](https://github.com/goodie1972/web-novel-editorial)
- [问题反馈](https://github.com/goodie1972/web-novel-editorial/issues)
- [许可证](LICENSE)
