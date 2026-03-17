from flask import (
    Flask,
    request,
    Response,
    render_template,
    jsonify,
    stream_with_context,
)
from flask_cors import CORS
import openai
import anthropic
import logging
import os
import json
from functools import wraps
from pathlib import Path
from dotenv import load_dotenv

# Import services
from services.project_service import ProjectManager
from services.memory_service import MemoryManager
from services.role_service import RoleRouter
from services.style_service import StyleLibrary
from services.deflavor_service import AIDeflavoringService
from services.wordcount_service import WordCountService
from services.checkpoint_service import CheckpointService
from services.handover_service import HandoverService

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# 配置CORS - 从环境变量读取允许的来源
allowed_origins = os.environ.get("CORS_ORIGINS", "*")
if allowed_origins == "*":
    CORS(app)
else:
    CORS(app, origins=allowed_origins.split(","))

# 配置日志
log_level = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(levelname)s - [%(name)s] %(message)s"
)
logger = logging.getLogger(__name__)

# 配置数据目录
DATA_DIR = Path(os.environ.get("DATA_DIR", "./data"))
DATA_DIR.mkdir(exist_ok=True)
PROJECT_DATA_FILE = DATA_DIR / "project_data.json"

# 配置请求限制
MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# API超时配置
API_TIMEOUT = int(os.environ.get("API_TIMEOUT", 120))  # 120秒

