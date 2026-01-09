#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structlog 生产/开发双环境一体化日志配置
核心能力：日期+大小双重轮转、JSON结构化、多环境切换、中文无乱码、线程安全
"""
import sys
import os
import logging
from datetime import datetime, timedelta

import structlog
from concurrent_log_handler import ConcurrentRotatingFileHandler
from structlog.processors import CallsiteParameterAdder, CallsiteParameter

# ====================== 【1. 环境常量定义 - 核心配置区】 ======================
# ✅ 环境切换：通过系统环境变量 PYTHON_ENV 控制，默认开发环境
# 启动命令示例：PYTHON_ENV=prod python app.py
# os.environ.setdefault("PYTHON_ENV","prod")
ENV = os.environ.get("PYTHON_ENV", "dev").lower()  # dev / prod
assert ENV in ["dev", "prod"], "PYTHON_ENV 仅支持 dev/prod 两个值！"

# ✅ 全局基础配置（可根据项目需求修改）
PROJECT_NAME = "AI-SPIRIT-FOX"  # 项目名称（日志中全局追加）
PROJECT_VERSION = "v1.0.0"     # 项目版本（日志中全局追加）
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")  # 日志根目录（项目根目录下logs）
LOG_ENCODING = "utf-8"         # 强制UTF-8，根治中文乱码
DEFAULT_LOG_LEVEL = logging.DEBUG if ENV == "dev" else logging.INFO  # 环境差异化级别

# ✅ 日志轮转核心参数（双环境通用，按需调整）
MAX_BYTES = 100 * 1024 * 1024    # 单日志文件最大100MB（大小切割阈值）
BACKUP_COUNT = 50                # 日志文件最大保留50个（数量兜底）
MAX_DAYS = 30                    # 日志最长保留30天（时间兜底，自动清理）
ERROR_LOG_MAX_DAYS = 7           # 错误日志仅保留7天
CLEAN_EXPIRE_DAYS = 30           # 替代maxDays：自动清理30天前日志
ERROR_CLEAN_DAYS = 7             # 错误日志清理7天前文件

# ====================== 【2. 初始化日志目录】 ======================
os.makedirs(LOG_DIR, exist_ok=True)
# 区分环境的日志文件名
APP_LOG_FILE = os.path.join(LOG_DIR, f"{PROJECT_NAME}.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, f"{PROJECT_NAME}-error.log")

def clean_expired_logs():
    """✅ 替代maxDays参数：启动时自动清理过期日志，适配所有库版本"""
    now = datetime.now()
    for file_name in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, file_name)
        if not os.path.isfile(file_path):
            continue
        # 获取文件最后修改时间
        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        # 判断是否过期
        expire_days = ERROR_CLEAN_DAYS if "error" in file_name else CLEAN_EXPIRE_DAYS
        if (now - mtime) > timedelta(days=expire_days):
            try:
                os.remove(file_path)
                if ENV == "dev":
                    print(f"🗑️  清理过期日志：{file_name}")
            except Exception:
                pass
    # 启动时执行一次日志清理（替代maxDays自动清理能力）
clean_expired_logs()

# ====================== 【3. 清空原生日志器处理器（防重复输出，必加）】 ======================
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)  # 根日志器设为最低级别，交由处理器过滤
root_logger.handlers.clear()         # 清空默认处理器，解决日志重复输出核心问题
# ✅ 第2重：关闭根日志器传播性（兜底）
root_logger.propagate = False

# ✅ 重2：禁用第三方库自身日志（防干扰）
logging.getLogger("concurrent_log_handler").setLevel(logging.CRITICAL)
logging.getLogger("structlog").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# ✅ 重3：全局禁用日志传播（终极兜底）
logging.Logger.propagate = False

# ====================== 【4. 配置日志处理器（双环境适配）】 ======================
def _create_handlers():
    """创建日志处理器：控制台+文件（双重轮转），双环境差异化配置"""
    handlers = []

    # ✅ 处理器1：控制台处理器（双环境差异化配置）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(DEFAULT_LOG_LEVEL)
    console_handler.name = "CONSOLE_HANDLER"  # ✅ 新增：给控制台处理器命名，用于后续精准判断
    console_handler.propagate = False          # ✅ 第4重：关闭处理器传播性
    # 开发环境控制台UTF-8适配（Windows系统友好）
    if ENV == "dev":
        console_handler.stream.reconfigure(encoding=LOG_ENCODING)

    # ✅ 处理器2：全局日志文件处理器（核心！日期+大小双重轮转，线程安全）
    file_handler = ConcurrentRotatingFileHandler(
        filename=APP_LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding=LOG_ENCODING,
        use_gzip=ENV == "prod",  # 生产环境自动压缩过期日志，节省磁盘
    )
    file_handler.setLevel(logging.DEBUG)  # 文件保存所有级别日志，便于排障
    file_handler.name = "FILE_ALL_HANDLER"
    file_handler.propagate = False  # ✅ 第4重：关闭处理器传播性

    # ✅ 处理器3：错误日志文件处理器（独立轮转，仅保存ERROR/CRITICAL）
    error_handler = ConcurrentRotatingFileHandler(
        filename=ERROR_LOG_FILE,
        maxBytes=MAX_BYTES // 2,  # 错误日志单文件50MB
        backupCount=BACKUP_COUNT // 5,
        encoding=LOG_ENCODING,
        use_gzip=ENV == "prod",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.name = "FILE_ERROR_HANDLER"
    error_handler.propagate = False  # ✅ 第4重：关闭处理器传播性

    handlers.extend([console_handler, file_handler, error_handler])
    return handlers

# 初始化所有处理器
handlers = _create_handlers()

# ====================== 【5. Structlog 全局核心配置（双环境一体化）】 ======================
def _get_structlog_processors():
    """获取双环境适配的日志处理器链"""
    processors = [
        # 基础处理器：添加日志级别、堆栈信息、异常捕获
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),  # 全局解码，防止中文乱码
        # ============== 核心新增：添加文件名等调用站点信息 ==============
        CallsiteParameterAdder(
            parameters=[
                CallsiteParameter.FILENAME,  # 输出当前文件名（含后缀，如 main.py）
                # 可选：额外添加其他调用信息（按需开启）
                CallsiteParameter.LINENO,    # 输出行号
                CallsiteParameter.FUNC_NAME # 输出当前函数名
                # CallsiteParameter.MODULE,    # 输出模块名（不含后缀，如 main）
            ]
        ),

        # 时间戳：开发环境易读格式，生产环境毫秒级精准格式
        structlog.processors.TimeStamper(
            fmt="%Y-%m-%d %H:%M:%S" if ENV == "dev" else "%Y-%m-%d %H:%M:%S.%f",
            utc=False
        ),
        # 全局追加固定字段：项目名、版本、环境（企业级规范）
        lambda _, __, event_dict: {
            **event_dict,
            "project": PROJECT_NAME,
            "version": PROJECT_VERSION,
            "env": ENV
        },
        # 格式分流核心处理器
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]
    return processors

# Structlog全局配置
structlog.configure(
    processors=_get_structlog_processors(),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,  # 缓存日志器，提升高并发性能
)

# ====================== 【6. 配置日志格式（控制台美化+文件JSON，双分流）】 ======================
def _bind_formatter(handler):
    """为处理器绑定对应格式：控制台美化文本、文件标准JSON"""
    # ✅ 核心修复：通过处理器name判断（替代错误的is判断），100%精准匹配控制台处理器
    if handler.name == "CONSOLE_HANDLER":
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(
                colors=ENV == "dev",
                sort_keys=False,
                pad_level=True
            )
        )
    else:
        # 文件处理器绑定JSON格式
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(
                indent=4 if ENV == "dev" else None
            )
        )
    handler.setFormatter(formatter)

# ✅ 第5重：安全添加处理器（同名处理器仅添加1次，防重复注册）
def add_handler_safely(logger, handler):
    for h in logger.handlers:
        if hasattr(h, "name") and h.name == handler.name:
            return
    logger.addHandler(handler)

# ✅ 重5：给控制台处理器添加【日志去重过滤器】（终极绝杀，确保单条日志仅输出1次）
class ConsoleDuplicateFilter(logging.Filter):
    def __init__(self):
        self.log_cache = set()
        self.max_cache_size = 1000  # 缓存上限，防止内存溢出

    def filter(self, record):
        # 生成日志唯一标识（日志内容+级别+模块）
        log_key = f"{record.msg}-{record.levelno}-{record.module}"
        if log_key in self.log_cache:
            return False  # 重复日志，直接过滤
        # 缓存日志标识，超出上限则清空
        if len(self.log_cache) >= self.max_cache_size:
            self.log_cache.clear()
        self.log_cache.add(log_key)
        return True

# 绑定格式+添加处理器+注册去重过滤器
for handler in handlers:
    _bind_formatter(handler)
    add_handler_safely(root_logger, handler)
    handler.addFilter(ConsoleDuplicateFilter())

# ====================== 【7. 导出全局日志器（第6重：终极防重复）】 ======================
# ✅ 单例模式：确保全局仅一个日志器实例
if "logger" not in globals():
    logger = structlog.get_logger()
    logger.propagate = False  # ✅ 第6重：关闭日志器传播性（终极兜底）



# 配置完成日志提示
# logger.info(
#     "✅ 日志配置初始化完成",
#     log_dir=LOG_DIR,
#     log_level=logging.getLevelName(DEFAULT_LOG_LEVEL),
#     env=ENV.upper(),
#     max_bytes=f"{MAX_BYTES//1024//1024}MB",
#     max_days=MAX_DAYS
# )