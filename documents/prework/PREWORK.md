# PREWORK — rebuild guide for the fresh repo (created Oct 5, night before)

Everything in `~/workspace/gloo-hackathon/` is PRE-WORK. Tomorrow (Tue Oct 6, ~5pm)
a fresh repo gets created and the competition entry is built there from scratch.
This file is the blueprint — architecture and decisions transfer, code does not.

## What to rebuild (the agent)

**Shape:** single Python agent, five sequential stages, each ending at a human
approval gate. No frameworks — plain `requests` against Gloo AI Studio. A pastor
must be able to run it with `pip install -r requirements.txt` + one command.

**Stages** (each: one model call → guardrail check → pastor approval gate):
1. **Triage** — raw intake → structured case: situation (1–2 sentences), people,
   location, family language (es/en), urgency (high/med/low) + one-line reason,
   3 most important missing facts. "Do not give advice. Keep it factual."
2. **Rights brief** — plain-language brief in the family's language, built ONLY
   from a checked-in JSON of sourced rights info (each point cited by source).
   Ends urging attorney consult.
3. **Attorney directory** — national hotlines/resources from a checked-in JSON;
   local entries are church-added. "Do not recommend a specific attorney."
4. **Family checklist** — DO TONIGHT (5–7 steps) / DO NOT DO (4–5) / GATHER THESE
   DOCUMENTS. General information only.
5. **Pastoral draft** — under 120 words, warm/steady/hopeful, in the family's
   language. No legal claims, no outcome promises.

**Self-correction cycle** (this is the "real agent" behavior — keep it):
every stage call goes through ask → guardrail-check → on failure, feed the
failure reasons back into the instructions and retry (max 2 retries) → if all
fail, raise and escalate to the human. Record `self_corrections` per stage;
those counts are eval data.

**Guardrails** (prompt-level + code-level + server-side):
- System boundary (6 rules): legal INFORMATION only, never advice/predictions/
  strategy; always urge attorney consult; ground claims in provided sources with
  citation; on case-specific advice requests, state the boundary briefly and
  route to attorney; calm/compassionate, no frightening language; respond in the
  family's language.
- Banned-phrase output check (fail closed): "you should plead", "your case will",
  "you will win", "guaranteed" (+ extend as evals find more).
- Disclaimer on every stage output (EN + ES versions).
- Gloo server-side guardrails: HTTP 403 → catch as GuardrailBlock → stage
  becomes "[Blocked — pastor handles manually]".
- No send path exists anywhere: nothing reaches the family except through the
  pastor's hands. No real personal data: synthetic demo scenario only.

**Model layer:** Gloo AI Studio, `POST https://platform.ai.gloo.com/ai/v2/guarded/responses`
(OpenAI-compatible shape), `Authorization: Bearer $GLOO_API_KEY`, model via
`$GLOO_MODEL` (default `gloo-anthropic-claude-sonnet-4.6`; list live models at
`GET /platform/v2/models`).

**Data files:** `know_your_rights.json` (entries: topic, summary_es, summary_en,
source — verify with an attorney before real use), `attorney_directory.json`
(national: name, description, url; local: name, area, phone, url).

## What to do during the event (scored!)

1. **Git from the first commit.** Every meaningful step gets a commit Oct 6–8 —
   the code verification team checks event-period work. (Pre-work repo has the
   pattern; do NOT copy its history.)
2. **MIT LICENSE** in the repo (rules require it listed in code).
3. **Name the specific user** in the build doc + pitch: "a solo pastor fielding a
   panicked call from an immigrant family on a Sunday afternoon" — not "pastors".
4. **Live demo with an edge case.** Recorded happy path doesn't count. Suggested
   edges: intake asks "will my husband be deported?" (must route, not predict);
   English intake / Spanish family (language detection); deliberately vague intake
   (must ask missing facts, not fabricate).
5. **Eval set:** ~20 hand-built cases with pass criteria; log failure modes found
   and what changed. Include `self_corrections` counts per run.
6. **Session log** from a live run, auditable.
7. **Verbatim prompts + one earlier version** and what was wrong with it.
8. **Cost/latency per run** (bonus points).
9. **BUILD_DOC.md** — skeleton with the track's exact sections lives in the
   pre-work repo; fill it, don't redesign it.
10. **Bonus plays:** publish build doc openly (permissive license); MCP server
    endpoint; practitioner quote from a mentor at the event; "what didn't work"
    section written honestly.

## Submissions & deadlines (official rules — they govern over announcements)

- Wed Oct 7, 9:00 pm MT — preliminary: solution + 250-word English description
  (video optional). Via organizer-provided GitHub and/or Drive.
- Thu Oct 8, 9:00 am MT — finalist submission (90-sec video REQUIRED, Google Drive).
- All entrants: 90-second summary presentation. Finalist judging Thu morning,
  in person (required for any prize).
- Prize pool: **$200,000** total per official rules (not $250k). Categories:
  Grand Prize; Best of track ×3 (Agents/Bible/Ministry Resourcing); Best in
  function ×3 (Design, Storytelling/Pitch, Technology); bonus challenges.
- Judging: 5 criteria × 20% (0–10 each): Concept/Product, Innovation, Impact and
  Execution, AI, Presentation. "Progress during the event" is explicit.
- Join the Discord. Keep everything non-political (code of conduct bars overtly
  political projects) — humanitarian framing throughout.

## Still needed before live runs work

Gloo AI Studio API key: account at https://studio.ai.gloo.com → add $10 credits →
Dashboard → API Keys → Create New Key → `.env` as `GLOO_API_KEY`. Do this BEFORE
the fresh repo needs its first live run.
