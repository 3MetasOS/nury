# Nury core interface (hack-jedi)

Python 3.12. Needs `requests`. `GLOO_API_KEY` comes from the environment or the repo-root `.env`. `GLOO_MODEL` is optional (default `gloo-anthropic-claude-sonnet-4.6`). Run from `code/`.

```python
from nury.engine import (CaseState, GateDecision, StageResult, run_stage, run_pipeline,
                         approve_all, DEMO_PROVOKE, STOP_MESSAGE)
from nury.audit import AuditLog
from nury.engine import get_playbook, compute_outcome   # get_playbook("detention") -> Playbook
from nury.playbook import list_playbooks, load_playbook   # list_playbooks() -> [{id, title, description}] for the crisis picker
from nury.stages import STAGES, REGISTRY      # shim: the detention playbook's stages (ids: triage, rights, attorney, checklist, pastoral)
from nury.gloo_client import GlooClient, GuardrailBlock
```

## Signatures

```python
CaseState(intake: str, language: str = "es")   # .approved {stage_id: approved-or-edited text}
                                               # .results  {stage_id: StageResult}
                                               # .set_manual(stage_id, text)  # pastor wrote it by hand

GateDecision(action: "approve" | "edit" | "stop", text: str | None)   # text required for "edit"

run_stage(stage_id, state, gate=approve_all, client=None, audit=None, provoke=None, fault_injection=None, playbook=None) -> StageResult
run_pipeline(playbook, state, gate=approve_all, client=None, audit=None, provoke=None, stages=None, fault_injection=None) -> list[StageResult]
                                  # playbook = id string or Playbook. The old run_pipeline(state, gate, ...) still works (detention).
run_scripted(intake, language="es", decisions=None, fault_injection=None, client=None, audit=None, stages=None, playbook=None) -> (state, results, audit)
                                  # decisions: {stage_id: "approve" | "stop" | ("edit", text)}; default approve
scripted_gate(decisions) -> gate
```

`gate(result: StageResult) -> GateDecision` runs after each stage. The gate only ever sees a safe draft.

```python
StageResult(stage_id, title,
  status,      # "approved" | "edited" | "stopped" | "escalated" | "error"
  draft,       # safe draft shown at the gate (None if escalated or error)
  final,       # text later stages use: the draft if approved, the pastor's text if edited
  disclaimer,  # show with every output (English for triage, family language otherwise)
  metrics,     # attempts, retries, self_corrections, latency_s, input_tokens, output_tokens, cost_usd
  message,     # "I'll handle this manually." for stopped / escalated / error
  # eval-only fields (the gate callback never receives `attempts`):
  attempts,           # [{n, text, violations: [{category, reason}]}]  (text None on a Gloo 403)
  reason_categories,  # categories of rejected attempts, e.g. ["banned_phrase"]
  escalated,          # bool
  shown_text,         # draft + disclaimer, what the pastor saw (None if escalated)
  gate,               # {action, edited_text}
  input_context)      # {dep_stage_id: approved/edited text this stage consumed}
```

## Playbooks (a crisis is a folder)

`code/playbooks/<id>/` holds `playbook.json`, `stages.json`, `prompts/`, `sources/`, `outcomes.json`. The engine never names a crisis. Detention is `playbooks/detention/`. To add a crisis, add a folder. See `documents/ARCHITECTURE.md`.

