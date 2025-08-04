"""HTTP客户端管理模块"""
import httpx
from typing import Optional
from core.config import config


class HTTPClientManager:
    """HTTP客户端管理器，提供共享的异步HTTP客户端"""
    
    _instance: Optional['HTTPClientManager'] = None
    _client: Optional[httpx.AsyncClient] = None
    
    def __new__(cls) -> 'HTTPClientManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            request_config = config.get('request_config', {})
            timeout = request_config.get('timeout', 30.0)
            
            # 创建共享的HTTP客户端，配置连接池参数
            self._client = httpx.AsyncClient(
                timeout=timeout,
                limits=httpx.Limits(
                    max_keepalive_connections=20,  # 最大保持连接数
                    max_connections=100,           # 最大总连接数
                    keepalive_expiry=30.0          # 连接保持时间
                ),
                http2=True  # 启用HTTP/2支持
            )
    
    @property
    def client(self) -> httpx.AsyncClient:
        """获取HTTP客户端实例"""
        if self._client is None:
            self.__init__()
        return self._client
    
    async def close(self):
        """关闭HTTP客户端"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None


# 全局HTTP客户端管理器实例
http_client_manager = HTTPClientManager()