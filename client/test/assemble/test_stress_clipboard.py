#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量多用户压力测试脚本（含注册）
场景：先批量注册 testuser1…testuser100，再登录各设备并发写入剪贴板，统计延迟。
"""
import time
import uuid
import random
import string
from concurrent.futures import ThreadPoolExecutor, as_completed
from client.api.api_manager import APIManager

# —— 配置区域 —— #
BASE_URL         = "http://47.110.154.99:8000"  # 后端服务地址
USERNAME_PREFIX  = "testuser"                   # 账号名前缀
PASSWORD         = "testpass"                   # 统一密码
TOTAL_USERS      = 100                          # 注册数量：testuser1…testuser100
CONCURRENCY      = 50                           # 并发线程数
REQUESTS_PER_JOB = 100                          # 每线程写入次数
# —————————— #

def random_text(length=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def worker(manager: APIManager, username: str, device_id: str, n: int):
    latencies = []
    successes = 0
    for _ in range(n):
        content = random_text(50)
        t0 = time.time()
        resp = manager.clipboard.add_clipboard(username, content, device_id)
        t1 = time.time()
        latencies.append((t1 - t0) * 1000)
        if resp.get("success"):
            successes += 1
    # 最后拉取列表
    manager.clipboard.get_clipboards(username)
    return successes, latencies

if __name__ == "__main__":
    # 1. 批量注册
    print(f"开始批量注册 {TOTAL_USERS} 个用户…")
    for i in range(1, TOTAL_USERS + 1):
        time.sleep(1)
        username = f"{USERNAME_PREFIX}{i}"
        mgr_reg = APIManager(BASE_URL)
        res = mgr_reg.auth.register(username, PASSWORD)
        if res.get("success"):
            print(f"[OK] 注册成功：{username}")
        else:
            msg = res.get("message")
            print(f"[WARN] 注册失败{username}：{msg}")
    print("注册阶段结束\n")

    time.sleep(2)
    # 2. 批量登录
    logged_in = []
    print(f"开始登录用户…")
    for i in range(1, TOTAL_USERS + 1):
        time.sleep(1)
        username = f"{USERNAME_PREFIX}{i}"
        mgr = APIManager(BASE_URL)
        device_info = {"device_id": str(uuid.uuid4()), "device_name": f"Device_{username}"}
        res = mgr.login(username, PASSWORD, device_info)
        # print(res)
        if res.get("success"):
            dev = "Testdevice{i}"
            logged_in.append((mgr, username, dev))
            print(f"[OK] 登录成功：{username} (device_id={dev})")
        else:
            print(f"[WARN] 登录失败：{username} -> {res.get('message')}")
    if not logged_in:
        print("无可用账号，退出测试。")
        exit(1)

    print(f"共 {len(logged_in)} 个账号可用，开始并发压力测试…\n")

    # 3. 并发压测
    all_latencies = []
    total_success = 0
    start = time.time()
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = []
        for idx in range(CONCURRENCY):
            mgr, user, dev = logged_in[idx % len(logged_in)]
            futures.append(executor.submit(worker, mgr, user, dev, REQUESTS_PER_JOB))
        for fut in as_completed(futures):
            succ, lats = fut.result()
            total_success += succ
            all_latencies.extend(lats)
    duration = time.time() - start

    # 4. 结果统计
    count = len(all_latencies)
    avg   = sum(all_latencies) / count if count else 0
    sorted_l = sorted(all_latencies)
    p50   = sorted_l[int(0.50 * count)]
    p95   = sorted_l[int(0.95 * count)]
    p99   = sorted_l[int(0.99 * count)]

    print("—— 多用户压力测试结果 ——")
    print(f"总账号数       : {len(logged_in)}")
    print(f"并发线程数     : {CONCURRENCY}")
    print(f"每线程请求数   : {REQUESTS_PER_JOB}")
    print(f"总请求数       : {CONCURRENCY * REQUESTS_PER_JOB}")
    print(f"写入成功次数   : {total_success}")
    print(f"总耗时         : {duration:.2f}s")
    print(f"平均延时(写)   : {avg:.2f}ms")
    print(f"P50 延时       : {p50:.2f}ms")
    print(f"P95 延时       : {p95:.2f}ms")
    print(f"P99 延时       : {p99:.2f}ms")
