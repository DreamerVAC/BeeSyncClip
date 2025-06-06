#!/usr/bin/env python3
"""
BeeSyncClip 服务器诊断脚本
"""

import socket
import time
import requests
from urllib.parse import urlparse

def check_port_open(host, port):
    """检查端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        return False

def check_http_service(url):
    """检查HTTP服务响应"""
    try:
        # 尝试原始HTTP请求
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port or 80
        
        sock.connect((host, port))
        
        # 发送HTTP请求
        request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        sock.send(request.encode())
        
        response = sock.recv(4096).decode()
        sock.close()
        
        return response
    except Exception as e:
        return f"错误: {e}"

def diagnose_server():
    """诊断服务器状态"""
    server_host = "47.110.154.99"
    server_port = 8000
    server_url = f"http://{server_host}:{server_port}"
    
    print("🔍 BeeSyncClip 服务器诊断")
    print("="*60)
    
    # 1. 检查端口连通性
    print(f"1. 检查端口连通性 {server_host}:{server_port}")
    port_open = check_port_open(server_host, server_port)
    print(f"   结果: {'✅ 端口开放' if port_open else '❌ 端口关闭'}")
    
    # 2. 检查HTTP服务
    print(f"\n2. 检查HTTP服务响应")
    http_response = check_http_service(server_url)
    print(f"   原始HTTP响应:")
    print(f"   {http_response[:300]}...")
    
    # 3. 分析响应头
    if "HTTP" in http_response:
        lines = http_response.split('\n')
        status_line = lines[0] if lines else ""
        print(f"\n3. HTTP状态行: {status_line}")
        
        # 检查状态码
        if "503" in status_line:
            print("   ⚠️ HTTP 503 服务不可用")
            print("   可能原因:")
            print("   - FastAPI应用启动失败")
            print("   - Redis连接问题")
            print("   - 配置文件错误")
            print("   - 依赖服务未就绪")
        elif "200" in status_line:
            print("   ✅ HTTP 200 服务正常")
        else:
            print(f"   ❓ 未知状态: {status_line}")
    
    # 4. 建议解决方案
    print(f"\n4. 建议解决方案:")
    print("   1. 检查服务器日志: tail -f logs/beesyncclip.log")
    print("   2. 检查Redis服务: redis-cli ping")
    print("   3. 检查配置文件: config/config.yaml")
    print("   4. 重启服务器进程")
    print("   5. 检查依赖服务状态")
    
    # 5. 测试命令
    print(f"\n5. 服务器端测试命令:")
    print(f"   # 检查进程")
    print(f"   ps aux | grep python")
    print(f"   # 检查端口占用")
    print(f"   netstat -tlnp | grep 8000")
    print(f"   # 本地测试")
    print(f"   curl -v http://localhost:8000/health")

if __name__ == "__main__":
    diagnose_server() 