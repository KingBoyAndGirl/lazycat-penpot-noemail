#!/usr/bin/env python3
"""
Penpot 管理员初始化脚本
通过 PREPL 协议直接在后端创建 admin 账号，绕过邮箱验证。
"""

import json
import socket
import sys
import time

PREPL_HOST = "penpot-backend"
PREPL_PORT = 6063
MAX_RETRIES = 60
RETRY_INTERVAL = 2

ADMIN_FULLNAME = "admin"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "admin123"


def send_prepl(data):
    """发送 PREPL 命令并等待返回结果"""
    s = socket.create_connection((PREPL_HOST, PREPL_PORT), timeout=10)
    try:
        f = s.makefile(mode="rw")
        json.dump(data, f)
        f.write("\n")
        f.flush()

        while True:
            line = f.readline()
            if not line:
                break
            result = json.loads(line)
            tag = result.get("tag", None)

            if tag == "ret":
                val = result.get("val", None)
                err = result.get("err", None)
                if err:
                    print(f"[ERROR] PREPL 命令失败: {err}", file=sys.stderr)
                    return False, err
                return True, val
            elif tag == "out":
                print(f"[PREPL] {result.get('val', '')}", end="")
            else:
                print(f"[WARN] 意外的 PREPL 响应: {result}", file=sys.stderr)
                return False, result
    finally:
        s.close()

    return False, "无响应"


def wait_for_prepl():
    """等待 PREPL 服务就绪"""
    print(f"[INIT] 等待 PREPL 服务 {PREPL_HOST}:{PREPL_PORT} ...")
    for i in range(MAX_RETRIES):
        try:
            ok, _ = send_prepl({"cmd": "echo", "params": {}})
            if ok:
                print(f"[INIT] PREPL 服务就绪 (尝试 {i + 1}/{MAX_RETRIES})")
                return True
        except (ConnectionRefusedError, OSError):
            pass
        time.sleep(RETRY_INTERVAL)
    print(f"[FATAL] PREPL 服务在 {MAX_RETRIES * RETRY_INTERVAL}s 内未就绪", file=sys.stderr)
    return False


def create_admin():
    """创建管理员账号"""
    print(f"[INIT] 创建管理员账号: {ADMIN_EMAIL} / {ADMIN_FULLNAME}")
    ok, val = send_prepl({
        "cmd": "create-profile",
        "params": {
            "fullname": ADMIN_FULLNAME,
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        }
    })
    if ok:
        print(f"[INIT] 管理员账号创建成功: {val}")
        return True
    else:
        print(f"[WARN] 创建失败 (可能已存在): {val}", file=sys.stderr)
        return False


def main():
    if not wait_for_prepl():
        sys.exit(1)
    create_admin()
    print("[INIT] 初始化完成")
    sys.exit(0)


if __name__ == "__main__":
    main()
