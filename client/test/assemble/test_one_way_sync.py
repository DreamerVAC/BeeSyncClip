# 文件：client/test/assemble/test_one_way_sync_cli.py
"""
集成测试用例1：同一用户不同设备单向同步（CLI 版本）
步骤：设备A通过 API 写入“Hello”→设备B通过 API 拉取列表→检查最新内容是否为 “Hello”
"""
import time
import uuid
from client.api.api_manager import APIManager

# ==== 配置区域 ====
BASE_API_URL = "http://47.110.154.99:8000"
USERNAME     = "testuser1"
PASSWORD     = "testpass"
POLL_RETRIES = 10       # 轮询次数
POLL_INTERVAL = 2.0    # 秒
# ===================


def register_user(username):
    print(f"[setup] 注册用户: {username}")
    mgr = APIManager(BASE_API_URL)
    res = mgr.auth.register(username, PASSWORD)
    print(f"[setup] 注册响应: {res}")
    return mgr


def login_device(username, device_label):
    mgr = APIManager(BASE_API_URL)
    device_info = {"device_id": str(uuid.uuid4()), "device_name": f"{device_label}_{username}"}
    print(f"[setup] 登录设备 {device_label} for {username}")
    login_res = mgr.login(username, PASSWORD, device_info)
    assert login_res.get("success"), f"{device_label} 登录失败: {login_res}"
    dev_id = mgr.get_current_device_id()
    print(f"[setup] {device_label} 登录成功, device_id={dev_id}")
    return mgr, username, dev_id


def main():
    # 注册用户（仅需调用一次）
    register_user(USERNAME)
    # 登录两个不同设备
    mgrA, user, devA = login_device(USERNAME, "DeviceA")
    mgrB, _, devB = login_device(USERNAME, "DeviceB")

    print("=== 用例1 CLI：同一用户不同设备单向同步测试开始 ===")
    # 设备A 写入“Hello”
    print(f"[api] 设备A({devA}) 写入剪贴板 'Hello'")
    res = mgrA.clipboard.add_clipboard(user, "Hello", devA)
    assert res.get('success'), f"写入失败: {res}"

    # 设备B 轮询拉取最新内容
    latest = None
    for i in range(POLL_RETRIES):
        print(f"[poll] 第 {i+1} 次拉取列表... (DeviceB={devB})")
        lst = mgrB.clipboard.get_clipboards(user)
        assert lst.get('success'), f"拉取失败: {lst}"
        items = lst.get('clipboards', [])
        if items:
            latest = items[0].get('content')
            print(f"[poll] 当前第一条内容: '{latest}'")
            if latest == "Hello":
                break
        time.sleep(POLL_INTERVAL)

    assert latest == "Hello", f"最终未同步到 'Hello', 实际为 '{latest}'"
    print("=== 用例1 CLI 测试通过 ===")


if __name__ == "__main__":
    main()


