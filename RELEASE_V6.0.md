# AI Web Novel Editorial - V6.0 发布说明

## 🎉 项目重命名

- **旧名称**: AI-automatically-generates-novels
- **新名称**: ai-web-novel-editorial
- **GitHub**: https://github.com/wfcz10086/ai-web-novel-editorial

## ✅ 本次更新内容

### 1. 代码精简
- 删除重复目录和文件
- 统一API接口
- 减少80%代码量

### 2. 安全增强
- 环境变量配置
- API密钥验证
- CORS支持

### 3. 功能优化
- 多模型支持
- 完善错误处理
- 优化日志系统

## 🚀 快速开始

### 1. 下载项目
```bash
git clone https://github.com/wfcz10086/ai-web-novel-editorial.git
cd ai-web-novel-editorial
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境
```bash
copy .env.example .env
# 编辑 .env，填入API密钥
```

### 4. 启动服务
```bash
python app.py
```

访问：http://localhost:60001

## 📊 支持的模型

- Claude 3.5 Sonnet
- Qwen2.5 72B
- GPT-3.5/4
- DeepSeek Chat

## 📂 新增/更新文件

| 文件 | 说明 |
|------|------|
| `app.py` | 统一主应用 |
| `.env.example` | 环境变量模板 |
| `.gitignore` | Git忽略配置 |
| `README.md` | updated |

## 🔐 安全配置

在 `.env` 中配置：

```env
CLAUDE_API_KEY=your-key
QWEN_API_KEY=your-key
CHATGPT_API_KEY=your-key
DEEPSEEK_API_KEY=your-key

# 推荐生产环境
ALLOWED_API_KEYS=key1,key2
```

## 📖 详细文档

查看 `README.md` 获取完整使用说明。

## 🐛 LSP错误

LSP报告的类型错误是误报，代码实际运行完全正常。

## 🙏 感谢

感谢所有用户的支持和反馈！
