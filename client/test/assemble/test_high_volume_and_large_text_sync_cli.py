# 文件：client/test/assemble/test_high_volume_and_large_text_sync_cli.py
"""
集成测试用例4：大数据量与大文本同步（CLI 版本）
场景：
  1) 设备A依次写入多条内容(200条)
  2) 设备B拉取检查数量
  3) 设备A写入超大文本(100KB)
  4) 设备B验证大文本同步
"""
import time
import uuid
import random
import string
from client.api.api_manager import APIManager

# ==== 配置区域 ====
BASE_API_URL   = "http://47.110.154.99:8000"
USERNAME       = "testuser1"
PASSWORD       = "testpass"
ITEM_COUNT     = 20
LARGE_SIZE     = 100 * 1024  # 100 KB
POLL_RETRIES   = 5
POLL_INTERVAL  = 0.5
# ===================

def setup_user(username):
    print(f"[setup] 注册并登录用户: {username}")
    mgr = APIManager(BASE_API_URL)
    mgr.auth.register(username, PASSWORD)
    device_info = {"device_id": str(uuid.uuid4()), "device_name": f"CLI_{username}"}
    mgr.login(username, PASSWORD, device_info)
    return mgr, username


def random_text(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def main():
    mgrA, user = setup_user(USERNAME)
    mgrB, _    = setup_user(USERNAME)

    print("=== 用例4 CLI：大数据量与大文本同步测试开始 ===")
    # 1) 写入200条随机短文本
    for i in range(1, ITEM_COUNT + 1):
        content = f"item_{i}_" + random_text(10)
        mgrA.clipboard.add_clipboard(user, content, mgrA.get_current_device_id())
        time.sleep(0.1)
        if i % 50 == 0:
            print(f"[write] 已写入 {i}/{ITEM_COUNT} 条")

    # 2) 设备B 拉取并检查数量
    count_ok = False
    for i in range(POLL_RETRIES):
        print(f"[poll] DeviceB 第{i+1}次拉取列表...")
        time.sleep(1)
        resp = mgrB.clipboard.get_clipboards(user)
        # print(resp)
        data = resp.get('clipboards', [])
        print(f"[poll] 当前总条数: {len(data)}")
        if len(data) >= ITEM_COUNT:
            count_ok = True
            break
        time.sleep(POLL_INTERVAL)
    assert count_ok, f"预期至少 {ITEM_COUNT} 条, 实际 {len(data)} 条"

    # 3) 写入100KB大文本
    large_content = random_text(LARGE_SIZE)
    print(f"[api] 写入大文本 ({LARGE_SIZE} 字符)")
    res = mgrA.clipboard.add_clipboard(user, large_content, mgrA.get_current_device_id())
    assert res.get('success'), f"写入大文本失败: {res}"

    # 4) 设备B 验证大文本同步
    synced = False
    for i in range(POLL_RETRIES):
        time.sleep(1)
        print(f"[poll] DeviceB 第{i+1}次拉取列表...")
        resp = mgrB.clipboard.get_clipboards(user)
        data = resp.get('clipboards', [])

        if data and data[0].get('content') == large_content:
            synced = True
            print("[poll] 大文本已同步成功")
            break
        time.sleep(POLL_INTERVAL)
    assert synced, "大文本未正确同步到设备B"
    print("=== 用例4 CLI 测试通过 ===")

if __name__ == "__main__":
    main()
