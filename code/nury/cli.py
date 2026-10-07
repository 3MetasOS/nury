"""Nury's rules from a shell. Read-only: no model, no key, no network, no file written.

    python -m nury.cli playbooks
    python -m nury.cli rules [--json]
    python -m nury.cli explain RULE_ID
    python -m nury.cli check --playbook detention --stage rights --lang es --file draft.txt     (or --file - for stdin)
    python -m nury.cli score [--set detention|hospital|attacker]

check exits 0 when the draft passes, 1 when a rule rejects it, 2 on a request it cannot use. Output is JSON."""
import argparse
import json
import sys

from . import toolkit


def _file_text(path):
    if path == "-":
        return sys.stdin.read(toolkit.MAX_CHARS + 1)
    with open(path, encoding="utf-8") as f:
        return f.read(toolkit.MAX_CHARS + 1)


def main(argv=None, out=None):
    out = out or sys.stdout
    ap = argparse.ArgumentParser(prog="python -m nury.cli", description="Read-only tools over Nury's rules.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("playbooks", help="list the playbooks")
    r = sub.add_parser("rules", help="describe every rule")
    r.add_argument("--json", action="store_true")
    e = sub.add_parser("explain", help="explain one rule")
    e.add_argument("rule_id")
    c = sub.add_parser("check", help="run the safety floor and a stage's named checks on a draft")
    c.add_argument("--playbook", required=True)
    c.add_argument("--stage", required=True)
    c.add_argument("--lang", required=True)
    c.add_argument("--file", required=True, help="a text file, or - for stdin (at most 20,000 characters)")
    s = sub.add_parser("score", help="summarize a stored evaluation set")
    s.add_argument("--set", dest="which", default="detention")
    try:
        a = ap.parse_args(argv)
    except SystemExit as ex:
        return 2 if ex.code else 0
    try:
        if a.cmd == "playbooks":
            print(toolkit.text_of(toolkit.list_playbooks()), file=out)
        elif a.cmd == "rules":
            rows = toolkit.describe_rules()
            if a.json:
                print(toolkit.text_of(rows), file=out)
            else:
                for x in rows:
                    print(f"{x['kind']:10} {x['name']:32} {x['explanation']}", file=out)
        elif a.cmd == "explain":
            print(toolkit.text_of(toolkit.explain(a.rule_id)), file=out)
        elif a.cmd == "check":
            res = toolkit.check_draft(a.playbook, a.stage, a.lang, _file_text(a.file))
            print(toolkit.text_of(res), file=out)
            return 0 if res["ok"] else 1
        elif a.cmd == "score":
            print(toolkit.text_of(toolkit.scorecard_summary(a.which)), file=out)
    except toolkit.ToolError as ex:
        print(json.dumps({"error": str(ex)}), file=out)
        return 2
    except OSError as ex:
        print(json.dumps({"error": f"could not read the file: {type(ex).__name__}"}), file=out)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
