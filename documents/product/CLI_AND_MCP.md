# Nury's rules from a shell or an agent: the CLI and the MCP server

Written 2026-10-07 by hack-jedi. Four new files, nothing else changed: `code/nury/toolkit.py` (the shared functions), `code/nury/cli.py`, `code/nury/mcp_server.py` and `code/tests/test_toolkit.py` (13 tests). The scored build behaves exactly as before.

## What it is for

Another team has its own drafts: a rights brief, a checklist, a message for a family. Before it shows them to anyone, it can ask Nury's rules: does this draft pass the safety floor and the checks a Nury stage applies? The answer is a list of violations, or none. The same rules run inside Nury on every draft. This is the pattern from `PATTERN.md` (generate, verify, regenerate, with a person at the gate) with the verify step offered on its own.

## What it is not

- It is not the pipeline. It writes nothing and calls no model.
- It is not a hosted API. It runs on your machine, on text you give it.
- It is not a complete test of a draft. It runs the deterministic rules only. Jev is not run, the church network and the official list are empty (so checks that compare a draft with them pass), and a verse is not fetched. A draft that passes here can still fail in Nury. The floor is a tripwire, not a proof.

## Hard limits (tested)

Read-only. No Gloo, Jev, YouVersion or ElevenLabs key is read or needed (a test records every environment variable the tools touch). No file is written. No network call (the tests block any connection to another machine). No case data. No way to start a run or reach a family. A draft is capped at 20,000 characters and is checked in memory and forgotten.

## Command line

```
python -m nury.cli playbooks                          # the crises Nury knows
python -m nury.cli rules                              # every rule, one line each (add --json)
python -m nury.cli explain cited_bullets              # one rule in full
python -m nury.cli check --playbook detention --stage rights --lang es --file draft.txt
cat draft.txt | python -m nury.cli check --playbook hospital --stage checklist --lang es --file -
python -m nury.cli score --set detention              # a stored evaluation set: outcomes, cost, Jev judge means
```

Run it from `code/`. `check` prints JSON and exits 0 when the draft passes, 1 when a rule rejects it, 2 when it cannot use the request:

```
{"ok": false, "violations": [{"category": "ungrounded_claim", "reason": "bullet without a source citation: '- Llame a un abogado...'"}],
 "named_checks": ["cited_bullets", "ends_with_referral"], "not_checked": ["Jev is not run; ..."]}
```

Stages: detention has triage, rights, attorney, checklist, pastoral; hospital has triage, info, resources, checklist, pastoral. Languages: `es`, `en`. A pastoral draft must use the VERSE, WHY and MESSAGE labels.

## MCP server

Standard library only, no new dependency, JSON-RPC over stdio. Tools: `list_playbooks`, `describe_rules`, `check_draft`, `get_scorecard_summary`. Each calls the same function as the command line.

A Claude Code `.mcp.json` entry (run from the repo root):

```json
{
  "mcpServers": {
    "nury-rules": {
      "command": "python3",
      "args": ["-m", "nury.mcp_server"],
      "cwd": "code"
    }
  }
}
```

Try it without a client:

```
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | (cd code && python3 -m nury.mcp_server)
```

Why both: an agent with a shell gets the command line for the cost of one short command and no schema in its context. An agent that speaks MCP gets typed tools it can discover. They share one set of functions, so they cannot disagree.

## How it is checked

`tests/test_toolkit.py`: the verdicts equal the engine's for the same text (a rejected draft from the engine's own loop gets the same categories here, and the approved text passes); no key is read; no file is opened for writing; none of the three modules imports a client; the command line returns 0, 1 and 2 where it should; an MCP handshake, a tool list, a check, a refusal, a bad message, an oversized line, and the server run as a real process.
