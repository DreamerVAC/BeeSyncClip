from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import hashlib
from urllib.parse import parse_qs, urlparse
from typing import Dict, List, Any, Optional
import uuid


class MockServer(BaseHTTPRequestHandler):
    """
    Mock服务器类，处理用户注册、登录、设备管理和剪贴板操作。
    使用类变量存储用户数据、设备信息和剪贴板内容。
    """

    # 使用字典存储用户数据和设备信息
    users: Dict[str, Dict[str, Any]] = {}  # 格式: {username: {'password_hash': str, ...}}
    devices: Dict[str, List[Dict[str, Any]]] = {}  # 格式: {username: [device1_info, device2_info, ...]}
    clipboards: Dict[str, List[Dict[str, Any]]] = {}  # 格式: {username: [clipboard1, clipboard2, ...]}

    # 硬编码测试账号和初始设备
    TEST_USERNAME = "testuser"
    TEST_PASSWORD = "test123"
    TEST_DEVICES = [
        {
            "device_id": "device-001",
            "label": "我的手机",
            "os": "Android",
            "ip_address": "192.168.1.100",
            "first_login": "2023-01-01 10:00:00",
            "last_login": "2023-01-10 15:30:00"
        },
        {
            "device_id": "device-002",
            "label": "我的平板",
            "os": "iOS",
            "ip_address": "192.168.1.101",
            "first_login": "2023-01-05 09:15:00",
            "last_login": "2023-01-09 14:20:00"
        },
        {
            "device_id": "device-003",
            "label": "我的电脑",
            "os": "Windows",
            "ip_address": "192.168.1.102",
            "first_login": "2023-01-08 13:45:00",
            "last_login": "2023-01-10 11:10:00"
        }
    ]

    # 硬编码测试剪贴板内容
    TEST_CLIPBOARDS = [
        {
            "clip_id": str(uuid.uuid4()),
            "content": "这是一条重要的笔记",
            "content_type": "text/plain",
            "created_at": "2023-01-01 10:00:00",
            "last_modified": "2023-01-02 11:00:00",
            "device_id": "device-001"
        },
        {
            "clip_id": str(uuid.uuid4()),
            "content": "https://example.com",
            "content_type": "text/uri-list",
            "created_at": "2023-01-03 14:00:00",
            "last_modified": "2023-01-03 14:00:00",
            "device_id": "device-002"
        },
        {
            "clip_id": str(uuid.uuid4()),
            "content": "购物清单:\n1. 牛奶\n2. 面包\n3. 鸡蛋",
            "content_type": "text/plain",
            "created_at": "2023-01-05 09:00:00",
            "last_modified": "2023-01-05 09:15:00",
            "device_id": "device-003"
        },
        {
            "clip_id": str(uuid.uuid4()),
            "content": "会议时间: 明天下午3点",
            "content_type": "text/plain",
            "created_at": "2023-01-07 13:00:00",
            "last_modified": "2023-01-07 13:00:00",
            "device_id": "device-001"
        },
        {
            "clip_id": str(uuid.uuid4()),
            "content": "项目截止日期: 2023-01-15",
            "content_type": "text/plain",
            "created_at": "2023-01-08 10:00:00",
            "last_modified": "2023-01-09 16:00:00",
            "device_id": "device-002"
        }
    ]

    def __init__(self, *args, **kwargs):
        # 初始化测试账号
        self._init_test_account()
        super().__init__(*args, **kwargs)

    def _init_test_account(self):
        """初始化测试账号"""
        if self.TEST_USERNAME not in self.users:
            # 创建测试用户
            self.users[self.TEST_USERNAME] = {
                'password_hash': self._hash_password(self.TEST_PASSWORD),
                'created_at': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            # 初始化测试设备
            self.devices[self.TEST_USERNAME] = self.TEST_DEVICES.copy()
            # 初始化测试剪贴板内容
            self.clipboards[self.TEST_USERNAME] = self.TEST_CLIPBOARDS.copy()

    def _set_response(self, status_code: int = 200) -> None:
        """设置HTTP响应头"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _hash_password(self, password: str) -> str:
        """使用SHA-256哈希密码"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def _validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> Optional[Dict[str, Any]]:
        """验证输入数据是否包含必需字段"""
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "success": False,
                "message": f"缺少必需字段: {', '.join(missing_fields)}",
                "status": 400
            }
        return None

    def _get_request_data(self) -> Dict[str, Any]:
        """从请求中获取JSON数据"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}

        try:
            post_data = self.rfile.read(content_length)
            return json.loads(post_data)
        except json.JSONDecodeError:
            return {}

    def _error_response(self, message: str, status_code: int = 400) -> None:
        """发送错误响应"""
        self._set_response(status_code)
        response = {
            "success": False,
            "message": message,
            "status": status_code
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self) -> None:
        """
        处理POST请求:
        - /login: 用户登录
        - /register: 用户注册
        - /update_device_label: 更新设备标签
        - /remove_device: 删除设备
        - /add_clipboard: 添加剪贴板内容
        - /delete_clipboard: 删除剪贴板内容
        - /clear_clipboards: 清空所有剪贴板内容
        """
        try:
            data = self._get_request_data()

            if self.path == '/login':
                self._handle_login(data)
            elif self.path == '/register':
                self._handle_register(data)
            elif self.path == '/update_device_label':
                self._handle_update_device_label(data)
            elif self.path == '/remove_device':
                self._handle_remove_device(data)
            elif self.path == '/add_clipboard':
                self._handle_add_clipboard(data)
            elif self.path == '/delete_clipboard':
                self._handle_delete_clipboard(data)
            elif self.path == '/clear_clipboards':
                self._handle_clear_clipboards(data)
            else:
                self._error_response("未知的API端点", 404)

        except Exception as e:
            self._error_response(f"服务器错误: {str(e)}", 500)

    def _handle_login(self, data: Dict[str, Any]) -> None:
        """处理登录请求"""
        # 验证输入
        error = self._validate_input(data, ['username', 'password', 'device_info'])
        if error:
            self._set_response(error['status'])
            self.wfile.write(json.dumps(error).encode('utf-8'))
            return

        username = data['username']
        password_hash = self._hash_password(data['password'])
        device_info = data['device_info']

        # 检查用户是否存在且密码匹配
        if username in self.users and self.users[username]['password_hash'] == password_hash:
            # 确保设备信息包含device_id
            if 'device_id' not in device_info:
                self._error_response("设备信息缺少device_id", 400)
                return

            # 初始化设备列表（如果不存在）
            if username not in self.devices:
                self.devices[username] = []

            # 查找或创建设备
            device = next((d for d in self.devices[username]
                           if d.get('device_id') == device_info['device_id']), None)

            current_time = time.strftime("%Y-%m-%d %H:%M:%S")

            if device:
                # 更新现有设备
                device.update({
                    'last_login': current_time,
                    **{k: v for k, v in device_info.items() if k not in ['device_id']}
                })
            else:
                # 添加新设备
                new_device = {
                    'device_id': device_info['device_id'],
                    'label': device_info.get('label', f"设备{len(self.devices[username]) + 1}"),
                    'last_login': current_time,
                    'first_login': current_time,
                    **{k: v for k, v in device_info.items() if k not in ['device_id', 'label']}
                }
                self.devices[username].append(new_device)
                device = new_device

            response = {
                "success": True,
                "message": "登录成功",
                "token": "mock_token",
                "device_id": device_info['device_id'],
                "devices": self.devices[username],
                "current_device": device,
                "clipboards": self.clipboards.get(username, [])
            }
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self._error_response("用户名或密码错误", 401)

    def _handle_register(self, data: Dict[str, Any]) -> None:
        """处理注册请求"""
        # 验证输入
        error = self._validate_input(data, ['username', 'password'])
        if error:
            self._set_response(error['status'])
            self.wfile.write(json.dumps(error).encode('utf-8'))
            return

        username = data['username']
        password_hash = self._hash_password(data['password'])

        # 检查用户名是否已存在
        if username in self.users:
            self._error_response("用户名已存在", 409)
            return

        # 存储用户信息
        self.users[username] = {
            'password_hash': password_hash,
            'created_at': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.devices[username] = []  # 初始化设备列表
        self.clipboards[username] = []  # 初始化剪贴板列表

        response = {
            "success": True,
            "message": "注册成功",
            "user_count": len(self.users),
            "username": username
        }
        self._set_response(201)  # 201 Created
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def _handle_update_device_label(self, data: Dict[str, Any]) -> None:
        """处理更新设备标签请求"""
        # 验证输入
        error = self._validate_input(data, ['username', 'device_id', 'new_label'])
        if error:
            self._set_response(error['status'])
            self.wfile.write(json.dumps(error).encode('utf-8'))
            return

        username = data['username']
        device_id = data['device_id']
        new_label = data['new_label']

        if username not in self.devices:
            self._error_response("用户未找到", 404)
            return

        # 查找设备
        device = next((d for d in self.devices[username]
                       if d.get('device_id') == device_id), None)

        if device:
            device['label'] = new_label
            response = {
                "success": True,
                "message": "设备标签更新成功",
                "device_id": device_id,
                "new_label": new_label
            }
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self._error_response("设备未找到", 404)

    def _handle_remove_device(self, data: Dict[str, Any]) -> None:
        """处理删除设备请求 - 同时删除相关剪贴板记录"""
        # 验证输入
        error = self._validate_input(data, ['username', 'device_id'])
        if error:
            self._set_response(error['status'])
            self.wfile.write(json.dumps(error).encode('utf-8'))
            return

        username = data['username']
        device_id = data['device_id']

        if username not in self.devices:
            self._error_response("用户未找到", 404)
            return

        # 查找并删除设备
        device_found = False
        for i, device in enumerate(self.devices[username]):
            if device.get('device_id') == device_id:
                self.devices[username].pop(i)
                device_found = True
                break

        if not device_found:
            self._error_response("设备未找到", 404)
            return

        # 删除该设备的所有剪贴板记录
        removed_clip_count = 0
        if username in self.clipboards:
            # 只保留不是该设备的记录
            original_count = len(self.clipboards[username])
            self.clipboards[username] = [
                clip for clip in self.clipboards[username]
                if clip.get('device_id') != device_id
            ]
            removed_clip_count = original_count - len(self.clipboards[username])

        response = {
            "success": True,
            "message": "设备删除成功",
            "device_id": device_id,
            "removed_clip_count": removed_clip_count
        }
        self._set_response()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def _handle_add_clipboard(self, data: Dict[str, Any]) -> None:
        """处理添加剪贴板内容请求"""
        # 验证输入
        error = self._validate_input(data, ['username', 'content', 'device_id'])
        if error:
            self._set_response(error['status'])
            self.wfile.write(json.dumps(error).encode('utf-8'))
            return

        username = data['username']
        content = data['content']
        device_id = data['device_id']
        content_type = data.get('content_type', 'text/plain')

        if username not in self.clipboards:
            self._error_response("用户未找到", 404)
            return

        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        new_clip = {
            "clip_id": str(uuid.uuid4()),
            "content": content,
            "content_type": content_type,
            "created_at": current_time,
            "last_modified": current_time,
            "device_id": device_id
        }

        self.clipboards[username].append(new_clip)

        response = {
            "success": True,
            "message": "剪贴板内容添加成功",
            "clip_id": new_clip["clip_id"],
            "clipboards": self.clipboards[username]
        }
        self._set_response(201)  # 201 Created
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def _handle_delete_clipboard(self, data: Dict[str, Any]) -> None:
        """处理删除剪贴板内容请求"""
        # 验证输入
        error = self._validate_input(data, ['username', 'clip_id'])
        if error:
            self._set_response(error['status'])
            self.wfile.write(json.dumps(error).encode('utf-8'))
            return

        username = data['username']
        clip_id = data['clip_id']

        if username not in self.clipboards:
            self._error_response("用户未找到", 404)
            return

        # 查找并删除剪贴板内容
        for i, clip in enumerate(self.clipboards[username]):
            if clip.get('clip_id') == clip_id:
                # 记录被删除的内容用于日志
                deleted_content = clip['content'][:50] + "..." if len(clip['content']) > 50 else clip['content']

                self.clipboards[username].pop(i)
                response = {
                    "success": True,
                    "message": f"剪贴板内容删除成功: '{deleted_content}'",
                    "clip_id": clip_id,
                    "remaining_clips": len(self.clipboards[username])
                }
                self._set_response()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

        self._error_response("剪贴板内容未找到", 404)

    def _handle_clear_clipboards(self, data: Dict[str, Any]) -> None:
        """处理清空所有剪贴板内容请求"""
        # 验证输入
        error = self._validate_input(data, ['username'])
        if error:
            self._set_response(error['status'])
            self.wfile.write(json.dumps(error).encode('utf-8'))
            return

        username = data['username']

        if username not in self.clipboards:
            self._error_response("用户未找到", 404)
            return

        # 清空剪贴板
        deleted_count = len(self.clipboards[username])
        self.clipboards[username] = []

        response = {
            "success": True,
            "message": "剪贴板已清空",
            "deleted_count": deleted_count
        }
        self._set_response()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_GET(self) -> None:
        """
        处理GET请求:
        - /get_devices: 获取用户设备列表
        - /get_clipboards: 获取用户剪贴板内容
        """
        try:
            if self.path.startswith('/get_devices'):
                # 解析查询参数
                query = parse_qs(urlparse(self.path).query)
                username = query.get('username', [''])[0]

                if not username:
                    self._error_response("缺少username参数", 400)
                    return

                if username in self.devices:
                    response = {
                        "success": True,
                        "devices": self.devices[username],
                        "count": len(self.devices[username])
                    }
                    self._set_response()
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self._error_response("用户未找到", 404)
            elif self.path.startswith('/get_clipboards'):
                # 解析查询参数
                query = parse_qs(urlparse(self.path).query)
                username = query.get('username', [''])[0]

                if not username:
                    self._error_response("缺少username参数", 400)
                    return

                if username in self.clipboards:
                    response = {
                        "success": True,
                        "clipboards": self.clipboards[username],
                        "count": len(self.clipboards[username])
                    }
                    self._set_response()
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self._error_response("用户未找到", 404)
            else:
                self._error_response("未知的API端点", 404)

        except Exception as e:
            self._error_response(f"服务器错误: {str(e)}", 500)


def run(server_class=HTTPServer, handler_class=MockServer, port=8000) -> None:
    """启动HTTP服务器"""
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'启动模拟服务器，端口 {port}...')
    print(f'测试账号: {MockServer.TEST_USERNAME}')
    print(f'测试密码: {MockServer.TEST_PASSWORD}')
    print('初始设备列表:')
    for device in MockServer.TEST_DEVICES:
        print(f"  - {device['label']} (ID: {device['device_id']})")
    print('初始剪贴板内容:')
    for clip in MockServer.TEST_CLIPBOARDS:
        print(f"  - ID: {clip['clip_id']}")
        print(f"    内容: {clip['content']}")
        print(f"    类型: {clip['content_type']}")
        print(f"    设备ID: {clip['device_id']}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器正在关闭...")
        httpd.server_close()


if __name__ == '__main__':
    run()