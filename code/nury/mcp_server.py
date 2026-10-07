"""A small MCP server over stdio that exposes Nury's rules as read-only tools. Standard library only.

    python -m nury.mcp_server

Tools: list_playbooks, describe_rules, check_draft, get_scorecard_summary. They call the same functions as the command line
(nury.toolkit). No model, no key, no network, no file written, no way to start a run or reach a family. check_draft never
sends the text anywhere: it is checked in memory and forgotten. Protocol: JSON-RPC 2.0, one JSON message per line."""
import json
import sys

from . import toolkit

PROTOCOL = "2024-11-05"
MAX_LINE = 200_000

TOOLS = [
    {"name": "list_playbooks", "description": "List Nury's crisis playbooks (id, title, status).",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "describe_rules", "description": "Describe every rule Nury checks a draft against: the safety floor, the named checks and the Jev questions.",
     "inputSchema": {"type": "object", "properties": {"name": {"type": "string", "description": "One rule name to explain; leave out for all rules."}}, "additionalProperties": False}},
    {"name": "check_draft", "description": "Run Nury's safety floor and a stage's named checks on a draft you wrote. No model is called and nothing is stored. Returns the violations, if any.",
     "inputSchema": {"type": "object", "required": ["playbook", "stage", "lang", "text"], "additionalProperties": False,
                     "properties": {"playbook": {"type": "string", "description": "detention or hospital"},
                                    "stage": {"type": "string", "description": "a stage id, for example rights, checklist, pastoral"},
                                    "lang": {"type": "string", "description": "es or en"},
                                    "text": {"type": "string", "maxLength": toolkit.MAX_CHARS}}}},
    {"name": "get_scorecard_summary", "description": "Summarize a stored evaluation set: outcomes, corrections, cost and Jev judge means. Single runs on synthetic families.",
     "inputSchema": {"type": "object", "properties": {"set": {"type": "string", "enum": ["detention", "hospital", "attacker"]}}, "additionalProperties": False}},
]


def _call(name, args):
    if name == "list_playbooks":
        return toolkit.list_playbooks()
    if name == "describe_rules":
        return toolkit.explain(args["name"]) if args.get("name") else toolkit.describe_rules()
    if name == "check_draft":
        return toolkit.check_draft(args.get("playbook"), args.get("stage"), args.get("lang"), args.get("text"))
    if name == "get_scorecard_summary":
        return toolkit.scorecard_summary(args.get("set", "detention"))
    raise toolkit.ToolError(f"unknown tool {name!r}")


def handle(msg):
    """One JSON-RPC message in, the reply out (None for a notification)."""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
        return {"jsonrpc": "2.0", "id": msg.get("id") if isinstance(msg, dict) else None, "error": {"code": -32600, "message": "invalid request"}}
    mid, method, params = msg.get("id"), msg["method"], msg.get("params") or {}
    if "id" not in msg:                                   # a notification (for example notifications/initialized): no reply
        return None

    def ok(result):
        return {"jsonrpc": "2.0", "id": mid, "result": result}
    if method == "initialize":
        return ok({"protocolVersion": params.get("protocolVersion") or PROTOCOL, "capabilities": {"tools": {}},
                   "serverInfo": {"name": "nury-rules", "version": "1.0"}})
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": TOOLS})
    if method == "tools/call":
        try:
            res = _call(params.get("name"), params.get("arguments") or {})
            return ok({"content": [{"type": "text", "text": toolkit.text_of(res)}], "isError": False})
        except toolkit.ToolError as e:
            return ok({"content": [{"type": "text", "text": str(e)}], "isError": True})
        except (TypeError, KeyError, ValueError, OSError) as e:
            return ok({"content": [{"type": "text", "text": f"the request could not be used ({type(e).__name__})"}], "isError": True})
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}


def main(stdin=None, stdout=None):
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    while True:
        line = stdin.readline(MAX_LINE + 1)
        if not line:
            return 0
        if len(line) > MAX_LINE:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "message too long"}}
            while line and not line.endswith("\n"):          # skip the rest of that line
                line = stdin.readline(MAX_LINE)
        elif not line.strip():
            continue
        else:
            try:
                reply = handle(json.loads(line))
            except ValueError:
                reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        if reply is not None:
            stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            stdout.flush()


if __name__ == "__main__":
    sys.exit(main())
