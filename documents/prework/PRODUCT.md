# PRODUCT.md — Nury (prototype)

Named for Juan's late tía Nury — devout Catholic, Legion of Mary, Cord of the
Discalced Carmelites, never married, always ready to help in the church.

## What it is
Nury is a crisis-response agent for a solo pastor. When an immigrant family
faces a detention, raid, or sudden legal emergency, the pastor types what the
family told them; the agent works through five stages and produces a complete
response package. Every stage pauses for pastor approval. Nothing reaches the
family except through the pastor's hands.

## The user (specific, per Track 1)
A solo pastor, no staff, no lawyer on the line — fielding a panicked call on a
Sunday afternoon or late at night, often from a church parking lot, on their phone.

## The job (five stages)
1. Triage — raw intake → structured case (situation, people, location, family
   language, urgency + reason, 3 missing facts). Factual, no advice.
2. Rights brief — plain-language brief in the family's language, built ONLY from
   a vetted local source file, every point cited. Ends urging attorney consult.
3. Attorney resources — national hotlines + church-vetted local entries.
   Never recommends a specific attorney.
4. Family checklist — DO TONIGHT / DO NOT DO / GATHER THESE DOCUMENTS.
5. Pastoral message draft — under 120 words, warm/steady/hopeful, family's language.

## Agent behavior (the "real agent" requirements)
- Each stage: model call → guardrail check → on failure, feed failure reasons
  back and retry (max 2 retries) → if all fail, escalate to the human.
- Guardrails: legal INFORMATION only (never advice/predictions/strategy);
  attorney consult urged; claims grounded in provided sources with citation;
  calm language; family's language; disclaimer on every output.
- Approval gate between stages: Approve / Edit / Stop. Stop = "I'll handle
  this manually."
- No send path. No open web: legal info comes only from vetted local sources.
- Audit log of every tool call, check, retry, timestamp (collapsible).

## Distribution (assumptions — labeled)
- Single self-contained HTML file. Pastor opens a URL (GitHub Pages). No install,
  no server. Gloo AI Studio is the backend; pastor pastes their own API key once
  (localStorage, never leaves the device).
- This prototype simulates the agent run with scripted data (no API key yet);
  the JS is architected with a clean seam (`Agent.runStage`) so the event build
  swaps simulation for live Gloo calls.

## Design world (from the brief)
- NOT a chat UI. Three views: Intake → Pipeline → Package.
- "Lantern in the dark": deep ink background, single warm amber accent, calm and
  steady. Night-shift cockpit for crisis use.
- Serif (family-facing words deserve care) + quiet grotesque for chrome.
- Mobile-first: pastor is on their phone. Thumb-sized approval buttons.
- Mode: Operate. Scanability and the real usage scene outrank expression.
