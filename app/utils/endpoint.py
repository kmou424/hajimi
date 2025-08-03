"""
自定义端点和请求头工具模块
"""

import re
from typing import Dict
from urllib.parse import urlparse
import app.config.settings as settings
from app.utils.logging import log


def get_custom_endpoint() -> str:
    """
    获取自定义API端点，如果用户没有配置或配置无效，则返回默认值

    Returns:
        str: 有效的API端点URL
    """
    default_endpoint = "https://generativelanguage.googleapis.com"

    if not settings.CUSTOM_ENDPOINT:
        return default_endpoint

    custom_endpoint = settings.CUSTOM_ENDPOINT.strip()

    # 验证URL格式
    try:
        parsed = urlparse(custom_endpoint)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"自定义端点URL格式无效: {custom_endpoint}")

        if parsed.scheme not in ["http", "https"]:
            raise ValueError(
                f"自定义端点协议无效: {parsed.scheme}，必须是 http 或 https"
            )

        endpoint = custom_endpoint.rstrip("/")
        log("info", f"使用自定义API(路径已隐藏): {parsed.scheme}://{parsed.netloc}")
        return endpoint

    except Exception as e:
        log("error", f"{e}，使用默认端点")
        return default_endpoint


def parse_custom_headers() -> Dict[str, str]:
    """
    解析自定义请求头配置

    配置格式: key1=val1;key2=val2

    Returns:
        Dict[str, str]: 解析后的请求头字典
    """
    headers = {}

    if not settings.CUSTOM_HEADERS:
        return headers

    custom_headers = settings.CUSTOM_HEADERS.strip()

    try:
        # 按分号分割每个头部配置
        header_pairs = custom_headers.split(";")

        for pair in header_pairs:
            pair = pair.strip()
            if not pair:
                continue

            if "=" not in pair:
                continue

            key, value = pair.split("=", 1)
            key = key.strip()
            value = value.strip()

            if not key:
                continue

            # 验证头部名称格式（基本的HTTP头部名称规则）
            if not re.match(r"^[a-zA-Z][a-zA-Z0-9\-_]*$", key):
                continue

            headers[key] = value

        if headers:
            log("info", f"加载了 {len(headers)} 个自定义请求头")

    except Exception as e:
        log("error", f"解析自定义请求头时出错: {e}")
        return {}

    return headers
