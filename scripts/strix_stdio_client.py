# -*- coding: utf-8 -*-
"""strix_stdio_client.py — drive the strix_sandbox MCP server over stdio WITHOUT the Qoder bridge.

Use when a session has no mcp__strix_sandbox__* tools (bridge/discovery broken) but you still
need a sandbox. One process = one lifecycle: the server's session cache and its atexit
container-cleanup are per-process, so start -> commands -> stop must happen in a SINGLE run.

Always pass YOUR OWN scan_id. A fresh process cannot see other processes' sandboxes, so
start() will create a NEW container under whatever name you pass — never reuse a live
worker's scan_id, and never call this to "check" someone else's sandbox.

Usage:
  "<PY>" strix_stdio_client.py <scan_id> [--timeout N] "<shell command>" ["<shell command>" ...]
  "<PY>" strix_stdio_client.py <scan_id> [--timeout N] --pull <container_path> <host_path> ...

  --timeout N   per-command wall-clock seconds passed to sandbox_exec (default 120)
  --pull        base64-pulls a file out of the container, decodes it to the host path

Absolute paths (verified 2026-10-08):
  Interpreter: D:\\code\\work\\strix-main\\.venv-mcp\\Scripts\\python.exe
  Server:      D:\\code\\work\\strix-main\\qoder_mcp\\strix_sandbox_mcp.py

Examples:
  "<PY>" strix_stdio_client.py w12345-evid "echo alive && hostname"
  "<PY>" strix_stdio_client.py w12345-evid --timeout 600 "nmap -sV -Pn 203.0.113.5"
  "<PY>" strix_stdio_client.py w12345-evid --pull /workspace/ev/shot.png D:/out/shot.png "agent-browser open https://example.com; sleep 2; agent-browser screenshot /workspace/ev/shot.png"

Notes:
  * Every call carries scan_id (the raw server defaults to "qoder" and fails otherwise).
  * exec results are JSON ({exit_code, ok, stdout, stderr}); this client parses them for you.
  * If the script dies mid-run, the server process dies with it and its atexit hook
    force-removes the containers it created — nothing lingers.
  * Piped raw JSON-RPC is fine for stateless calls, but requests are processed concurrently:
    blind-piping sandbox_start + sandbox_exec in one go can run exec before start finishes.
    This client awaits each response, so sequences are safe.
"""
import asyncio
import base64
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PY = r"D:\code\work\strix-main\.venv-mcp\Scripts\python.exe"
SRV = r"D:\code\work\strix-main\qoder_mcp\strix_sandbox_mcp.py"

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call(session, name, args, timeout):
    res = await asyncio.wait_for(session.call_tool(name, args), timeout)
    parts = [getattr(b, "text", "") for b in (res.content or []) if getattr(b, "text", None)]
    return "\n".join(parts)


async def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        return 1
    scan = argv.pop(0)
    exec_timeout = 120
    steps = []
    while argv:
        a = argv.pop(0)
        if a == "--timeout":
            exec_timeout = int(argv.pop(0))
        elif a == "--pull":
            steps.append(("pull", argv.pop(0), argv.pop(0)))
        else:
            steps.append(("exec", a))
    params = StdioServerParameters(command=PY, args=[SRV])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            out = await call(s, "sandbox_start", {"scan_id": scan}, 300)
            cid = json.loads(out).get("container_id", "")[:12]
            print("[start] scan=%s container=%s" % (scan, cid))
            for st in steps:
                if st[0] == "exec":
                    out = json.loads(await call(
                        s, "sandbox_exec",
                        {"scan_id": scan, "command": st[1], "timeout": exec_timeout},
                        exec_timeout + 90))
                    print("[exec rc=%s] %s" % (out.get("exit_code"), st[1][:140]))
                    if out.get("stdout"):
                        print(out["stdout"][:20000])
                    if out.get("stderr"):
                        print("[stderr]", out["stderr"][:2000])
                else:
                    src, dst = st[1], st[2]
                    out = json.loads(await call(
                        s, "sandbox_exec",
                        {"scan_id": scan, "timeout": 60,
                         "command": "base64 -w0 '%s'; echo; echo __B64_END__" % src},
                        150))
                    b64 = out.get("stdout", "").split("__B64_END__")[0].strip()
                    if len(b64) < 16:
                        print("[pull FAILED] %s -> no data (rc=%s)" % (src, out.get("exit_code")))
                        continue
                    data = base64.b64decode(b64 + "=" * (-len(b64) % 4))
                    with open(dst, "wb") as f:
                        f.write(data)
                    print("[pull] %s -> %s (%d bytes)" % (src, dst, len(data)))
            out = await call(s, "sandbox_stop", {"scan_id": scan}, 120)
            print("[stop]", out.replace("\n", " ")[:160])
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