- `playbook.json` carries the domain wording the engine's rules template fills in: `boundary: {who, domain, professional, professional_kind}`, the `disclaimer` (en, es), `draft_label`, and optional `extra_banned: [{pattern, why}]`. The rules stay in the engine (`nury/guardrails.py`). The engine holds no immigration words.
- `summary` (optional, on a stage in `stages.json`): one plain line for the pastor's screen, at most 140 characters, no HTML. Display only: it is never put in a prompt, a check, the audit log or a model request (tests prove it). Read it as `stage.summary` from `get_playbook(id).stages`; it is an empty string when absent.
- `stages.json` per stage: `id, title, audience ("pastor"|"family"), prompt, input, deps, sources, checks, when, variants`.
- `sources[]`: `{name, file, var, groups:[{list, line, empty?}]}`. The engine renders the vetted JSON into the prompt variable `{{var}}`. `{{lang_name}}` is also available.
- `checks[]`: named checks from `nury/checks.py`: `required_labels, numbered_after, cited_bullets, ends_with_referral, vetted_links_present, required_headings, max_words`. They add to the safety floor.
- **Paths.** `when` is a plain field match on triage output (`"LABEL: value"` lines become fields, e.g. `urgency`). `{"field": "triage.urgency", "in": ["high"]}`, or `equals`, `matches` (regex), `all`, `any`. A stage whose `when` fails gets `status="skipped"` and the run goes on. `variants: [{when, prompt}]` swaps the prompt for the first match. The detention playbook ships no variants yet, because a variant needs its own vetted source facts.
- **Outcomes.** After `run_pipeline`, `state.outcome = {outcome, message, package, failed_stage}`. `outcome` is `package_complete`, `stopped_by_pastor`, `escalated`, or `blocked` (Gloo blocked every attempt, or the call failed). `outcomes.json` says what each hands the pastor. `by_stage` overrides one failing stage (rights escalation hands over `sources_list`).
- **Safety floor (engine, not data).** Boundary prompt, banned-pattern checks, language check, link and phone allowlist from the stage's sources and approved earlier text, disclaimer on every output, 3-attempt cap, no send path. The loader refuses a playbook whose disclaimer drops "AI assistant / pastor / not a <professional> / advice" (EN and ES), or that has no `boundary` fields, and refuses a playbook whose stage 1 is not `triage`.
- Prompt history: `playbooks/detention/PROMPT_NOTES.md`. Tests: `cd code && python3 -m unittest discover -s tests`.

## Crisis list and live tracks

`nury.playbook.list_playbooks()` returns the data for `GET /api/playbooks`, in display order:

```json
{"playbooks": [
  {"id": "detention",     "title": "Immigration detention or raid", "description": "...", "status": "live"},
  {"id": "hospital",      "title": "Hospital emergency",            "description": "...", "status": "live"},
  {"id": "sudden-death",  "title": "Sudden death in a family",      "description": "Coming soon. Not available yet.", "status": "soon"},
  {"id": "house-fire",    "title": "House fire or displacement",    "description": "Coming soon. Not available yet.", "status": "soon"}
]}
```

- `status` is `live` or `soon`. A `soon` entry has no stages. `load_playbook`, `run_stage` and `run_pipeline` raise `PlaybookError` for it. The UI must not make it clickable.
- **Source approval.** A playbook with `sources/approvals.json` (hospital) runs only when every source it uses is `approved`. A `rejected` source is removed from the playbook. While any is `pending`, the playbook lists as `soon` and refuses to run. For UI work only, set `NURY_ALLOW_PENDING=1` in your dev shell: it lists and runs as `live`. Never set it for the demo or the eval.
- **Stage ids differ per playbook.** Take them from `get_playbook(id).stages`. Hospital: `triage, info, resources, checklist, pastoral`. Detention: `triage, rights, attorney, checklist, pastoral`. For the forced rejection use stage index 1 of the playbook: `fault_injection={"stage": pb.stages[1].id, "times": 1, "draft_suffix": UNSAFE_SUFFIX}`. The env switch `NURY_FORCE_REJECTION` still targets `rights` only.
- Pass the id through: `run_stage(stage_id, state, gate, client, audit, fault_injection=..., playbook="hospital")`, `run_pipeline("hospital", state, ...)`, `run_scripted(..., playbook="hospital")`.
- `playbook.json` may carry `intake: {placeholder, demo}`. The app reads it for the intake box and the "Use demo intake" button. The detention demo text is the locked text from `presentation/SHARED_DEMO.md`, byte for byte.
- Hospital extra banned patterns (medical outcome, diagnosis guesses, medical advice, promises of healing) live in `playbooks/hospital/playbook.json` under `extra_banned`, not in the engine.

## Skills

Small versioned instruction modules in `code/skills/<name>/SKILL.md` (header: name, version; sections `## EN` and `## ES`; optional `checks.json` of named checks). A stage names them in `stages.json`: `"skills": ["voice", "grounding"]`. The engine adds the skill text for the stage's output language to the stage prompt. No extra model call.

