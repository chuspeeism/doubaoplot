#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图表选择器：把选图页面挂在本机地址上，收下用户选的结果。

用户说不清自己要画什么图的时候用这个。它做两件事：

1. 起一个只监听本机的小服务，把 chart-selector.html 挂在 http://127.0.0.1:<端口>/ 上
   —— 45 张实机示例图铺开，点一张就行
2. 用户在页面上点「发送给豆包」时，把拼好的提示词收下来

**默认不弹任何浏览器窗口。** 它只把地址打出来，由宿主（豆包工作等）用自己的内置浏览器打开。
上一版默认调系统默认浏览器，结果每次都弹一个 Chrome 窗口，用户还得再说一句
「在豆包内置浏览器打开」—— 所以现在开窗口必须显式加 --open。

页面永远会先把提示词放进用户的剪贴板，所以就算这个服务没起来、端口被占，
用户也能自己粘贴 —— 这条路不会断。

    python selector.py                 # 挂上页面，打印地址，等用户选（默认不开窗口）
    python selector.py --open          # 顺便用系统默认浏览器打开（宿主没有内置浏览器时才用）
    python selector.py --print-path    # 只打印页面文件路径，不起服务
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
PAGE_ROUTES = {"/", "/index.html", "/chart-selector.html"}


class _Handler(BaseHTTPRequestHandler):
    result: dict = {}
    page_bytes: bytes = b""

    def _reply(self, code: int) -> None:
        self.send_response(code)
        self.send_header("Content-Type", "image/gif")
        self.send_header("Content-Length", str(len(PIXEL)))
        # 页面也可能是 file:// 打开的，来源序列化成 null，必须放开才收得到
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(PIXEL)

    def _serve_page(self) -> None:
        body = _Handler.page_bytes
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in PAGE_ROUTES and _Handler.page_bytes:
            self._serve_page()
            return
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


def _open_in_browser(target: str) -> bool:
    """用系统默认方式打开地址或文件。打不开也不算失败——把地址给用户就行。"""
    try:
        if sys.platform == "win32":
            os.startfile(target)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", target], check=True)
        else:
            subprocess.run(["xdg-open", target], check=True)
        return True
    except Exception:
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="打开科研配图选择器并接收用户的选择")
    ap.add_argument("--print-path", action="store_true",
                    help="只打印页面文件路径，不起服务、不开窗口")
    ap.add_argument("--open", action="store_true", dest="open_browser",
                    help="额外用系统默认浏览器打开（宿主没有内置浏览器面板时才加这个）")
    ap.add_argument("--timeout", type=float, default=600.0, help="等待用户选择的秒数")
    ap.add_argument("--json", action="store_true", help="结果按 JSON 输出")
    a = ap.parse_args(argv)

    if not PAGE.exists():
        print(f"找不到选择器页面：{PAGE}", file=sys.stderr)
        return 1

    if a.print_path:
        print(PAGE)
        return 0

    _Handler.page_bytes = PAGE.read_bytes()

    server = None
    port = None
    for candidate in PORTS:
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate), _Handler)
            port = candidate
            break
        except OSError:
            continue

    if server is None:
        # 端口全被占也不致命：页面还能用 file:// 打开，用户点「复制」自己粘回来
        print(f"选择器页面：{PAGE}", flush=True)
        print(f"页面地址（本地文件）：{PAGE.as_uri()}", flush=True)
        print("提示：本机候选端口都被占了，一键发送用不了。"
              "请在页面上点「复制」，再把内容粘给我。", flush=True)
        if a.open_browser:
            _open_in_browser(PAGE.as_uri())
        return 2

    url = f"http://127.0.0.1:{port}/"
    print(f"选择器地址：{url}", flush=True)
    print(f"页面文件：{PAGE}", flush=True)
    print("请在宿主的内置浏览器里打开上面这个地址，不要另外弹一个系统浏览器窗口。", flush=True)
    if a.open_browser and not _open_in_browser(url):
        print("没能自动打开浏览器。把上面的地址给用户，让他自己打开。", flush=True)
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
