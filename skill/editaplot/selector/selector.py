#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图表选择器：打开选图页面，收下用户选的结果。

用户说不清自己要画什么图的时候用这个。它做两件事：

1. 打开 chart-selector.html —— 45 张实机示例图铺开，点一张就行
2. 起一个只监听本机的小服务，用户在页面上点「发送给豆包」时把拼好的提示词收下来

页面永远会先把提示词放进用户的剪贴板，所以就算这个服务没起来、端口被占，
用户也能自己粘贴 —— 这条路不会断。

    python selector.py                 # 开页面，等用户选，把结果打到标准输出
    python selector.py --print-path    # 只打印页面路径，不开窗口（宿主自带浏览器面板时用）
    python selector.py --timeout 900   # 等多久放弃（默认 600 秒）
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = HERE / "chart-selector.html"

# 必须和页面里的 PORTS 一致；页面会同时试这几个，撞端口也不至于卡死
PORTS = [17864, 17865, 17866]

# 1×1 透明 GIF：页面用 <img> 发请求，回一张真图片才能让它判定成功
PIXEL = base64.b64decode(b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
MAX_BODY = 64 * 1024


class _Handler(BaseHTTPRequestHandler):
    result: dict = {}

    def _reply(self, code: int) -> None:
        self.send_response(code)
        self.send_header("Content-Type", "image/gif")
        self.send_header("Content-Length", str(len(PIXEL)))
        # 页面可能是 file:// 打开的，来源序列化成 null，必须放开才收得到
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(PIXEL)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/pick":
            self._reply(404)
            return
        text = urllib.parse.parse_qs(parsed.query).get("d", [""])[0]
        if not text.strip():
            self._reply(400)
            return
        if len(text.encode("utf-8")) > MAX_BODY:
            self._reply(413)
            return
        self._reply(200)
        _Handler.result["prompt"] = text
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, *args) -> None:
        pass


def _open_in_browser(path: Path) -> bool:
    """用系统默认方式打开页面。打不开也不算失败——把路径给用户就行。"""
    try:
        if sys.platform == "win32":
            os.startfile(str(path))  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=True)
        else:
            subprocess.run(["xdg-open", str(path)], check=True)
        return True
    except Exception:
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="打开科研配图选择器并接收用户的选择")
    ap.add_argument("--print-path", action="store_true",
                    help="只打印页面路径，不自己开窗口（宿主有内置浏览器面板时用这个）")
    ap.add_argument("--timeout", type=float, default=600.0, help="等待用户选择的秒数")
    ap.add_argument("--json", action="store_true", help="结果按 JSON 输出")
    a = ap.parse_args(argv)

    if not PAGE.exists():
        print(f"找不到选择器页面：{PAGE}", file=sys.stderr)
        return 1

    if a.print_path:
        print(PAGE)
        return 0

    server = None
    for port in PORTS:
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
            break
        except OSError:
            continue

    print(f"选择器页面：{PAGE}", flush=True)
    if server is None:
        # 端口全被占也不致命：用户仍可在页面上点「复制」，自己粘回来
        print("提示：本机候选端口都被占了，一键发送用不了。"
              "请在页面上点「复制」，再把内容粘给我。", flush=True)
        _open_in_browser(PAGE)
        return 2

    opened = _open_in_browser(PAGE)
    if not opened:
        print("没能自动打开浏览器。请手动双击上面这个文件。", flush=True)
    print(f"正在等你选图（最多 {a.timeout:.0f} 秒）…", flush=True)

    threading.Timer(a.timeout, server.shutdown).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

    prompt = _Handler.result.get("prompt")
    if not prompt:
        print("没等到选择。用户可能直接点了「复制」——问他一句，"
              "或者让他把复制的内容粘过来。", flush=True)
        return 3

    if a.json:
        print(json.dumps({"ok": True, "prompt": prompt}, ensure_ascii=False))
    else:
        print("\n---- 用户选好了 ----")
        print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
