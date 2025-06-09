"""
设备管理相关的API路由
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from loguru import logger

from server.security import security_middleware
from server.auth import auth_manager
from server.redis_manager import redis_manager


device_router = APIRouter(prefix="/devices", tags=["设备管理"])


class UpdateDeviceLabelRequest(BaseModel):
    device_id: str
    new_label: str


class RemoveDeviceRequest(BaseModel):
    device_id: str


def success_response(data: Dict[str, Any], status_code: int = 200) -> JSONResponse:
    """返回成功响应"""
    return JSONResponse(content=data, status_code=status_code)


def error_response(message: str, status_code: int = 400) -> JSONResponse:
    """返回错误响应"""
    return JSONResponse(content={"error": message}, status_code=status_code)


@device_router.get("/list")
async def get_devices(req: Request):
    """获取用户的所有设备"""
    try:
        # 认证用户
        user_payload = await security_middleware.authenticate_request(req)
        if not user_payload:
            return error_response("未认证的请求", 401)
        
        user_id = user_payload['user_id']
        username = user_payload['username']
        
        # 获取用户设备列表
        devices = auth_manager.get_user_devices(user_id)
        
        # 格式化设备信息
        device_list = []
        for device in devices:
            device_info = {
                "id": device.id,
                "label": device.label,
                "device_type": device.device_type,
                "os_info": device.os_info,
                "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                "is_current": device.id == user_payload['device_id'],
                "created_at": device.created_at.isoformat() if device.created_at else None
            }
            
            # 检查设备在线状态
            is_online = redis_manager.is_device_online(user_id, device.id)
            device_info["is_online"] = is_online
            
            device_list.append(device_info)
        
        logger.debug(f"获取设备列表: user={username}, count={len(device_list)}")
        
        return success_response({
            "success": True,
            "devices": device_list,
            "total": len(device_list)
        })
        
    except Exception as e:
        logger.error(f"获取设备列表失败: {e}")
        return error_response("获取设备列表失败", 500)


@device_router.put("/update-label")
async def update_device_label(request: UpdateDeviceLabelRequest, req: Request):
    """更新设备标签"""
    try:
        # 认证用户
        user_payload = await security_middleware.authenticate_request(req)
        if not user_payload:
            return error_response("未认证的请求", 401)
        
        user_id = user_payload['user_id']
        username = user_payload['username']
        
        # 验证设备访问权限
        if not security_middleware.validate_device_access(user_payload, request.device_id):
            return error_response("无权限访问该设备", 403)
        
        # 验证标签长度
        if len(request.new_label) > 50:
            return error_response("设备标签长度不能超过50个字符")
        
        # 更新设备标签
        success = auth_manager.update_device_label(
            user_id, 
            request.device_id, 
            request.new_label
        )
        
        if success:
            logger.info(f"设备标签已更新: user={username}, device={request.device_id}, label={request.new_label}")
            return success_response({
                "success": True,
                "message": "设备标签已更新"
            })
        else:
            return error_response("更新设备标签失败，设备不存在或无权限", 404)
            
    except Exception as e:
        logger.error(f"更新设备标签失败: {e}")
        return error_response("更新设备标签失败", 500)


@device_router.delete("/{device_id}")
async def remove_device(device_id: str, req: Request):
    """移除设备"""
    try:
        # 认证用户
        user_payload = await security_middleware.authenticate_request(req)
        if not user_payload:
            return error_response("未认证的请求", 401)
        
        user_id = user_payload['user_id']
        username = user_payload['username']
        current_device_id = user_payload['device_id']
        
        # 不能删除当前设备
        if device_id == current_device_id:
            return error_response("不能删除当前使用的设备")
        
        # 验证设备访问权限
        if not security_middleware.validate_device_access(user_payload, device_id):
            return error_response("无权限访问该设备", 403)
        
        # 移除设备
        success = auth_manager.remove_device(user_id, device_id)
        
        if success:
            # 清理设备相关的Redis数据
            redis_manager.cleanup_device_data(user_id, device_id)
            
            logger.info(f"设备已移除: user={username}, device={device_id}")
            return success_response({
                "success": True,
                "message": "设备已移除"
            })
        else:
            return error_response("移除设备失败，设备不存在或无权限", 404)
            
    except Exception as e:
        logger.error(f"移除设备失败: {e}")
        return error_response("移除设备失败", 500)


@device_router.get("/{device_id}/status")
async def get_device_status(device_id: str, req: Request):
    """获取设备状态"""
    try:
        # 认证用户
        user_payload = await security_middleware.authenticate_request(req)
        if not user_payload:
            return error_response("未认证的请求", 401)
        
        user_id = user_payload['user_id']
        
        # 验证设备访问权限
        if not security_middleware.validate_device_access(user_payload, device_id):
            return error_response("无权限访问该设备", 403)
        
        # 获取设备信息
        device = auth_manager.get_device_by_id(user_id, device_id)
        if not device:
            return error_response("设备不存在", 404)
        
        # 获取设备在线状态
        is_online = redis_manager.is_device_online(user_id, device_id)
        
        # 获取设备统计信息
        stats = redis_manager.get_device_stats(user_id, device_id)
        
        return success_response({
            "success": True,
            "device": {
                "id": device.id,
                "label": device.label,
                "device_type": device.device_type,
                "os_info": device.os_info,
                "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                "is_online": is_online,
                "created_at": device.created_at.isoformat() if device.created_at else None,
                "stats": stats
            }
        })
        
    except Exception as e:
        logger.error(f"获取设备状态失败: {e}")
        return error_response("获取设备状态失败", 500)


@device_router.get("/stats")
async def get_devices_stats(req: Request):
    """获取所有设备的统计信息"""
    try:
        # 认证用户
        user_payload = await security_middleware.authenticate_request(req)
        if not user_payload:
            return error_response("未认证的请求", 401)
        
        user_id = user_payload['user_id']
        
        # 获取用户设备列表
        devices = auth_manager.get_user_devices(user_id)
        
        # 统计信息
        total_devices = len(devices)
        online_devices = 0
        device_types = {}
        
        for device in devices:
            # 检查在线状态
            if redis_manager.is_device_online(user_id, device.id):
                online_devices += 1
            
            # 统计设备类型
            device_type = device.device_type
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        return success_response({
            "success": True,
            "stats": {
                "total_devices": total_devices,
                "online_devices": online_devices,
                "offline_devices": total_devices - online_devices,
                "device_types": device_types
            }
        })
        
    except Exception as e:
        logger.error(f"获取设备统计失败: {e}")
        return error_response("获取设备统计失败", 500) 