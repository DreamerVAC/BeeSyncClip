# 文件：client/test/assemble/test_offline_recovery_sync_cli.py
"""
集成测试用例3：同一用户不同设备断网后恢复同步（CLI 版本）
步骤：设备A模拟离线复制“123”，恢复网络后重试→设备B拉取列表验证内容为“123”
"""
import time
import uuid
from client.api.api_manager import APIManager

# ==== 配置区域 ====
BASE_API_URL = "http://47.110.154.99:8000"
USERNAME     = "testuser1"
PASSWORD     = "testpass"
POLL_RETRIES = 5
POLL_INTERVAL = 1.0
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
    # 注册用户（仅需一次）
    register_user(USERNAME)
    # 登录两个不同设备
    mgrA, user, devA = login_device(USERNAME, "DeviceA")
    mgrB, _, devB = login_device(USERNAME, "DeviceB")

    print("=== 用例3 CLI：同一用户不同设备断网后恢复同步测试开始 ===")
    # 模拟断网：忽略写入异常
    try:
        print(f"[api] 模拟离线状态写入 '123' (DeviceA={devA})")
        mgrA.clipboard.add_clipboard(user, "123", devA)
    except Exception as e:
        print(f"[api] 离线写入异常（预期）：{e}")

    # 恢复网络后重试写入
    print(f"[api] 恢复网络后重试写入 '123' (DeviceA={devA})")
    res = mgrA.clipboard.add_clipboard(user, "123", devA)
    assert res.get('success'), f"重试写入失败: {res}"

    # 设备B 轮询拉取验证
    latest = None
    for i in range(POLL_RETRIES):
        print(f"[poll] 第 {i+1} 次拉取列表... (DeviceB={devB})")
        lst = mgrB.clipboard.get_clipboards(user)
        assert lst.get('success'), f"拉取失败: {lst}"
        items = lst.get('clipboards', [])
        if items:
            latest = items[0].get('content')
            print(f"[poll] 当前第一条内容: '{latest}'")
            if latest == "123":
                break
        time.sleep(POLL_INTERVAL)

    assert latest == "123", f"最终未同步到 '123', 实际为 '{latest}'"
    print("=== 用例3 CLI 测试通过 ===")


if __name__ == "__main__":
    main()
