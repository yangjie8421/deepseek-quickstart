from typing import Any
import asyncio
import httpx
from mcp.server.fastmcp import FastMCP
from settings import GD_API_BASE_URL, GD_API_KEY

# 1. 初始化 FastMCP 服务器
# 创建一个名为 "weather" 的服务器实例。这个名字有助于识别这套工具。
mcp = FastMCP("chinaweather")

@mcp.tool()
async def get_weather(city: str, extensions: str = 'base'，timeout:int = 30) -> dict:
    """
    异步获取高德天气API数据
    
    Args:
        api_key: 高德开放平台的API Key
        city: 城市编码或城市名称，如："110101" 或 "北京"
        extensions: 返回结果类型，'base'返回实况天气，'all'返回预报天气
    
    Returns:
        天气数据的字典,请求失败时返回None
    """
    
    params = {
        'key': GD_API_KEY,
        'city': city,
        'extensions': extensions,
        'output': 'JSON'
    }
    
    try:
        async with httpx.AsyncClient(timeout) as client:
            
            # 发起GET请求，获取天气数据
            response = await client.get(GD_API_BASE_URL, params=params)

            # 检查HTTP状态码，非正常响应则抛出异常
            response.raise_for_status()

            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP错误: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"请求失败: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
    return None


if __name__ == "__main__":
    mcp.run(transport='stdio')
    