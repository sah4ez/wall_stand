#!/usr/bin/env python3
"""Minimal MCP stdio client: spawn server, handshake, call tools.

Usage:
  mcp_client.py list
  mcp_client.py call <tool_name> <json_args>
"""
import json, os, subprocess, sys, threading, queue, time

# путь к freecadcmd можно переопределить: FREECADCMD=... mcp_client.py ...
FREECADCMD = os.environ.get(
    "FREECADCMD",
    "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd")
CMD = ["uvx", "freecad-mcp", "--freecadcmd", FREECADCMD]

class McpSession:
    def __init__(self, cmd=CMD):
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, bufsize=1)
        self.q = queue.Queue()
        self.err = []
        threading.Thread(target=self._reader, daemon=True).start()
        threading.Thread(target=self._err_reader, daemon=True).start()
        self._id = 0

    def _reader(self):
        for line in self.proc.stdout:
            line = line.strip()
            if line:
                self.q.put(line)

    def _err_reader(self):
        for line in self.proc.stderr:
            self.err.append(line)

    def _send(self, obj):
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def request(self, method, params=None, timeout=120):
        self._id += 1
        rid = self._id
        msg = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params is not None:
            msg["params"] = params
        self._send(msg)
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                line = self.q.get(timeout=max(0.1, deadline - time.time()))
            except queue.Empty:
                break
            data = json.loads(line)
            if data.get("id") == rid:
                if "error" in data:
                    raise RuntimeError(f"RPC error: {data['error']}")
                return data.get("result")
        raise TimeoutError(f"timeout waiting for {method}; stderr tail: {''.join(self.err[-15:])}")

    def notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        self._send(msg)

    def start(self):
        result = self.request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "zcode-stdio-bridge", "version": "0.1.0"},
        }, timeout=60)
        self.notify("notifications/initialized")
        return result

    def list_tools(self):
        out, cursor = [], None
        while True:
            params = {} if cursor is None else {"cursor": cursor}
            r = self.request("tools/list", params, timeout=60)
            out.extend(r.get("tools", []))
            cursor = r.get("nextCursor")
            if not cursor:
                return out

    def call(self, name, args, timeout=300):
        return self.request("tools/call", {"name": name, "arguments": args}, timeout=timeout)

def fmt_result(res):
    import base64
    texts = []
    for i, c in enumerate(res.get("content", [])):
        if c.get("type") == "text":
            texts.append(c["text"])
        elif c.get("type") == "image":
            path = f"/tmp/mcp_img_{i}.png"
            with open(path, "wb") as f:
                f.write(base64.b64decode(c["data"]))
            texts.append(f"[image saved: {path}]")
    body = "\n".join(texts) if texts else json.dumps(res, ensure_ascii=False)
    flag = " [isError]" if res.get("isError") else ""
    return body + flag

if __name__ == "__main__":
    s = McpSession()
    try:
        info = s.start()
        print("== server:", json.dumps(info.get("serverInfo", {}), ensure_ascii=False))
        if sys.argv[1] == "list":
            for t in s.list_tools():
                desc = (t.get("description") or "").strip().split("\n")[0][:110]
                print(f"- {t['name']}: {desc}")
        elif sys.argv[1] == "call":
            name, args = sys.argv[2], json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
            print(fmt_result(s.call(name, args)))
    finally:
        try:
            s.proc.terminate()
        except Exception:
            pass
