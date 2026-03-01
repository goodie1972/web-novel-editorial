# AI Web Novel Editorial 📖

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

一个基于Web的智能小说编辑和创作工具，支持多种主流大模型接入。

## 🚀 主要特性

- ✅ **四步创作流程** - 信息创建 → 角色设定 → 情节大纲 → 章节创作
- ✅ **多模型支持** - Claude / Qwen / ChatGPT / DeepSeek / Gemini
- ✅ **思维导图** - 可拖拽构建总纲和章节
- ✅ **AI自我优化** - 智能评分与迭代优化
- ✅ **智能润色** - 右键菜单快速优化
- ✅ **知识库管理** - 支持长文本记忆
- ✅ **快捷词条** - Shift+L快速输入
- ✅ **主题切换** - 明暗/护眼模式
- ✅ **12种小说类型** - 都市、玄幻、仙侠等

## 📦 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
copy .env.example .env
# 编辑 .env，填入你的API密钥
```

### 3. 启动服务

```bash
python app.py
```

访问：**http://localhost:60001**

## 🔐 环境配置

在 `.env` 中配置必需的API密钥：

```env
# AI模型API密钥（至少配置一个）
CLAUDE_API_KEY=your-claude-api-key
QWEN_API_KEY=your-qwen-api-key
CHATGPT_API_KEY=your-chatgpt-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key

# 服务器配置
PORT=60001
FLASK_DEBUG=False

# 安全配置（可选）
ALLOWED_API_KEYS=key1,key2,key3
```

## 🎯 支持的AI模型

| 模型 | 提供商 | 默认参数 |
|------|--------|----------|
| **Claude 3.5 Sonnet** | Anthropic | 高性能写作模型 |
| **Qwen2.5 72B** | 阿里巴巴 | 高性价比开源模型 |
| **GPT-3.5/4** | OpenAI | 经典大模型 |
| **DeepSeek Chat** | 深度求索 | 高效率模型 |

## 📂 项目结构

```
ai-web-novel-editorial/
├── app.py                  # 🆕 统一主应用
├── requirements.txt        # Python依赖
├── .env.example           # 环境变量模板
├── .gitignore             # Git忽略配置
├── README.md              # 项目文档
├── RELEASE_V6.0.md        # 版本发布说明
├── templates/             # HTML模板
│   └── index_v2.html      # 主界面
├── static/                # 前端静态资源
│   ├── config.js
│   ├── ai-update.js
│   ├── chat-and-counter.js
│   └── ...
└── jpg/                   # 截图资源
```

## 🎮 使用指南

### 四步创作流程

1. **作品信息创建**
   - 设置书名、题材、风格
   - 编写故事简介
   - 选择小说类型

2. **角色设定**
   - 创建主要角色
   - 定义人物关系
   - 设置角色背景

3. **情节大纲规划**
   - 生成故事大纲
   - 设计章节结构
   - 规划剧情节点

4. **章节内容创作**
   - 一键生成章节
   - AI智能润色
   - 迭代优化内容

### 智能优化系统

- **自动分割** - 按句子/段落/字符分割
- **AI评分** - 0-100分综合评分
- **迭代优化** - 最多3次自动优化
- **实时预览** - 优化效果即时查看

### 右键菜单功能

- 深化冲突、增加伏笔
- 完善人物动机
- 强化感情线
- 优化节奏
- 扩充细节
- 提升高潮

## 🔧 技术栈

### 后端
- Flask - Web框架
- Flask-CORS - 跨域支持
- OpenAI SDK - AI接口

### 前端
- HTML5 - 页面结构
- CSS3 - 样式设计
- jQuery - 交互逻辑

### 数据存储
- JSON文件 - 本地存储

## 🔒 安全建议

### 生产环境推荐配置

1. **API密钥验证**
   ```env
   ALLOWED_API_KEYS=your-secure-key-1,your-key-2
   ```

2. **限制CORS**
   - 在 `app.py` 中修改CORS配置
   - 指定允许的域名

3. **使用HTTPS**
   - 通过Nginx反向代理
   - 或使用Cloudflare

4. **环境变量安全**
   - `.env` 文件已添加到 `.gitignore`
   - 请勿提交到Git仓库

## 🐛 常见问题

### Q: API调用失败怎么办？
- 检查API密钥是否正确配置
- 确认网络连接正常
- 查看日志输出获取详细错误

### Q: 如何添加新的模型？
在 `app.py` 的 `API_MODELS` 字典中添加新模型配置即可。

### Q: 端口被占用怎么办？
修改 `.env` 中的 `PORT` 变量，或使用 `python app.py --port 8080` 指定端口。

## 📊 更新日志

### v6.0 (2025.3.1) 🎉
- ✅ 项目重新命名：ai-web-novel-editorial
- ✅ 代码精简：减少80%代码量
- ✅ 安全增强：环境变量 + API密钥验证
- ✅ 统一接口：所有模型使用统一API

### v5.2 (2025.1.23)
- 修复小bug
- 新增谷歌大模型、DeepSeek v3

### v5.0 (2024.12.12)
- 新增思维导图功能
- 修复文本域重叠问题

### v4.0 (2024.12.9)
- 新增AI自我评分迭代功能

### v3.0 (2024.12.8)
- 新增提示词预览修改
- 新增知识库管理

## 📄 许可证

MIT License - 详情见 [LICENSE](LICENSE)

## 👨‍💻 作者

- GitHub: [wfcz10086](https://github.com/wfcz10086)
- 项目主页: https://github.com/wfcz10086/ai-web-novel-editorial

## 🙏 致谢

感谢所有使用和反馈问题的用户！

## 📖 相关链接

- [项目主页](https://github.com/wfcz10086/ai-web-novel-editorial)
- [问题反馈](https://github.com/wfcz10086/ai-web-novel-editorial/issues)
- [许可证](LICENSE)
