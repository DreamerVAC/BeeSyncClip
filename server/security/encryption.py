"""
加密管理器
提供AES加密/解密、RSA密钥交换、数据签名等功能
"""

import os
import base64
import hashlib
from typing import Optional, Tuple, Dict, Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from loguru import logger
import json
import time


class EncryptionManager:
    """加密管理器"""
    
    def __init__(self, key_size: int = 32):
        """
        初始化加密管理器
        
        Args:
            key_size: AES密钥长度（32字节=256位）
        """
        self.key_size = key_size
        self.backend = default_backend()
        
        # 生成服务器RSA密钥对
        self._generate_server_keypair()
        
        # 用户会话密钥缓存
        self.user_session_keys: Dict[str, bytes] = {}
        
        logger.info("加密管理器初始化完成")
    
    def _generate_server_keypair(self):
        """生成服务器RSA密钥对"""
        try:
            self.server_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=self.backend
            )
            self.server_public_key = self.server_private_key.public_key()
            logger.info("服务器RSA密钥对生成完成")
        except Exception as e:
            logger.error(f"生成RSA密钥对失败: {e}")
            raise
    
    def get_server_public_key_pem(self) -> str:
        """获取服务器公钥（PEM格式）"""
        try:
            pem = self.server_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return pem.decode('utf-8')
        except Exception as e:
            logger.error(f"获取服务器公钥失败: {e}")
            raise
    
    def generate_session_key(self, user_id: str) -> bytes:
        """为用户生成会话密钥"""
        try:
            session_key = os.urandom(self.key_size)
            self.user_session_keys[user_id] = session_key
            logger.debug(f"为用户 {user_id} 生成会话密钥")
            return session_key
        except Exception as e:
            logger.error(f"生成会话密钥失败: {e}")
            raise
    
    def get_session_key(self, user_id: str) -> Optional[bytes]:
        """获取用户会话密钥"""
        return self.user_session_keys.get(user_id)
    
    def remove_session_key(self, user_id: str):
        """移除用户会话密钥"""
        self.user_session_keys.pop(user_id, None)
        logger.debug(f"移除用户 {user_id} 的会话密钥")
    
    def decrypt_with_server_key(self, encrypted_data: str) -> bytes:
        """使用服务器私钥解密数据（用于密钥交换）"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data)
            decrypted = self.server_private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted
        except Exception as e:
            logger.error(f"RSA解密失败: {e}")
            raise
    
    def encrypt_with_session_key(self, data: str, user_id: str) -> str:
        """使用会话密钥加密数据"""
        try:
            session_key = self.get_session_key(user_id)
            if not session_key:
                raise ValueError(f"用户 {user_id} 没有有效的会话密钥")
            
            # 生成随机IV
            iv = os.urandom(16)
            
            # AES-256-CBC加密
            cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            
            # 填充数据到16字节边界
            data_bytes = data.encode('utf-8')
            padding_length = 16 - (len(data_bytes) % 16)
            padded_data = data_bytes + (bytes([padding_length]) * padding_length)
            
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # 组合IV和加密数据
            result = iv + encrypted_data
            return base64.b64encode(result).decode('utf-8')
            
        except Exception as e:
            logger.error(f"AES加密失败: {e}")
            raise
    
    def decrypt_with_session_key(self, encrypted_data: str, user_id: str) -> str:
        """使用会话密钥解密数据"""
        try:
            session_key = self.get_session_key(user_id)
            if not session_key:
                raise ValueError(f"用户 {user_id} 没有有效的会话密钥")
            
            # 解码base64
            data = base64.b64decode(encrypted_data)
            
            # 分离IV和加密数据
            iv = data[:16]
            encrypted_data = data[16:]
            
            # AES-256-CBC解密
            cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            
            decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # 移除填充
            padding_length = decrypted_padded[-1]
            decrypted_data = decrypted_padded[:-padding_length]
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            logger.error(f"AES解密失败: {e}")
            raise
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        """
        哈希密码
        
        Returns:
            Tuple[str, str]: (hashed_password, salt)
        """
        try:
            if salt is None:
                salt = os.urandom(32)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=self.backend
            )
            
            hashed = kdf.derive(password.encode('utf-8'))
            
            return (
                base64.b64encode(hashed).decode('utf-8'),
                base64.b64encode(salt).decode('utf-8')
            )
            
        except Exception as e:
            logger.error(f"密码哈希失败: {e}")
            raise
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """验证密码"""
        try:
            salt_bytes = base64.b64decode(salt)
            expected_hash = base64.b64decode(hashed_password)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_bytes,
                iterations=100000,
                backend=self.backend
            )
            
            try:
                kdf.verify(password.encode('utf-8'), expected_hash)
                return True
            except Exception:
                return False
                
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False
    
    def create_data_signature(self, data: str) -> str:
        """创建数据签名"""
        try:
            data_bytes = data.encode('utf-8')
            signature = self.server_private_key.sign(
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            logger.error(f"创建数据签名失败: {e}")
            raise
    
    def encrypt_clipboard_content(self, content: str, user_id: str) -> Dict[str, Any]:
        """
        加密剪切板内容
        
        Returns:
            包含加密内容和元数据的字典
        """
        try:
            encrypted_content = self.encrypt_with_session_key(content, user_id)
            
            # 创建内容哈希用于完整性检查
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            return {
                'encrypted_content': encrypted_content,
                'content_hash': content_hash,
                'encryption_method': 'AES-256-CBC',
                'timestamp': str(int(time.time()))
            }
            
        except Exception as e:
            logger.error(f"加密剪切板内容失败: {e}")
            raise
    
    def decrypt_clipboard_content(self, encrypted_data: Dict[str, Any], user_id: str) -> str:
        """
        解密剪切板内容
        
        Args:
            encrypted_data: 包含加密内容和元数据的字典
            user_id: 用户ID
            
        Returns:
            解密后的内容
        """
        try:
            encrypted_content = encrypted_data.get('encrypted_content')
            expected_hash = encrypted_data.get('content_hash')
            
            if not encrypted_content:
                raise ValueError("缺少加密内容")
            
            # 解密内容
            decrypted_content = self.decrypt_with_session_key(encrypted_content, user_id)
            
            # 验证内容完整性
            if expected_hash:
                actual_hash = hashlib.sha256(decrypted_content.encode('utf-8')).hexdigest()
                if actual_hash != expected_hash:
                    raise ValueError("内容完整性验证失败")
            
            return decrypted_content
            
        except Exception as e:
            logger.error(f"解密剪切板内容失败: {e}")
            raise


# 全局加密管理器实例
encryption_manager = EncryptionManager() 