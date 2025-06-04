"""
BeeSyncClip 共享工具函数
"""

import hashlib
import platform
import socket
import base64
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import psutil
from loguru import logger


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = Path(config_path)
        self._config = None
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if not self.config_path.exists():
                logger.warning(f"配置文件不存在: {self.config_path}")
                return {}
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
                logger.info(f"已加载配置文件: {self.config_path}")
                return self._config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的嵌套键"""
        if not self._config:
            return default
        
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        if not self._config:
            self._config = {}
        
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            logger.info(f"配置已保存到: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False


class CryptoHelper:
    """加密解密助手"""
    
    def __init__(self, password: str):
        self.password = password.encode()
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)
    
    def _derive_key(self) -> bytes:
        """从密码派生密钥"""
        salt = b'BeeSyncClip_Salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key
    
    def encrypt(self, data: str) -> str:
        """加密数据"""
        try:
            encrypted_data = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"加密失败: {e}")
            return data
    
    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"解密失败: {e}")
            return encrypted_data


def get_device_info() -> Dict[str, str]:
    """获取设备信息"""
    try:
        system_info = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': socket.gethostname(),
            'processor': platform.processor(),
        }
        
        try:
            system_info['cpu_count'] = str(psutil.cpu_count())
            memory = psutil.virtual_memory()
            system_info['memory_total'] = str(memory.total)
        except:
            pass
        
        device_string = f"{system_info['hostname']}-{system_info['platform']}-{system_info['architecture']}"
        system_info['device_id'] = hashlib.md5(device_string.encode()).hexdigest()
        
        return system_info
    
    except Exception as e:
        logger.error(f"获取设备信息失败: {e}")
        return {
            'platform': 'Unknown',
            'hostname': 'Unknown',
            'device_id': 'unknown-device'
        }


def calculate_checksum(data: str) -> str:
    """计算数据校验和"""
    return hashlib.sha256(data.encode()).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def ensure_directory(path: str) -> bool:
    """确保目录存在"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录失败 {path}: {e}")
        return False


def get_local_ip() -> str:
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


# 全局配置管理器实例
config_manager = ConfigManager() 