"""
DatiAI 配置文件
包含应用的基本设置和常量
"""
import os

# 基础配置
APP_NAME = "智能答题助手 (DatiAI)"
APP_VERSION = "1.0.0"
DEBUG = True

# 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
DATA_DIR = os.path.join(BASE_DIR, 'data')
SCREENSHOT_DIR = os.path.join(DATA_DIR, 'screenshots')
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')

# 确保必要的目录存在
for dir_path in [SCREENSHOT_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

# 截图设置
SCREENSHOT_HOTKEY = "ctrl+alt+a"  # 全局热键
SCREENSHOT_FORMAT = "png"         # 截图格式

# Coze API 设置 (从原始AIdati.py复制)
AUTH_TOKEN = "Bearer pat_vgjLmxuJoQVlObQdTYa6OLThw12eXK2vqigFtEIKv0AHIivRVVTVARr5aSt3qCZi"
BOT_ID = "7484971600212033570"
WORKFLOW_ID = "7484954756813996069"

# Web服务设置
HOST = "127.0.0.1"
PORT = 5000

# Nginx反向代理设置（可选）
USE_NGINX = False
NGINX_PORT = 80 