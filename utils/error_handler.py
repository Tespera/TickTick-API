"""统一错误处理模块"""
import functools
from typing import Any, Callable, Dict, Optional
from fastapi import HTTPException
from utils import app_logger
from models import ApiResponse


class ErrorHandler:
    """统一错误处理器"""
    
    @staticmethod
    def handle_service_error(error: Exception, context: str = "服务") -> Dict[str, Any]:
        """处理服务层错误"""
        error_msg = f"{context}操作失败: {str(error)}"
        app_logger.error(error_msg)
        
        # 根据异常类型返回不同的错误信息
        if isinstance(error, ConnectionError):
            return {
                "error": "connection_error",
                "message": "网络连接失败，请检查网络设置",
                "details": str(error)
            }
        elif isinstance(error, TimeoutError):
            return {
                "error": "timeout_error", 
                "message": "请求超时，请稍后重试",
                "details": str(error)
            }
        elif isinstance(error, ValueError):
            return {
                "error": "invalid_data",
                "message": "数据格式错误",
                "details": str(error)
            }
        else:
            return {
                "error": "internal_error",
                "message": "系统内部错误",
                "details": str(error)
            }
    
    @staticmethod
    def handle_auth_error(message: str = "认证失败") -> Dict[str, Any]:
        """处理认证错误"""
        app_logger.warning(f"认证错误: {message}")
        return {
            "error": "auth_error",
            "message": message,
            "auth_required": True
        }
    
    @staticmethod
    def handle_validation_error(message: str, field: Optional[str] = None) -> Dict[str, Any]:
        """处理数据验证错误"""
        app_logger.warning(f"数据验证错误: {message}")
        error_data = {
            "error": "validation_error",
            "message": message
        }
        if field:
            error_data["field"] = field
        return error_data


def api_error_handler(context: str = "API", return_response: bool = True):
    """API错误处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except HTTPException:
                # 重新抛出FastAPI HTTP异常
                raise
            except Exception as e:
                error_data = ErrorHandler.handle_service_error(e, context)
                
                if return_response:
                    return ApiResponse(
                        code=500,
                        message=error_data["message"],
                        data=error_data
                    )
                else:
                    return error_data
        return wrapper
    return decorator


def service_error_handler(context: str = "服务"):
    """服务层错误处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                return ErrorHandler.handle_service_error(e, context)
        return wrapper
    return decorator


def safe_execute(func: Callable, default_value: Any = None, context: str = "操作") -> Any:
    """安全执行函数，捕获异常并返回默认值"""
    try:
        return func()
    except Exception as e:
        app_logger.warning(f"{context}执行失败: {e}")
        return default_value


async def safe_execute_async(func: Callable, default_value: Any = None, context: str = "异步操作") -> Any:
    """安全执行异步函数，捕获异常并返回默认值"""
    try:
        return await func()
    except Exception as e:
        app_logger.warning(f"{context}执行失败: {e}")
        return default_value