- Today: `voice` on pastoral and checklist (both playbooks); `grounding` on checklist (both), attorney (detention), resources (hospital). `{professional}` in a skill is filled from the playbook's `boundary.professional`, so skills carry no domain words.
- **Floor wins.** A skill can add rules and checks. The loader refuses a skill that tries to override the floor, the disclaimer or the citations (English or Spanish wording), that has no version or no EN and ES section, or whose checks.json removes, replaces, or names an unknown check. A playbook that names a refused skill does not load.
- **Switch.** Skills are ON by default. Turn them off per call with `skills=False` on `run_stage`, `run_pipeline`, or `run_scripted` (`skills=True` forces on), or for the whole process with `NURY_SKILLS=off`. Off means no skill text, no skill checks, no `skill_applied` events (an audit event `skills_off` {stage, skipped} appears instead), and `metrics["skills"] == []`. The floor, the disclaimer, and playbook checks are unchanged. Use it for before and after runs.
- **Evidence.** Audit event `skill_applied` with `name`, `version`, `stage` (once per stage run). `StageResult.metrics["skills"]` = `[{"name", "version"}]`. A skill's own check failure shows as a category, for example `stock_phrase`.

## Case files (`nury/casefile.py`, no model call)

```python
from nury import casefile as cf
cf.save_case(state, audit, playbook=None, root="cases", case_id=None, privacy=None) -> {"id", "path", "files"}
cf.list_cases(root="cases")  -> [{"id", "playbook", "title", "created", "status", "path"}]   # newest first
cf.load_case(case_id, root="cases") -> {"meta": {...}, "pages": {"index.md": text, ...}, "svg": "<svg ...>"}
cf.export_zip(case_id, root="cases", dest=None) -> "<path to .zip>"       # default <root>/<id>.zip
cf.nextsteps_svg(pb, state, title) -> svg string                          # the map alone
cf.CaseError                                                             # raised on any refusal
```