# API配置 - 从环境变量读取
API_MODELS = {
    "claude": {
        "type": "anthropic",  # 使用 Anthropic SDK
        "api_key": os.environ.get("CLAUDE_API_KEY", ""),
        "model": os.environ.get("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
        "max_tokens": int(os.environ.get("CLAUDE_MAX_TOKENS", 4096)),
    },
    "qwen": {
        "type": "openai",  # 使用 OpenAI 兼容接口
        "endpoint": os.environ.get(
            "QWEN_API_ENDPOINT", "https://api.cloudflare.com/v1"
        ),
        "api_key": os.environ.get("QWEN_API_KEY", ""),
        "model": os.environ.get("QWEN_MODEL", "cloudflare-llama-3-70b"),
    },
    "chatgpt": {
        "type": "openai",
        "endpoint": os.environ.get(
            "CHATGPT_API_ENDPOINT", "https://api.openai.com/v1/chat/completions"
        ),
        "api_key": os.environ.get("CHATGPT_API_KEY", ""),
        "model": os.environ.get("CHATGPT_MODEL", "gpt-3.5-turbo"),
    },
    "deepseek": {
        "type": "openai",
        "endpoint": os.environ.get(
            "DEEPSEEK_API_ENDPOINT", "https://api.deepseek.com/v1/chat/completions"
        ),
        "api_key": os.environ.get("DEEPSEEK_API_KEY", ""),
        "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
    },
}

# 当前活跃模型（可通过设置更新）
ACTIVE_MODEL = os.environ.get("DEFAULT_MODEL", "claude")


def _apply_model_config(config):
    """将保存的模型配置应用到 API_MODELS"""
    global ACTIVE_MODEL
    if not config:
        return

    active_provider = config.get("active_provider") or config.get("provider")
    if active_provider:
        ACTIVE_MODEL = active_provider

    providers = config.get("providers", {})
    # 兼容旧格式（单 provider）
    if not providers and config.get("provider"):
        providers = {
            config["provider"]: {
                "api_key": config.get("api_key", ""),
                "base_url": config.get("base_url", ""),
                "model": config.get("model", ""),
                "api_type": config.get("api_type", "openai_compatible"),
            }
        }

    for provider, settings in providers.items():
        api_key = settings.get("api_key", "")
        base_url = settings.get("base_url", "")
        model_raw = settings.get("model", "")
        # 用户可能选了多个模型（逗号分隔），取第一个作为默认调用模型
        model = model_raw.split(",")[0].strip() if model_raw else ""

        if provider == "claude":
            if api_key:
                API_MODELS["claude"]["api_key"] = api_key
            if model:
                API_MODELS["claude"]["model"] = model
        elif provider in ("deepseek", "qwen"):
            if api_key:
                API_MODELS[provider]["api_key"] = api_key
            if base_url:
                API_MODELS[provider]["endpoint"] = base_url
            if model:
                API_MODELS[provider]["model"] = model
        elif provider == "openai":
            if "openai" not in API_MODELS:
                API_MODELS["openai"] = {
                    "type": "openai",
                    "endpoint": base_url or "https://api.openai.com/v1",
                    "api_key": api_key,
                    "model": model or "gpt-4o",
                }
            else:
                if api_key:
                    API_MODELS["openai"]["api_key"] = api_key
                if base_url:
                    API_MODELS["openai"]["endpoint"] = base_url
                if model:
                    API_MODELS["openai"]["model"] = model
        elif provider == "doubao":
            if "doubao" not in API_MODELS:
                API_MODELS["doubao"] = {
                    "type": "openai",
                    "endpoint": base_url or "https://ark.cn-beijing.volces.com/api/v3",
                    "api_key": api_key,
                    "model": model or "doubao-pro-32k",
                }
            else:
                if api_key:
                    API_MODELS["doubao"]["api_key"] = api_key
                if base_url:
                    API_MODELS["doubao"]["endpoint"] = base_url
                if model:
                    API_MODELS["doubao"]["model"] = model
        elif provider == "custom" or provider.startswith("custom-"):
            api_type = settings.get("api_type", "openai_compatible")
            custom_name = settings.get("name", "自定义模型")
            if api_type == "claude":
                API_MODELS[provider] = {
                    "type": "anthropic",
                    "api_key": api_key,
                    "model": model,
                    "max_tokens": 4096,
                    "name": custom_name,
                }
            else:
                API_MODELS[provider] = {
                    "type": "openai",
                    "endpoint": base_url,
                    "api_key": api_key,
                    "model": model,
                    "name": custom_name,
                }

    logger.info(f"Model config applied, active provider: {ACTIVE_MODEL}")


# 启动时加载已保存的配置
_startup_config_file = DATA_DIR / "config.json"
# 兼容旧配置文件
if not _startup_config_file.exists():
    _old_config_file = DATA_DIR / "model_config.json"
    if _old_config_file.exists():
        _startup_config_file = _old_config_file

if _startup_config_file.exists():
    try:
        with open(_startup_config_file, "r", encoding="utf-8") as _f:
            _startup_config = json.load(_f)
        _apply_model_config(_startup_config)
    except Exception as _e:
        logger.warning(f"Failed to load saved config on startup: {_e}")

# Initialize services
project_manager = ProjectManager(DATA_DIR)
style_library = StyleLibrary(DATA_DIR / "styles.json")
deflavor_service = AIDeflavoringService(DATA_DIR / "deflavor_patterns.json")
wordcount_service = WordCountService()
checkpoint_service = CheckpointService(DATA_DIR)
handover_service = HandoverService(DATA_DIR)


def require_api_key(f):
    """API密钥验证装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return jsonify({"success": False, "error": "缺少API密钥"}), 401

        allowed_keys = os.environ.get("ALLOWED_API_KEYS", "").split(",")
        if api_key not in [k.strip() for k in allowed_keys if k.strip()]:
            return jsonify({"success": False, "error": "无效的API密钥"}), 403

        return f(*args, **kwargs)

    return decorated_function


def create_client(model_config):
    """创建AI客户端"""
    if model_config.get("type") == "anthropic":
        return anthropic.Anthropic(api_key=model_config["api_key"])
    else:
        return openai.OpenAI(
            base_url=model_config["endpoint"],
            api_key=model_config["api_key"],
            timeout=API_TIMEOUT
        )


def stream_response(client, model_config, messages):
    """流式响应生成器"""
    try:
        if model_config.get("type") == "anthropic":
            # 使用 Anthropic SDK
            with client.messages.stream(
                model=model_config["model"],
                max_tokens=model_config.get("max_tokens", 4096),
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    logger.debug(f"Yielding chunk: {text[:50]}...")
                    yield text
        else:
            # 使用 OpenAI 兼容接口
            completion = client.chat.completions.create(
                model=model_config["model"],
                messages=messages,
                stream=True
            )

            for chunk in completion:
                if (
                    chunk.choices
                    and chunk.choices[0].delta
                    and chunk.choices[0].delta.content
                ):
                    content = chunk.choices[0].delta.content
                    logger.debug(f"Yielding chunk: {content[:50]}...")
                    yield content

    except anthropic.APIError as e:
        logger.error(f"Anthropic API Error: {e}")
        yield f"\n\n[错误] Anthropic API请求失败: {str(e)}"
    except openai.APIError as e:
        logger.error(f"OpenAI API Error: {e}")
        yield f"\n\n[错误] API请求失败: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        yield f"\n\n[错误] 生成失败: {str(e)}"


@app.route("/")
@app.route("/professional")
def index():
    """主页面"""
    return render_template("professional.html")


@app.route("/gen", methods=["POST"])
def generate():
    """流式生成接口（用于大纲、章节生成）"""
    return _handle_stream_generation(default_model=ACTIVE_MODEL or "claude")


@app.route("/gen2", methods=["POST"])
def generate2():
    """低成本流式生成接口（默认使用Qwen）"""
    return _handle_stream_generation(default_model="qwen")


def _handle_stream_generation(default_model="claude"):
    """统一的流式生成处理函数"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "无效的请求数据"}), 400

    prompt = data.get("prompt", "")
    if not prompt or not prompt.strip():
        return jsonify({"success": False, "error": "提示词不能为空"}), 400

    # 支持通过 role 参数自动选择模型
    role = data.get("role", "")
    model_name = data.get("model", default_model)
    role_model_override = None

    if role:
        try:
            role_cfg_path = DATA_DIR / "role_config.json"
            if role_cfg_path.exists():
                with open(role_cfg_path, "r", encoding="utf-8") as f:
                    role_cfg = json.load(f)
                if role in role_cfg:
                    model_name = role_cfg[role].get("provider", model_name)
                    role_model_override = role_cfg[role].get("model", "")
        except Exception as e:
            logger.warning(f"Failed to load role config: {e}")

    logger.info(f"Received prompt for {model_name} (length: {len(prompt)})")

    if model_name not in API_MODELS:
        return jsonify({"success": False, "error": f"不支持的模型: {model_name}"}), 400

    model_config = dict(API_MODELS[model_name])
    if role_model_override:
        model_config["model"] = role_model_override

    if not model_config["api_key"]:
        return jsonify({"success": False, "error": "模型未配置API密钥"}), 500

    try:
        client = create_client(model_config)
        messages = [{"role": "user", "content": prompt}]

        return Response(
            stream_with_context(stream_response(client, model_config, messages)),
            mimetype="text/plain",
        )
    except Exception as e:
        logger.error(f"Failed to create stream: {e}")
        return jsonify({"success": False, "error": f"创建流失败: {str(e)}"}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """非流式AI对话接口"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "无效的请求数据"}), 400

    prompt = data.get("prompt", "")
    if not prompt or not prompt.strip():
        return jsonify({"success": False, "error": "提示词不能为空"}), 400

    # 支持通过 role 参数自动选择模型
    role = data.get("role", "")
    model_name = data.get("model", ACTIVE_MODEL or "qwen")
    role_model_override = None
    if role:
        try:
            role_cfg_path = DATA_DIR / "role_config.json"
            if role_cfg_path.exists():
                with open(role_cfg_path, "r", encoding="utf-8") as f:
                    role_cfg = json.load(f)
                if role in role_cfg:
                    model_name = role_cfg[role].get("provider", model_name)
                    role_model_override = role_cfg[role].get("model", "")
        except Exception as e:
            logger.warning(f"Failed to load role config: {e}")

    logger.info(f"Received chat request for {model_name}")

    if model_name not in API_MODELS:
        return jsonify({"success": False, "error": f"不支持的模型: {model_name}"}), 400

    # 用局部 copy，避免修改全局 API_MODELS
    model_config = dict(API_MODELS[model_name])
    if role_model_override:
        model_config["model"] = role_model_override

    logger.info(f"[chat] provider={model_name} model={model_config.get('model')} endpoint={model_config.get('endpoint')} key={str(model_config.get('api_key',''))[:12]}...")

    if not model_config["api_key"]:
        return jsonify({"success": False, "error": "模型未配置API密钥"}), 500

    try:
        client = create_client(model_config)
        messages = [{"role": "user", "content": prompt}]

        if model_config.get("type") == "anthropic":
            # 使用 Anthropic SDK
            logger.info(f"Calling Anthropic API: model={model_config['model']}")
            response = client.messages.create(
                model=model_config["model"],
                max_tokens=model_config.get("max_tokens", 4096),
                messages=messages
            )
            logger.debug(f"Anthropic response: {response}")
            # 安全地提取内容
            if not response.content:
                raise ValueError("Anthropic API返回的content为空")
            content = response.content[0].text
            if not content:
                raise ValueError("Anthropic API返回的内容文本为空")
        else:
            # 使用 OpenAI 兼容接口
            logger.info(f"Calling OpenAI API: model={model_config['model']}")
            response = client.chat.completions.create(
                model=model_config["model"],
                messages=messages,
                stream=False
            )
            logger.debug(f"OpenAI response: {response}")
            # 安全地提取内容
            if not response.choices:
                raise ValueError("OpenAI API返回的choices为空")
            if not response.choices[0].message:
                raise ValueError("OpenAI API返回的message为空")
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("OpenAI API返回的内容文本为空")

        logger.info(f"Chat completed, content length: {len(content)}")
        return jsonify({"success": True, "content": content})

    except anthropic.APIError as e:
        logger.error(f"Anthropic API Error: {e}")
        logger.error(f"Anthropic API Error details: {e.response.text if hasattr(e, 'response') and e.response else 'No response'}")
        return jsonify({"success": False, "error": f"API错误: {str(e)}"}), 500
    except openai.APIError as e:
        logger.error(f"OpenAI API Error: {e}")
        logger.error(f"OpenAI API Error details: {e.response.text if hasattr(e, 'response') and e.response else 'No response'}")
        return jsonify({"success": False, "error": f"API错误: {str(e)}"}), 500
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        return jsonify({"success": False, "error": f"数据解析错误: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"success": False, "error": f"生成失败: {str(e)}"}), 500


@app.route("/api/save", methods=["POST"])
@require_api_key
def save_project():
    """保存项目数据"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "无效的请求数据"}), 400

    try:
        # 使用安全的文件路径
        with open(PROJECT_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Project data saved successfully to {PROJECT_DATA_FILE}")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Failed to save project: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/load", methods=["GET"])
@require_api_key
def load_project():
    """加载项目数据"""
    try:
        if not PROJECT_DATA_FILE.exists():
            return jsonify({"success": True, "data": None})

        with open(PROJECT_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({"success": True, "data": data})
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse project data: {e}")
        return jsonify({"success": False, "error": "项目数据格式错误"}), 500
    except Exception as e:
        logger.error(f"Failed to load project: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/models", methods=["GET"])
def get_models():
    """获取可用模型列表"""
    return jsonify({"success": True, "models": list(API_MODELS.keys())})


@app.route("/api/provider-models", methods=["POST"])
def get_provider_models():
    """获取指定提供商的实际可用模型列表"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "无效的请求数据"}), 400

    provider = data.get("provider", "")
    api_key = data.get("api_key", "")
    base_url = data.get("base_url", "")

    if not provider:
        return jsonify({"success": False, "error": "缺少提供商参数"}), 400

    if not api_key:
        return jsonify({"success": False, "error": "缺少 API Key"}), 400

    try:
        # 根据不同的提供商调用相应的 API
        if provider == "openai" or provider == "custom":
            # OpenAI 和自定义提供商
            if not base_url:
                base_url = "https://api.openai.com/v1"

            client = openai.OpenAI(base_url=base_url, api_key=api_key, timeout=30)
            models_response = client.models.list()

            # 提取模型信息并分类
            models = []
            for model in models_response.data:
                # 打印完整的模型对象以便调试
                logger.info(f"Model object from {provider}: {model}")
                logger.info(f"Model dict: {model.model_dump() if hasattr(model, 'model_dump') else vars(model)}")

                model_info = {
                    "id": model.id,
                    "type": _classify_model_type(model.id),
                    "created": getattr(model, "created", None)
                }
                models.append(model_info)

        elif provider == "qwen":
            # 阿里千问
            if not base_url:
                base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

            client = openai.OpenAI(base_url=base_url, api_key=api_key, timeout=30)
            models_response = client.models.list()

            # 提取模型信息并分类
            models = []
            for model in models_response.data:
                # 打印完整的模型对象以便调试
                logger.info(f"Model object from {provider}: {model}")
                logger.info(f"Model dict: {model.model_dump() if hasattr(model, 'model_dump') else vars(model)}")

                model_info = {
                    "id": model.id,
                    "type": _classify_model_type(model.id),
                    "created": getattr(model, "created", None)
                }
                models.append(model_info)

        elif provider == "deepseek":
            # DeepSeek
            if not base_url:
                base_url = "https://api.deepseek.com/v1"

            client = openai.OpenAI(base_url=base_url, api_key=api_key, timeout=30)
            models_response = client.models.list()

            # 提取模型信息并分类
            models = []
            for model in models_response.data:
                # 打印完整的模型对象以便调试
                logger.info(f"Model object from {provider}: {model}")
                logger.info(f"Model dict: {model.model_dump() if hasattr(model, 'model_dump') else vars(model)}")

                model_info = {
                    "id": model.id,
                    "type": _classify_model_type(model.id),
                    "created": getattr(model, "created", None)
                }
                models.append(model_info)

        elif provider == "claude":
            # Claude/Anthropic - 返回预定义列表（Anthropic API 不提供模型列表端点）
            models = [
                {"id": "claude-opus-4-20250514", "type": "text"},
                {"id": "claude-sonnet-4-20250514", "type": "text"},
                {"id": "claude-3-5-sonnet-20241022", "type": "text"},
                {"id": "claude-3-5-haiku-20241022", "type": "text"},
                {"id": "claude-3-opus-20240229", "type": "text"},
                {"id": "claude-3-sonnet-20240229", "type": "text"},
                {"id": "claude-3-haiku-20240307", "type": "text"}
            ]

        elif provider == "doubao":
            # 豆包 - 返回预定义列表
            models = [
                {"id": "doubao-pro-4k", "type": "text"},
                {"id": "doubao-pro-32k", "type": "text"},
                {"id": "doubao-pro-128k", "type": "text"},
                {"id": "doubao-lite-4k", "type": "text"},
                {"id": "doubao-lite-32k", "type": "text"},
                {"id": "doubao-lite-128k", "type": "text"}
            ]

        else:
            return jsonify({"success": False, "error": f"不支持的提供商: {provider}"}), 400

        logger.info(f"Successfully fetched {len(models)} models for provider: {provider}")
        return jsonify({"success": True, "models": models})

    except openai.APIError as e:
        logger.error(f"API Error when fetching models for {provider}: {e}")
        return jsonify({"success": False, "error": f"API 错误: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error when fetching models for {provider}: {e}")
        return jsonify({"success": False, "error": f"获取模型列表失败: {str(e)}"}), 500


def _classify_model_type(model_id):
    """根据模型ID分类模型类型"""
    model_id_lower = model_id.lower()

    # 嵌入模型（优先判断，因为最明确）
    if any(keyword in model_id_lower for keyword in ["embedding", "embed", "text-embedding"]):
        return "embedding"

    # 语音模型
    if any(keyword in model_id_lower for keyword in ["whisper", "tts", "speech", "audio", "cosyvoice", "paraformer", "sensevoice"]):
        return "audio"

    # 视觉模型（包含图像生成、视频生成、视觉理解）
    vision_keywords = [
        # 图像生成
        "dall-e", "dalle", "stable-diffusion", "midjourney", "imagen", "wanx", "flux",
        # 视频生成
        "video", "cogvideo", "sora",
        # 视觉理解
        "vision", "vl", "visual", "qwen-vl", "qvq", "gpt-4-vision", "gpt-4o",
        # 阿里云百炼的视觉模型
        "qwen2-vl", "qwen-vl-max", "qwen-vl-plus"
    ]
    if any(keyword in model_id_lower for keyword in vision_keywords):
        return "vision"

    # 默认为文本生成模型
    return "text"


@app.route("/api/model-config", methods=["GET", "POST"])
def model_config():
    """保存和加载配置"""
    config_file = DATA_DIR / "config.json"
    # 兼容旧配置文件
    old_config_file = DATA_DIR / "model_config.json"

    if request.method == "POST":
        # 保存配置
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "无效的请求数据"}), 400

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            _apply_model_config(data)
            logger.info("Configuration saved and applied successfully")
            return jsonify({"success": True, "message": "配置已保存并生效"})
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    else:
        # 加载配置
        try:
            # 优先读取新配置文件
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return jsonify({"success": True, "data": data})
            # 兼容旧配置文件
            elif old_config_file.exists():
                with open(old_config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return jsonify({"success": True, "data": data})
            else:
                return jsonify({"success": True, "data": None})
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config: {e}")
            return jsonify({"success": False, "error": "配置文件格式错误"}), 500
        except Exception as e:
            logger.error(f"Failed to load model config: {e}")
            return jsonify({"success": False, "error": str(e)}), 500


# ==================== Role Config API ====================

ROLE_CONFIG_FILE = os.path.join(DATA_DIR, "role_config.json")

@app.route("/api/role-config", methods=["GET", "POST"])
def role_config():
    if request.method == "GET":
        if os.path.exists(ROLE_CONFIG_FILE):
            with open(ROLE_CONFIG_FILE, "r", encoding="utf-8") as f:
                return jsonify(json.load(f))
        return jsonify({})
    else:
        data = request.json or {}
        with open(ROLE_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # Reload role models into RoleRouter
        try:
            with open(ROLE_CONFIG_FILE, "r", encoding="utf-8") as f:
                role_models = json.load(f)
            # Update RoleRouter with new configuration
            role_router = RoleRouter(role_models)
            # Store in app context for use in workflow endpoints
            app.role_router = role_router
            logger.info(f"Role config updated: {list(role_models.keys())}")
        except Exception as e:
            logger.warning(f"Failed to update role router: {e}")
        return jsonify({"success": True})


@app.route("/api/role-config/models", methods=["GET"])
def get_role_models():
    """Get all available models for role configuration"""
    try:
        # Get models from all providers
        models = []
        for provider, config in API_MODELS.items():
            if provider == "claude":
                # Claude models from config
                if config.get("model"):
                    models.append({
                        "provider": provider,
                        "model": config["model"],
                        "label": f"[Claude] {config['model']}"
                    })
            else:
                # OpenAI-compatible models from endpoint
                endpoint = config.get("endpoint", "")
                if endpoint and "dashscope" in endpoint:
                    # Aliyun Qwen specific models
                    qwen_models = [
                        "qwen-plus", "qwen-turbo", "qwen-long", "qwen-max",
                        "qwen3.5-plus", "qwen3-coder-next", "qwen3.5-flash"
                    ]
                    for m in qwen_models:
                        models.append({
                            "provider": provider,
                            "model": m,
                            "label": f"[通义千问] {m}"
                        })
                elif endpoint and "deepseek" in endpoint:
                    deepseek_models = ["deepseek-chat", "deepseek-coder"]
                    for m in deepseek_models:
                        models.append({
                            "provider": provider,
                            "model": m,
                            "label": f"[DeepSeek] {m}"
                        })
                elif endpoint and "openai.com" in endpoint:
                    openai_models = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo", "o1", "o1-mini"]
                    for m in openai_models:
                        models.append({
                            "provider": provider,
                            "model": m,
                            "label": f"[OpenAI] {m}"
                        })

        return jsonify({"success": True, "models": models})
    except Exception as e:
        logger.error(f"Failed to get role models: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== Project Management APIs ====================

@app.route("/api/projects", methods=["POST"])
def create_project():
    """Create new project"""
    data = request.json
    if not data or not data.get("name"):
        return jsonify({"success": False, "error": "项目名称不能为空"}), 400

    try:
        project = project_manager.create_project(
            name=data["name"],
            mode=data.get("mode", "professional"),
            settings=data.get("settings", {})
        )
        return jsonify({"success": True, "project": project})
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/projects", methods=["GET"])
def list_projects():
    """List all projects"""
    try:
        projects = project_manager.list_projects()
        return jsonify({"success": True, "projects": projects})
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/projects/<project_id>", methods=["GET"])
def get_project(project_id):
    """Load project"""
    try:
        project = project_manager.load_project(project_id)
        return jsonify({"success": True, "project": project})
    except FileNotFoundError:
        return jsonify({"success": False, "error": "项目不存在"}), 404
    except Exception as e:
        logger.error(f"Failed to load project: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/projects/<project_id>", methods=["PUT"])
def update_project(project_id):
    """Update project"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "无效的请求数据"}), 400

    try:
        project_manager.save_project(project_id, data)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Failed to update project: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== Memory System APIs ====================

@app.route("/api/memory/<project_id>/<collection>", methods=["POST"])
def add_memory(project_id, collection):
    """Add document to memory"""
    data = request.json
    if not data or not data.get("title") or not data.get("content"):
        return jsonify({"success": False, "error": "标题和内容不能为空"}), 400

    try:
        project_path = DATA_DIR / "projects" / project_id
        memory = MemoryManager(project_path)
        doc_id = memory.add_document(
            collection=collection,
            title=data["title"],
            content=data["content"],
            metadata=data.get("metadata", {})
        )
        return jsonify({"success": True, "doc_id": doc_id})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to add memory: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/memory/<project_id>/<collection>", methods=["GET"])
def query_memory(project_id, collection):
    """Query memory collection"""
    query = request.args.get("q")

    try:
        project_path = DATA_DIR / "projects" / project_id
        memory = MemoryManager(project_path)

        if query:
            documents = memory.query_documents(collection, query)
        else:
            documents = memory.get_all(collection)

        return jsonify({"success": True, "documents": documents})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to query memory: {e}")
        return jsonify({"success": False, "error": str(e)}), 500



@app.route("/api/memory/<project_id>/<collection>/<doc_id>", methods=["PUT"])
def update_memory(project_id, collection, doc_id):
    """Update a memory document"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "无数据"}), 400
    try:
        project_path = DATA_DIR / "projects" / project_id
        memory = MemoryManager(project_path)
        memory.update_document(collection, doc_id, data)
        return jsonify({"success": True})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to update memory: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/memory/<project_id>/<collection>/<doc_id>", methods=["DELETE"])
def delete_memory(project_id, collection, doc_id):
    """Delete a memory document"""
    try:
        project_path = DATA_DIR / "projects" / project_id
        memory = MemoryManager(project_path)
        data = memory._load_collection(collection)
        data["documents"] = [d for d in data["documents"] if d["id"] != doc_id]
        memory._save_collection(collection, data)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Failed to delete memory: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== Workflow & Quality APIs ====================

@app.route("/api/workflow/<project_id>/stage/<int:stage_num>", methods=["POST"])
def execute_stage(project_id, stage_num):
    """Execute workflow stage"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "无效的请求数据"}), 400

    try:
        project = project_manager.load_project(project_id)
        role = data.get("role", "editor_in_chief")
        prompt = data.get("prompt", "")

        role_router = RoleRouter(project.get("settings", {}).get("role_models"))
        model_name = role_router.get_model_for_role(role)

        if model_name not in API_MODELS:
            return jsonify({"success": False, "error": f"模型未配置: {model_name}"}), 400

        model_config = API_MODELS[model_name]
        client = create_client(model_config)
        messages = [{"role": "user", "content": prompt}]

        if data.get("stream", False):
            return Response(
                stream_with_context(stream_response(client, model_config, messages)),
                mimetype="text/plain"
            )
        else:
            if model_config.get("type") == "anthropic":
                response = client.messages.create(
                    model=model_config["model"],
                    max_tokens=model_config.get("max_tokens", 4096),
                    messages=messages
                )
                content = response.content[0].text
            else:
                response = client.chat.completions.create(
                    model=model_config["model"],
                    messages=messages
                )
                content = response.choices[0].message.content

            return jsonify({"success": True, "content": content})

    except Exception as e:
        logger.error(f"Failed to execute stage: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/workflow/<project_id>/quality-gate/<int:stage_num>", methods=["POST"])
def check_quality_gate(project_id, stage_num):
    """Check quality gate"""
    try:
        result = project_manager.check_quality_gate(project_id, stage_num)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.error(f"Failed to check quality gate: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/styles", methods=["GET"])
def get_styles():
    """Get style library"""
    try:
        genre = request.args.get("genre")
        if genre:
            styles = style_library.get_styles_by_genre(genre)
        else:
            genres = style_library.get_all_genres()
            return jsonify({"success": True, "genres": genres})
        return jsonify({"success": True, "styles": styles})
    except Exception as e:
        logger.error(f"Failed to get styles: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/deflavor", methods=["POST"])
def deflavor_analysis():
    """Analyze text for AI patterns"""
    data = request.json
    if not data or not data.get("text"):
        return jsonify({"success": False, "error": "文本不能为空"}), 400

    try:
        result = deflavor_service.analyze_text(data["text"])
        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.error(f"Failed to analyze text: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/wordcount", methods=["POST"])
def wordcount_analysis():
    """Analyze word count for chapter file"""
    data = request.json
    if not data or not data.get("filepath"):
        return jsonify({"success": False, "error": "文件路径不能为空"}), 400

    try:
        file_path = data.get("filepath")
        min_words = data.get("min_words", 4000)

        result = wordcount_service.check_word_count(file_path, min_words)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Failed to count words: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/checkpoint", methods=["POST"])
def create_checkpoint():
    """Create a checkpoint for current project"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "无效的请求数据"}), 400

    project_id = data.get("project_id")
    chapter_start = data.get("chapter_start", 1)
    chapter_end = data.get("chapter_end", 1)

    if not project_id:
        return jsonify({"success": False, "error": "缺少项目ID"}), 400

    try:
        project = project_manager.load_project(project_id)
        project_path = DATA_DIR / "projects" / project_id

        # Collect files to save
        files = []
        outputs_dir = project_path / "outputs"
        if outputs_dir.exists():
            for chapter_file in outputs_dir.glob("**/*.md"):
                files.append({
                    "relative_path": str(chapter_file.relative_to(project_path)),
                    "saved": True
                })

        # Memory files
        memory_files = ["project", "states", "foreshadowing", "chapters"]

        checkpoint_service_instance = CheckpointService(project_path)
        checkpoint = checkpoint_service_instance.create_checkpoint(
            chapter_start=chapter_start,
            chapter_end=chapter_end,
            files=files,
            memory_files=memory_files
        )

        logger.info(f"Checkpoint created: {checkpoint['id']} for chapters {chapter_start}-{chapter_end}")
        return jsonify({"success": True, "checkpoint": checkpoint})
    except Exception as e:
        logger.error(f"Failed to create checkpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/checkpoint/<project_id>", methods=["GET"])
def get_checkpoint(project_id):
    """Get latest checkpoint for project"""
    try:
        project = project_manager.load_project(project_id)
        project_path = DATA_DIR / "projects" / project_id

        checkpoint_service_instance = CheckpointService(project_path)
        latest = checkpoint_service_instance.get_latest_checkpoint()

        if latest:
            return jsonify({"success": True, "checkpoint": latest})
        else:
            return jsonify({"success": True, "checkpoint": None, "message": "No checkpoint found"})
    except Exception as e:
        logger.error(f"Failed to get checkpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/handover/<project_id>", methods=["POST"])
def create_handover(project_id):
    """Create handover document for interrupted project"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "无效的请求数据"}), 400

    try:
        project = project_manager.load_project(project_id)
        project_path = DATA_DIR / "projects" / project_id

        current_chapter = data.get("current_chapter", 1)
        next_tasks = data.get("next_tasks", [])
        special_notes = data.get("special_notes", "")

        handover_service_instance = HandoverService(project_path)
        result = handover_service_instance.create_handover(
            current_chapter=current_chapter,
            next_tasks=next_tasks,
            special_notes=special_notes
        )

        return jsonify(result)
    except Exception as e:
        logger.error(f"Failed to create handover: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/handover/<project_id>", methods=["GET"])
def get_handover(project_id):
    """Get existing handover document"""
    try:
        project = project_manager.load_project(project_id)
        project_path = DATA_DIR / "projects" / project_id

        handover_service_instance = HandoverService(project_path)
        result = handover_service_instance.read_handover()

        if result:
            return jsonify(result)
        else:
            return jsonify({"success": True, "content": None, "message": "No handover found"})
    except Exception as e:
        logger.error(f"Failed to get handover: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== Project Management API ====================

@app.route("/api/projects/<project_id>", methods=["DELETE"])
def delete_project(project_id):
    """Delete a project and all its data"""
    try:
        project_path = DATA_DIR / "projects" / project_id
        if not project_path.exists():
            return jsonify({"success": False, "error": "项目不存在"}), 404

        import shutil
        shutil.rmtree(project_path)
        logger.info(f"Project {project_id} deleted")
        return jsonify({"success": True, "message": "项目已删除"})
    except Exception as e:
        logger.error(f"Failed to delete project: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/projects/<project_id>/backup", methods=["POST"])
def backup_project(project_id):
    """Backup a project as ZIP file"""
    try:
        import zipfile
        import io
        from datetime import datetime

        project_path = DATA_DIR / "projects" / project_id
        if not project_path.exists():
            return jsonify({"success": False, "error": "项目不存在"}), 404

        # Generate backup filename
        project_data = project_manager.load_project(project_id)
        project_name = project_data.get("name", "unknown")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{project_name}_{project_id[:8]}_{timestamp}.zip"

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    arc_path = file_path.relative_to(project_path)
                    zip_file.write(file_path, arcname=arc_path)

        zip_buffer.seek(0)

        # Return as response
        response = Response(
            zip_buffer.getvalue(),
            mimetype='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename="{backup_filename}"',
                'Content-Length': len(zip_buffer.getvalue())
            }
        )
        return response
    except Exception as e:
        logger.error(f"Failed to backup project: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== Memory Collection API ====================

@app.route("/api/projects/<project_id>/memory/<collection>", methods=["GET"])
def export_memory_collection(project_id, collection):
    """Export a memory collection as JSON"""
    try:
        project_path = DATA_DIR / "projects" / project_id
        collection_file = project_path / "memory" / f"{collection}.json"

        if not collection_file.exists():
            return jsonify({"success": False, "error": "集合不存在"}), 404

        with open(collection_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Return as downloadable JSON
        response = Response(
            json.dumps(data, ensure_ascii=False, indent=2),
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename="{collection}_{project_id[:8]}.json"',
            }
        )
        return response
    except Exception as e:
        logger.error(f"Failed to export collection: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/projects/<project_id>/memory/<collection>/import", methods=["POST"])
def import_memory_collection(project_id, collection):
    """Import a memory collection from JSON"""
    try:
        if 'file' not in request.files:
            data = request.json
        else:
            file = request.files['file']
            data = json.load(file)

        project_path = DATA_DIR / "projects" / project_id
        collection_file = project_path / "memory" / f"{collection}.json"

        # Validate data structure
        if not isinstance(data, dict) or "documents" not in data:
            return jsonify({"success": False, "error": "无效的JSON格式"}), 400

        # Append to existing documents
        with open(collection_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)

        existing_documents = existing.get("documents", [])
        new_documents = data.get("documents", [])

        # Merge documents, avoiding duplicates by ID
        existing_ids = {doc.get("id") for doc in existing_documents}
        for doc in new_documents:
            if doc.get("id") not in existing_ids:
                existing_documents.append(doc)

        existing["documents"] = existing_documents

        with open(collection_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        return jsonify({
            "success": True,
            "message": f"已导入 {len(new_documents)} 条记录"
        })
    except json.JSONDecodeError:
        return jsonify({"success": False, "error": "无效的JSON格式"}), 400
    except Exception as e:
        logger.error(f"Failed to import collection: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/projects/<project_id>/memory/<collection>/clear", methods=["POST"])
def clear_memory_collection(project_id, collection):
    """Clear all documents from a memory collection"""
    try:
        project_path = DATA_DIR / "projects" / project_id
        collection_file = project_path / "memory" / f"{collection}.json"

        if not collection_file.exists():
            return jsonify({"success": False, "error": "集合不存在"}), 404

        with open(collection_file, 'w', encoding='utf-8') as f:
            json.dump({"documents": []}, f, ensure_ascii=False, indent=2)

        return jsonify({"success": True, "message": f"集合 {collection} 已清空"})
    except Exception as e:
        logger.error(f"Failed to clear collection: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 60001))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    logger.info(f"Starting server on port {port}")
    logger.info(f"Available models: {list(API_MODELS.keys())}")

    app.run(debug=debug, port=port, host="0.0.0.0")
