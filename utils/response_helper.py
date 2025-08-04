"""API响应助手模块"""
from typing import Any, Dict, Optional
from models import ApiResponse


class ResponseHelper:
    """API响应助手类"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = 200) -> ApiResponse:
        """创建成功响应"""
        return ApiResponse(
            code=code,
            message=message,
            data=data
        )
    
    @staticmethod
    def error(message: str, code: int = 400, data: Any = None) -> ApiResponse:
        """创建错误响应"""
        return ApiResponse(
            code=code,
            message=message,
            data=data
        )
    
    @staticmethod
    def auth_required(message: str = "需要认证") -> ApiResponse:
        """创建认证required响应"""
        return ApiResponse(
            code=401,
            message=message,
            data={"auth_required": True}
        )
    
    @staticmethod
    def not_found(message: str = "资源未找到") -> ApiResponse:
        """创建404响应"""
        return ApiResponse(
            code=404,
            message=message,
            data=None
        )
    
    @staticmethod
    def server_error(message: str = "服务器内部错误", details: Optional[str] = None) -> ApiResponse:
        """创建500响应"""
        data = {"error": "internal_server_error"}
        if details:
            data["details"] = details
            
        return ApiResponse(
            code=500,
            message=message,
            data=data
        )
    
    @staticmethod
    def validation_error(message: str, field: Optional[str] = None) -> ApiResponse:
        """创建数据验证错误响应"""
        data = {"error": "validation_error"}
        if field:
            data["field"] = field
            
        return ApiResponse(
            code=422,
            message=message,
            data=data
        )
    
    @staticmethod
    def from_service_result(result: Dict[str, Any], success_message: str = "操作成功") -> ApiResponse:
        """从服务层结果创建API响应"""
        if "error" in result:
            # 处理服务层错误
            error_type = result.get("error", "unknown_error")
            message = result.get("message", "操作失败")
            
            if error_type == "auth_error":
                return ResponseHelper.auth_required(message)
            elif error_type == "validation_error":
                return ResponseHelper.validation_error(message, result.get("field"))
            elif error_type == "not_found":
                return ResponseHelper.not_found(message)
            else:
                return ResponseHelper.server_error(message, result.get("details"))
        else:
            # 成功响应
            return ResponseHelper.success(result, success_message)
    
    @staticmethod
    def paginated_response(
        data: list, 
        total: int, 
        page: int = 1, 
        page_size: int = 20,
        message: str = "获取成功"
    ) -> ApiResponse:
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size
        
        pagination_data = {
            "items": data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
        return ResponseHelper.success(pagination_data, message)


# 便捷函数
def success_response(data: Any = None, message: str = "操作成功") -> ApiResponse:
    """快捷成功响应函数"""
    return ResponseHelper.success(data, message)


def error_response(message: str, code: int = 400) -> ApiResponse:
    """快捷错误响应函数"""
    return ResponseHelper.error(message, code)


def auth_error_response(message: str = "认证失败") -> ApiResponse:
    """快捷认证错误响应函数"""
    return ResponseHelper.auth_required(message)