Layout: `cases/<id>/` holds `index.md`, `intake.md` (the pastor's words, exactly; a revision appends below it), one page per stage (`01-<stage id>.md` ... in playbook order; skipped stages have no page), `people.md`, `documents.md`, `timeline.md`, `log.md`, `nextsteps.svg`, `case.json`. Pages link with relative markdown links, and `index.md` embeds the map. `cases/` is gitignored. The case id is `<playbook>-<yyyymmdd>-<hhmmss>-<4 hex>` unless you pass one. It never overwrites a case.

- **Call it after the run.** Pass the same `state` and `audit` the pipeline used (`run_scripted` returns both; the app already holds them). Refuses (`CaseError`) unless every stage is `approved` or `edited` (`skipped` is fine). Nothing is written on a refusal.
- **Approved content only.** Stage pages hold `state.approved[stage]` exactly (the pastor's edit if edited, disclaimer included). The log records each gate, edits (flagged), skills applied, and rejected drafts as categories only. A guard refuses the save if a rejected draft or a key value would be written.
- **Map.** Four lanes: Tonight (checklist DO TONIGHT), This week (the documents or bring list), Questions still open (triage MISSING FACTS), Who to call (vetted entries whose link or phone appears in the approved resources text). Steps and questions only. SVG viewBox is 400 wide, dark theme with amber, text escaped.
- Works for any playbook; the hospital case has no immigration text.

## Privacy (`nury/privacy.py`)

Nury sends no direct identifiers to a model. `PrivacyClient` wraps the Gloo client; the engine takes it as `client=`, so the core is unchanged. Outbound, protected names, phones, emails, street addresses, dates, A-numbers, case numbers and ID numbers become stable tokens (`[PERSON_1]`, `[PHONE_1]`, `[ADDRESS_1]`, `[DOB_1]`, `[ANUMBER_1]`, `[CASE_1]`...). Cities and states stay. The map stays in memory and in the case file; it is never sent. Inbound, the reply is detokenized, so the pastor sees real names.

```python
from nury.privacy import propose_terms, make_client, PrivacyClient
cands = propose_terms(intake_text)   # [{"term", "kind": "person"|"place", "count", "suggested": bool}] for the pastor to confirm
client = make_client(protected=[{"term": "Maria", "kind": "person"}, "Jose"])      # the pastor's final list
client = make_client(intake=intake_text)                                          # evals: protect every suggested person
gate = client.wrap_gate(gate)        # a name the pastor ADDS in an edit is protected before the next stage
run_pipeline("detention", state, gate, client, audit)
client.map()                         # {"[PERSON_1]": "Maria", ...}   kept by the app, never sent to the model
client.add_term("Saint Luke's", "place")                                          # the pastor can add terms any time
cf.save_case(state, audit, "detention", root, privacy=client)                    # writes privacy-map.json: real values, saved with the case, never sent to the model
```

- **On by default.** `make_client(...)` returns the plain Gloo client only when `NURY_PRIVACY=off` or `enabled=False` (for A/B).
- **Detection.** Phones, emails, addresses, dates, IDs: deterministic patterns, run on the user text only (vetted phones and links in the rules stay as they are). Names: only the protected list counts. A full name also protects each part.
- **Tokens vs the correction loop.** The checks and the gates see detokenized text. A mangled token (`[PERSON 1]`, `PERSON_1`) is repaired. A token the map does not know makes the client ask again (up to 2 more calls, counted in `meta["privacy"]["extra_calls"]` and in the stage's tokens and latency); if it still fails the token becomes `[?]`, a visible gap at the gate.
- **Events.** `client.events` has kinds and tokens only, never real values.
- **Honest limit.** Direct identifiers are removed. Context ("14 years", "his workplace", a rare job) can still hint at who a person is. A name the pastor did not protect is not removed.

## Church network (`nury/network.py`)

The pastor's own vetted contacts, saved by the app on the server that runs it (`network/network.json`, gitignored like `cases/`; there is no sign-in or encryption at rest yet). Nury lists them first, under "People our church has worked with", labeled as the church's own contacts and not endorsements. It never invents, alters, ranks or endorses a contact.

```python
from nury import network as net
n = net.load_network(root="network", demo=None)       # demo=None reads NURY_DEMO_NETWORK; "1" loads the FICTIONAL demo file (read only)
n.list(); n.get(id); n.add(entry); n.update(id, fields); n.delete(id); n.mark_used(id, "2026-10-07")
n.export_json(dest); n.import_json(src, merge=True)    # one bad entry refuses the whole import; fictional files are refused
n.home; n.set_home("Aurora", "CO")                     # the church's own place: used when a case does not say which state
net.validate(entry)                                    # -> cleaned entry or NetworkError (name, kind, phone or link required)
net.match(entries, state, city, language, kinds, limit=5)    # deterministic, no model
net.parse_location("Aurora, Colorado") -> ("Aurora", "CO")
net.KINDS  # pro_bono_immigration_attorney, legal_aid, medicare_medicaid_help, social_services, interpreter, other
```

Entry fields: `id, name, kind, services, languages (es, en), city, state, phone, url, note, last_used (YYYY-MM-DD), tags, nationwide`. The pastor's `note` stays on the pastor's screen: it is never put in a prompt, a draft, or the map.

- **Demo network.** `code/network_demo/DEMO_NETWORK_FAKE.json` (top-level `fictional: true`, names end with "(fictional)", phones 555-01xx, `.example.org` links). Loaded only when `NURY_DEMO_NETWORK=1`; demos, evals and video set it; a real run never does. The UI must show a banner "fictional demo contacts" when `n.fictional` is true.
- **Matching.** State and language must fit when known; city match ranks first, then most recently used, then name. With no state in the case (triage LOCATION), the church's `home` state is used; with neither, only `nationwide` entries are listed. `kinds` come from the stage in `stages.json`.
- **In the stages.** `attorney` (detention) and `resources` (hospital) carry a dynamic source `{"dynamic": "network", "kinds": [...]}` (and a hook `{"dynamic": "official_list"}` that reads an approved `sources/official_list.json`, empty until one exists). Checks: `network_entries_present` (every matched contact must be listed with its phone or link), `listed_contacts_known` (a church contact keeps its exact name with its own phone or link; a titled person such as "Abogado Juan Pérez" who is in neither list is rejected), `no_endorsement_words` (category `endorsement`: best, recommended, el mejor, altamente recomendada...). The phones and links of matched contacts join the run's allowlist.
- **Run record.** `state.sources_used[stage_id]["church_network"]["entries"]` and the audit event `dynamic_source {stage, entries: {name: [ids]}}`. The case file's "Who to call" lane shows them first, marked "Church:".
- **Our network screen.** `code/app/network_api.py` (`handle(method, path, body)`; also runs alone: `cd code && PORT=8120 python3 -m app.network_api`) and `code/app/static/network.html`. Routes: GET `/api/network` (entries, home, kinds, `fictional`, `readonly`), POST `/api/network`, PUT and DELETE `/api/network/<id>`, POST `/api/network/<id>/used`, POST `/api/network/home`, POST `/api/network/import`, GET `/api/network/export`. A bad request is a 400 with a plain `error`; in demo mode every write is a 403. The page shows the "Fictional demo contacts" banner when `fictional` is true. To mount it in `server.py`: send `/network` to `network.html`, and send any path that starts with `/api/network` to `network_api.handle(self.command, self.path, body)` and write its `(status, content_type, bytes)`.\n- **Privacy.** `client.allow_playbook(pb)` once per session keeps every vetted phone, link and email of the run intact (church network, official list, the playbook's own sources) and still tokenizes the family's own. `client.allow_network(entries)` (PrivacyClient) keeps those phones and links from being tokenized in the context sent to the model; the family's own numbers are still tokenized. Call it once per session with `n.list()`.

## Official list (`nury/officiallist.py`)

The U.S. Department of Justice list of recognized legal service providers (Colorado), as Juan approved it (21 of 28: 18 providers and 3 official pages; 7 held for Pending Renewal). `python3 -m nury.officiallist` builds `playbooks/detention/sources/official_list.json` from `OFFICIAL_LIST_DRAFT.json` and `approvals.json`: approved providers only, with their verbatim phones. Held entries are kept only as names (`held_names`), with no detail, so a check can reject a draft that names one. The detention attorney stage has a dynamic source `{"dynamic": "official_list"}`: entries for the case's state (the church's home state if the case has none), detention-related first, at most 5; an entry the draft says is "probably not useful for a detention call" (the asylum-only center) is skipped. Rules in the check `official_list_rules`: a held entry is never named; a listed entry keeps its exact name and its own phone, email or link and is never called free (the roster does not say whether services are free); the caveat "Listed by the U.S. Department of Justice. Listed does not mean recommended." is present; as-of dates are kept (pro bono list Updated October 2026, roster 10/04/26). The ABA detention entry lists the email route for a family member; the toll-free number on that page is for people held at military facilities and is not listed. Other states have no official section until their list is read and approved.

## Scripture (`nury/scripture.py`, pastoral stage only)

```python
from nury import scripture as scr
scr.list_verses(pb, "es")            # [{"id","reference","first_words","translation","origin"}]  for the gate selector
scr.swap_verse(draft_text, verse)    # verse = one entry of scr.for_language(scr.load_bank(pb.dir), "es"), or None to remove
scr.SCRIPTURE_NOTE                   # "The verse is Scripture, quoted exactly. The rest is a draft; edit it."  show it at the pastoral gate
result.scripture                     # {"id","reference","translation"} or None;  result.note is SCRIPTURE_NOTE when a verse is in the draft
```

The draft is: the message, then `«exact text»` and `— reference, translation`, then the why-lines. `scr.strip_block(text)` returns Nury's own sentences without the verse block: judges and wording checks should look at that, not the quoted verse. Only verses whose `approvals.json` status is `approved` are offered. Church verses go in `network/scripture.json` (need `source_url`, `license`, `translation_es` or `_en`, an id that starts with `church-`, `approved: true`). The audit log gets one `scripture` event with the verse id and the provider (`bank` or `youversion`), and a `scripture_fallback` event with the reasons when YouVersion failed.

Providers (`nury/scripture_providers.py`): `get_passage(entry, lang) -> {id, reference, text, translation, copyright, source}`. The bank is the default and the fallback. Set `YVP_APP_KEY` plus `YVP_BIBLE_ES` and `YVP_BIBLE_EN` (version ids Juan picks) to put YouVersion first. Only a passage id (`PSA.46.1`) and a version id leave the app. Nothing is cached. `run_stage(..., scripture_providers=[...])` injects a chain in tests. `swap_verse` takes a bank entry; it does not call a provider.

## Rules the seam enforces

- **Chaining.** `state.approved[stage_id]` holds approved or edited text. Later stages read it, never the raw draft.
- **Correction loop.** Draft, check, on fail feed the reasons back and regenerate. `MAX_ATTEMPTS = 3` attempts total (first draft + 2 regenerations), so `retries <= 2`. Then `status="escalated"` with `draft=None`. An unsafe draft never reaches the gate. A Gloo 403 (`GuardrailBlock`) counts as a failed try.
- **Stop.** `stop` returns `status="stopped"`. `run_pipeline` halts on stopped, escalated, or error. Continue by hand with `state.set_manual(stage_id, text)` and `run_stage(next_id, state)`.
- **Edits.** The pastor owns them. They are checked and any warnings go to the audit log. They are not blocked. The engine re-appends the disclaimer after an edit. `final` and `state.approved[stage]` always end with the disclaimer, once.
- **Reason categories.** `banned_phrase` (prediction, advice, identity claim, specific-attorney recommendation), `ungrounded_claim` (link or bullet not in vetted sources), `missing_vetted_entry`, `missing_referral`, `format`, `length`, `language`, `stock_phrase`, `gloo_block`. They appear in each `check` / `draft_rejected` audit event and in `StageResult`.
- **Fault injection** (`fault_injection={"stage": "rights", "times": 1, "draft_suffix": "..."}`). The engine appends `draft_suffix` to the first `times` drafts of that stage, after generation and before the checks. `times=1` gives reject, regenerate, pass. `times=3` gives escalation. Use `UNSAFE_SUFFIX` (Spanish) for a suffix that trips `banned_phrase` only. The rejected text goes to the audit log and `attempts` only. The gate and the pastor never get it.
- **Demo switch.** `NURY_FORCE_REJECTION=1` forces exactly one rejection on stage 2 (rights): reject, regenerate, pass.
- **Cost.** `cost_usd` is `None` unless you set `NURY_PRICE_IN` and `NURY_PRICE_OUT` (USD per 1M tokens).
- **Audit.** `AuditLog(path=None)`. Pass a JSONL path to persist. Event kinds: `stage_start`, `gloo_call`, `gloo_block`, `check`, `draft_rejected` (holds the rejected text, `visible_to_pastor=False`), `escalated`, `gate`, `edit_check`, `error`. Each has a UTC `ts`. Never show `draft_rejected` in the pastor UI.
- **No send path.** Nothing in this package sends anything to anyone.
- **Disclaimer.** The engine supplies it. The UI must show it with every output.
- **Language.** Triage is English for the pastor. Stages 2-5 use `state.language`.

## Example

```python
from nury.engine import *
from nury.audit import AuditLog

state = CaseState("Carlos was taken by ICE tonight in Aurora, CO. Wife Maria, two kids. Spanish.")
audit = AuditLog("audit.jsonl")

def gate(r):                       # replace with your UI
    print(r.title, r.metrics, "\n", r.draft, "\n", r.disclaimer)
    return GateDecision("approve")  # or GateDecision("edit", "my text") or GateDecision("stop")

for r in run_pipeline(state, gate, audit=audit):
    print(r.stage_id, r.status)

# Show a rejected-and-regenerated draft (demo/test only):
#   NURY_FORCE_REJECTION=1 python ...        # stage 2, once
#   run_stage("rights", state, fault_injection={"stage": "rights", "times": 1, "draft_suffix": UNSAFE_SUFFIX})

# Eval harness entrypoint with scripted gate decisions:
state, results, audit = run_scripted(intake, "es", decisions={"triage": ("edit", "my text"), "checklist": "stop"},
                                     fault_injection={"stage": "rights", "times": 3, "draft_suffix": UNSAFE_SUFFIX})
```

## Known notes

- Stage text comes from `code/playbooks/detention/sources/*.json` (vetted). Add church-vetted local attorneys to `attorney_directory.json` under `"local"`.
- Floor checks: `nury/guardrails.py`. Named playbook checks: `nury/checks.py`.
- `draft` shown at the gate: `shown_text` starts with a label line ("Borrador de Nury para revisión del pastor") from `playbook.json`. `final` does not carry it.
- A call takes 4-20 s per stage. Run stages in a worker thread if the UI must stay responsive.
