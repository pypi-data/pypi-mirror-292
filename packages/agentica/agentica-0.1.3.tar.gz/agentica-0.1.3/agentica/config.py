# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import os
from datetime import datetime

# Load environment variables from .env file
DOTENV_PATH = os.environ.get("DOTENV_PATH", os.path.join(os.getcwd(), ".env"))
try:
    from dotenv import load_dotenv  # noqa
    from loguru import logger  # noqa, need to import logger here to avoid circular import

    if load_dotenv(DOTENV_PATH, override=True):
        logger.info(f"Loaded environment variables from {DOTENV_PATH}")
    else:
        logger.debug(f"No .env file found at {DOTENV_PATH}, skipping...")
except ImportError:
    logger.debug("dotenv not installed, skipping...")

AGENTICA_HOME = os.environ.get("AGENTICA_HOME", os.path.expanduser("~/.agentica"))
DATA_DIR = os.environ.get("DATA_DIR", f"{AGENTICA_HOME}/data")
formatted_date = datetime.now().strftime("%Y%m%d")
LOG_FILE = os.environ.get("LOG_FILE", f"{AGENTICA_HOME}/logs/{formatted_date}.log")
logger.debug(f"LOG_FILE: {LOG_FILE}")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
SMART_LLM = os.environ.get("SMART_LLM")
FAST_LLM = os.environ.get("FAST_LLM")
# Code-interpreter E2B api key
E2B_API_KEY = os.environ.get("E2B_API_KEY")

# Model token limit
MODEL_TOKEN_LIMIT = {
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-instruct": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo-1106": 16384,
    "gpt-3.5-turbo-16k-0613": 16384,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-1106-preview": 128000,
    "gpt-4-0125-preview": 128000,
    "gpt-4-vision-preview": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4-turbo-preview": 128000,
    "gpt-4-turbo-2024-04-09": 128000,
    "gpt-4o": 128000,
    "gpt-4o-2024-05-13": 128000,
    "moonshot-v1-8k": 8000,
    "moonshot-v1-32k": 32000,
    "moonshot-v1-128k": 128000,
    "deepseek-chat": 128000,
    "deepseek-coder": 128000,
}
