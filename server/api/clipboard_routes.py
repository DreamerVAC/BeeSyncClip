"""
剪切板相关的API路由
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import time
from loguru import logger

from server.security import security_middleware, encryption_manager
from server.redis_manager import redis_manager
from shared.models import ClipboardItem, ClipboardType
from shared.utils import calculate_checksum


clipboard_router = APIRouter(prefix="/clipboard", tags=["剪切板"])


class AddClipboardRequest(BaseModel):
    content: str
    device_id: str
    content_type: Optional[str] = "text/plain"
    encrypted: Optional[bool] = False
    data: Optional[Dict[str, Any]] = None


class DeleteClipboardRequest(BaseModel):
    clip_id: str


class ClearClipboardsRequest(BaseModel):
    pass


def success_response(data: Dict[str, Any], status_code: int = 200) -> JSONResponse:
    """返回成功响应"""
    return JSONResponse(content=data, status_code=status_code)


def error_response(message: str, status_code: int = 400) -> JSONResponse:
    """返回错误响应"""
    return JSONResponse(content={"error": message}, status_code=status_code)


async def require_auth(request: Request) -> Dict[str, Any]:
    """要求认证的装饰器"""
    user_payload = await security_middleware.authenticate_request(request)
    if not user_payload:
        raise HTTPException(status_code=401, detail="未认证的请求")
    return user_payload


@clipboard_router.post("/add")
async def add_clipboard(request: AddClipboardRequest, req: Request):
    """添加剪切板内容"""
    try:
        # 认证用户
        user_payload = await security_middleware.authenticate_request(req)
        if not user_payload:
            return error_response("未认证的请求", 401)
        
        user_id = user_payload['user_id']
        username = user_payload['username']
        
        # 处理加密数据
        if request.encrypted and request.data:
            try:
                content = encryption_manager.decrypt_clipboard_content(request.data, user_id)
            except Exception as e:
                logger.error(f"解密剪切板内容失败: {e}")
                return error_response("数据解密失败", 400)
        else:
            content = request.content
        
        # 验证内容长度
        if len(content) > 10 * 1024 * 1024:  # 10MB限制
            return error_response("内容过大，超过10MB限制", 413)
        
        # 兼容原始API：直接使用MIME类型，不转换为枚举
        # 这样保持与前端和原始服务器的完全兼容
        clipboard_item = ClipboardItem(
            type=ClipboardType.TEXT,  # 内部统一使用TEXT，通过metadata保存原始类型
            content=content,
            metadata={
                "source": "api",
                "encrypted": request.encrypted,
                "original_content_type": request.content_type  # 保存原始content_type
            },
            size=len(content.encode('utf-8')),
            device_id=request.device_id,
            user_id=user_id,
            checksum=calculate_checksum(content)
        )
        
        # 保存到Redis
        if redis_manager.save_clipboard_item(clipboard_item):
            # 发布同步消息给其他设备
            sync_message = {
                "action": "add",
                "data": {
                    "clip_id": clipboard_item.id,
                    "content": content,
                    "content_type": request.content_type,
                    "created_at": clipboard_item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "device_id": request.device_id,
                    "checksum": clipboard_item.checksum
                },
                "source_device": request.device_id,
                "timestamp": clipboard_item.created_at.isoformat()
            }
            
            redis_manager.publish_clipboard_sync(user_id, sync_message['action'], sync_message['data'], sync_message.get('source_device'))
            
            logger.info(f"剪切板内容已添加: user={username}, size={clipboard_item.size}")
            
            return success_response({
                "success": True,
                "clip_id": clipboard_item.id,
                "message": "剪切板内容已添加"
            })
        else:
            return error_response("保存剪切板内容失败", 500)
            
    except Exception as e:
        logger.error(f"添加剪切板内容失败: {e}")
        return error_response("添加剪切板内容失败", 500)


@clipboard_router.get("/list")
async def get_clipboards(req: Request, encrypted: bool = False):
    """获取剪切板历史"""
    try:
        # 认证用户
        user_payload = await security_middleware.authenticate_request(req)
        if not user_payload:
            return error_response("未认证的请求", 401)
        
        user_id = user_payload['user_id']
        username = user_payload['username']
        
        # 获取剪切板历史
        history = redis_manager.get_user_clipboard_history(user_id, page=1, per_page=50)
        
        # 处理加密
        if encrypted:
            try:
                # 加密每个剪切板项的内容
                for item in history.items:
                    if hasattr(item, 'content'):
                        encrypted_content = encryption_manager.encrypt_clipboard_content(
                            item.content, user_id
                        )
                        item.content = encrypted_content
                        item.encrypted = True
            except Exception as e:
                logger.error(f"加密剪切板内容失败: {e}")
                return error_response("数据加密失败", 500)
        
        logger.debug(f"获取剪切板历史: user={username}, count={len(history.items)}")
        
        return success_response({
            "success": True,
            "clipboards": [
                {
                    "id": item.id,
                    "content": item.content,
                    "content_type": item.metadata.get('original_content_type', 'text/plain'),
                    "timestamp": item.created_at.isoformat(),
                    "device_id": item.device_id,
                    "size": item.size,
                    "checksum": item.checksum,
                    "encrypted": getattr(item, 'encrypted', False)
                }
                for item in history.items
            ],
            "total": history.total,
            "page": history.page,
            "per_page": history.per_page
        })
        
    except Exception as e:
        logger.error(f"获取剪切板历史失败: {e}")
        return error_response("获取剪切板历史失败", 500)


@clipboard_router.get("/latest")
async def get_latest_clipboard(req: Request, encrypted: bool = False):
    """获取最新的剪切板内容"""
    try:
        # 认证用户
        user_payload = await security_middleware.authenticate_request(req)
        if not user_payload:
            return error_response("未认证的请求", 401)
        
        user_id = user_payload['user_id']
        
        # 获取最新的剪切板项
        latest_item = redis_manager.get_latest_clipboard_item(user_id)
        
        if not latest_item:
            return success_response({
                "success": True,
                "clipboard": None,
                "message": "没有剪切板内容"
            })
        
        # 处理加密
        content = latest_item.content
        is_encrypted = False
        
        if encrypted:
            try:
                encrypted_content = encryption_manager.encrypt_clipboard_content(
                    content, user_id
                )
                content = encrypted_content
                is_encrypted = True
            except Exception as e:
                logger.error(f"加密最新剪切板内容失败: {e}")
                return error_response("数据加密失败", 500)
        
        return success_response({
            "success": True,
            "clipboard": {
                "id": latest_item.id,
                "content": content,
                "content_type": latest_item.type.value,
                "timestamp": latest_item.created_at.isoformat(),
                "device_id": latest_item.device_id,
                "size": latest_item.size,
                "checksum": latest_item.checksum,
                "encrypted": is_encrypted
            }
        })
        
    except Exception as e:
        logger.error(f"获取最新剪切板内容失败: {e}")
        return error_response("获取最新剪切板内容失败", 500)


@clipboard_router.delete("/{clip_id}")
async def delete_clipboard(clip_id: str, req: Request):
    """删除指定的剪切板内容"""
    try:
        # 认证用户
        user_payload = await security_middleware.authenticate_request(req)
        if not user_payload:
            return error_response("未认证的请求", 401)
        
        user_id = user_payload['user_id']
        username = user_payload['username']
        
        # 删除剪切板项
        success = redis_manager.delete_clipboard_item(clip_id)
        
        if success:
            # 发布同步消息
            sync_message = {
                "action": "delete",
                "data": {"id": clip_id},
                "source_device": user_payload['device_id'],
                "timestamp": str(int(time.time()))
            }
            
            redis_manager.publish_clipboard_sync(user_id, sync_message['action'], sync_message['data'], sync_message.get('source_device'))
            
            logger.info(f"剪切板内容已删除: user={username}, clip_id={clip_id}")
            
            return success_response({
                "success": True,
                "message": "剪切板内容已删除"
            })
        else:
            return error_response("删除失败，内容不存在或无权限", 404)
            
    except Exception as e:
        logger.error(f"删除剪切板内容失败: {e}")
        return error_response("删除剪切板内容失败", 500)


@clipboard_router.post("/clear")
async def clear_clipboards(req: Request):
    """清空所有剪切板内容"""
    try:
        # 认证用户
        user_payload = await security_middleware.authenticate_request(req)
        if not user_payload:
            return error_response("未认证的请求", 401)
        
        user_id = user_payload['user_id']
        username = user_payload['username']
        
        # 清空剪切板
        success = redis_manager.clear_user_clipboard_history(user_id)
        
        if success:
            # 发布同步消息
            sync_message = {
                "action": "clear",
                "data": {},
                "source_device": user_payload['device_id'],
                "timestamp": str(int(time.time()))
            }
            
            redis_manager.publish_clipboard_sync(user_id, sync_message['action'], sync_message['data'], sync_message.get('source_device'))
            
            logger.info(f"剪切板已清空: user={username}")
            
            return success_response({
                "success": True,
                "message": "剪切板已清空"
            })
        else:
            return error_response("清空剪切板失败", 500)
            
    except Exception as e:
        logger.error(f"清空剪切板失败: {e}")
        return error_response("清空剪切板失败", 500)


@clipboard_router.get("/stats")
async def get_clipboard_stats(req: Request):
    """获取剪切板统计信息"""
    try:
        # 认证用户
        user_payload = await security_middleware.authenticate_request(req)
        if not user_payload:
            return error_response("未认证的请求", 401)
        
        user_id = user_payload['user_id']
        
        # 获取统计信息
        stats = redis_manager.get_user_clipboard_stats(user_id)
        
        return success_response({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"获取剪切板统计失败: {e}")
        return error_response("获取剪切板统计失败", 500) 