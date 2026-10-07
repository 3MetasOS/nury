# How to add a rule to Nury

A rule is a check a draft must pass before the pastor sees it. Nury has two kinds you can add today, and one kind you cannot.

## What exists today

| Kind | Where it lives | What you write | Who can do it |
|---|---|---|---|
| Data rule | a playbook's JSON | a pattern and a reason, or a required heading | anyone who can edit JSON and run the tests |
| Code check | `code/nury/checks.py` | a short Python function, named in `stages.json` | a developer |
| Floor rule | `code/nury/guardrails.py` and the engine | not editable by a playbook | the core, with approval |

**Not built:** a rule editor in the app, a review and approval flow for a new rule, and staged rollout. Today a rule goes in through a code change, the tests, and a commit. `GET /api/rules` and the "How this was built" page list every rule that exists.

The floor is the part nothing can remove: the nine boundary rules in every prompt, the banned patterns, one language, the link, phone and email allowlists, the disclaimer, three attempts, and no send path. A playbook can add to the banned patterns. It cannot take one away.

## Example 1: a data rule (no code)

Add a banned pattern for one crisis in `playbooks/<id>/playbook.json`:

```json
"extra_banned": [
  {"pattern": "\\byour (mother|father) (will|is going to) (die|recover)\\b",
   "why": "predicts a medical outcome"}
]
```

The engine adds it to the floor patterns for that playbook only. A matching draft is rejected with the reason `banned_phrase` and regenerated. Test it the way `tests/test_core.py` tests the hospital patterns: run a stage with a fake model that returns the phrase, and check that the stage escalates.

## Example 2: a code check, step by step

The rule: the pastoral message may not shout. No word of five letters or more written in capitals. This is a worked example; it is not in the product.

**1. Write the check** in `code/nury/checks.py`. A check takes the stage's parameters, the draft text and a context, and returns a list of violations (empty means clean):

```python
import re
from nury import guardrails as g

def no_shouting(p, text, ctx):
    hits = sorted(set(re.findall(r"\b[A-ZÁÉÍÓÚÑ]{5,}\b", text)))
    return [g.R("format", f"words in capitals: {hits[:3]}")] if hits else []
```

**2. Register it.** Add `no_shouting` to the tuple that builds `REGISTRY` at the bottom of `checks.py`.

**3. Name it in the stage.** In `playbooks/<id>/stages.json`, add to that stage's `checks`:

```json
{"name": "no_shouting"}
```

The loader refuses a name that is not in the registry.

**4. Describe it.** Add one plain sentence to `CHECKS` in `code/nury/rules.py`. A test fails if a check has no description, and this is what the Rules page shows.

**5. Test it.** The test needs a draft that breaks the rule and a draft that does not:

```python
def test_no_shouting(self):
    ctx = SimpleNamespace(state=None)
    self.assertTrue(no_shouting({}, "Dios está CONTIGO esta noche.", ctx))
    self.assertEqual(no_shouting({}, "Dios está contigo esta noche.", ctx), [])
```

The first line must fail before the rule exists and pass after. Then run the whole suite: `cd code && python3 -m unittest discover -s tests`.

**6. Look at it live.** Run one pipeline and read the drafts. A rule that never fires may be wrong, and a rule that fires on safe text costs the pastor an attempt. If it fires on a safe draft, loosen the pattern, not the test.

## Rules for writing rules

- A check never changes the draft. It only says yes or no, with a reason.
- The reason goes back to the model, so write it as an instruction, in plain words. Never put the offending text in it.
- A rule that looks at the pastor's own words should skip words the pastor wrote in the intake. See `no_unauthorized_promises` for how.
- Do not weaken a floor rule to make a draft pass. Fix the prompt or the source.
- Every rule needs a test with the exact sentence that started it.

## Where the rules are listed

`code/nury/rules.py` has the plain-English description of every floor rule, named check and Jev question, and which stages use each. The app reads it through `GET /api/rules`.
