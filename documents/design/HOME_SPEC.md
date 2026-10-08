# Nury home and crisis detail: design spec

Owner: UX/UI lead. For: hack-artisans. Target file: `code/app/static/index.html`.
Prototype files (open them in a browser, they need no server):
- `documents/design/prototype/home.html` (Home, Cases, Our network, About sheet, Settings sheet)
- `documents/design/prototype/crisis-detail.html#detention` and `#hospital`
- `documents/design/prototype/icons.svg` (the icon and scene sprite)

Voice of this document: short sentences, plain words. Copy in the prototype is draft copy for the product owner to approve.

## 0. What I could not verify

I had no browser, no shell and no way to list folders. Read this before you trust anything below.
- I never saw the prototype render. I wrote it defensively (flex and grid with `minmax(0,1fr)`, `overflow-wrap:anywhere`, no fixed widths). `body{overflow-x:hidden}` is a safety net, not a fix. Check 390 px and 1280 px for horizontal scroll first.
- Contrast ratios below are computed by hand. Run a checker before you ship. One value is close to the line (Day primary button, section 9).
- I did not find the self-hosted Fraunces and Inter files. I checked `code/app/static/fonts` and `branding/fonts`, and neither exists. The current app loads fonts from Google Fonts (lines 10 to 12 of `index.html`), which is an external request. The prototype uses `@font-face` with `local()` only, so it falls back to Georgia and system sans if the fonts are not installed. Please find or add the font files and use real `@font-face` rules.
- I did not read `code/nury/casefile.py`, `server.py` or `network.html`. The data fields and endpoints in section 12 are assumptions from `index.html`. Confirm them.
- The `<dialog>` sheets, `:focus-visible`, `aria-pressed` toggles and `line-clamp` are standard in current browsers. I did not test them in Safari on iOS.
- I did not test with a screen reader. `FEATURES.md` says nobody has. Do not claim it.
- The design research in section 1 is from memory of well known guidance. I did not re-fetch the pages this session. Names are given so you can look them up.
- Crisis detail copy (what each stage makes, what the pastor decides) is my reading of `stages.json` and `playbook.json` for both crises. Product owner should read it once. The "call 911 first" line is new copy and needs approval.

## 1. Design craft notes (what shaped the choices)

| Topic | Guidance used | Where it shows up |
|---|---|---|
| Visibility of system status, recognition over recall (Nielsen's 10 heuristics) | A returning user should see what is open and where they stopped, not remember it. | "Continue where you left off", stage pips ("Stage 3 of 5. Waiting for you.") |
| Dashboards in care and case tools (NN/g dashboard guidance; the "inbox plus next action" pattern in case-management tools) | Lead with the few items that need action, show a count summary, push the full list to its own page. | Home shows at most 3 open cases and count tiles. The full list lives on Cases. |
| Cards versus lists (NN/g on cards and list views) | Cards suit few, rich items. Lists suit many items you scan and compare. | Home uses cards (status, progress, next action). Cases uses compact rows. |
| Progressive disclosure (NN/g) | Show the decision first, details on demand. | Home crisis cards show one line. The detail page shows the workflow before intake. About sheet holds the technical claims. |
| Thumb reach (Steve Hoober's studies of how people hold phones; Apple HIG 44 pt; Material 48 dp) | Primary actions low and large. | 56 px primary buttons, bottom tab bar on phone, a fixed Begin bar on the crisis page, hero button full width. |
| Accessibility (WCAG 2.2: 1.4.3 and 1.4.11 contrast, 2.4.7 focus visible, 2.5.8 target size, 4.1.3 status messages, 2.3.3 and `prefers-reduced-motion`) | AA text contrast, visible focus, status read aloud, motion off on request. | Section 10. |
| Empty states (NN/g on empty states; "teach the interface, give one next step") | Say what will be here, why it is empty, and give one action. | First-visit Home and empty Cases. |
| Trauma-informed, calm microcopy (for example Chayn's trauma-informed design principles) | Short, plain, active voice, no alarm, no blame, give control back. | Section 8. "Nury drafts. You decide." "Nothing was sent." |
| Frontend craft | One accent, real hierarchy, no template look. Each area gets its own picture and background, not just a new title. | Section 6 and the area bands. |

## 2. Information architecture

Sitemap:

```
Home  (#/)
|-- Crisis detail  (#/crisis/detention, #/crisis/hospital)     task page, no tab bar on phone
|    `-- Intake  ->  Protect names  ->  Pipeline (5 stages, gate after each)  ->  Package
|                                                                              `-- Save to case file
|-- Cases  (#/cases, #/cases/inprogress|follow|v2|saved)
|    `-- Case viewer  (#/case/:id)  versions v1 v2, Something changed, Compare, Export zip
|-- Our network  (#/network)  contacts the church vetted
|-- About this build  (sheet, #about)
`-- Settings  (sheet): Night and Day
```

Rules:
- Three tabs: Home, Cases, Our network. Bottom bar on phones (60 px tall), pills in the top bar at 960 px and up.
- Task pages (Crisis detail, Intake, Protect, Pipeline, Package) hide the bottom tabs on phone. A task has one job and one exit. The back link and the fixed Begin bar replace the tabs.
- Settings and About are sheets, not pages. Back and Escape close them. Focus returns to the button that opened them.
- Coming-soon crises are not links. They have no detail page.
- Leave room for more: a new crisis is a new card (data driven), a new area is a new tab and a new band. Do not add a fourth tab without a design pass. A place for sign-in is deliberately not designed.

## 3. Home layout, in order

### Phone (390 px). One column, top to bottom.

1. Top bar (60 px): lantern mark 28 px, "Nury" in Fraunces 600, settings button (48 px) at right. The tagline is hidden on phone.
2. Hero card. Heading "Welcome back." (first visit: "Nury is ready."), one line of help, a full-width primary button "Respond to a crisis" (56 px) that scrolls to section 4. A small lantern scene sits under the text. Radial amber glow from the top right.
3. "Continue where you left off": up to 3 case cards, link "See all N cases" at the right of the heading. Hidden when there are no cases. Replaced by the first-visit card (below).
4. "A family needs help": two live cards (Detention, Hospital), then two dashed "Coming soon" cards. Each live card links to its crisis detail page.
5. "Your cases" count tiles: All, In progress, Needs follow-up, Version 2, Saved. Each tile links to Cases with that filter. Shown only when there are more than 3 cases (otherwise Continue already shows all).
6. "Our network" tile with its own picture and a button.
7. "How this was made" strip with five short facts and the "About this build" link.
8. Footer line: AI assistant disclaimer and "Nury never sends anything. You do."
9. Bottom tab bar (fixed).

Why Continue comes before the crisis cards on phone: a returning pastor is more often resuming a case. The hero button is the one-tap path to responding, so a family in need is never more than one tap away. Product owner may flip this (section 13).

### Desktop (1280 px). Max width 1120 px.

```
[ top bar: lantern Nury tagline | Home Cases Our network |           settings ]
[ hero, full width: text and button (left) | lantern scene (right)           ]
[ Continue where you left off (flex)        | A family needs help (392 px)    ]
[ Your cases count tiles                    | Our network tile                ]
[ How this was made strip, full width                                       ]
```

The DOM order is the phone order. CSS `display:contents` plus `order` on phone, and two flex columns at 960 px and up.

### First visit (zero cases)
- Heading "Nury is ready." Hero line: "When a family calls, respond here. Nury drafts. You decide. Nury never sends anything."
- The Continue slot becomes a card: "No cases yet." One sentence on what appears here, then three numbered steps (Choose the crisis, Tell Nury what the family said, Approve each stage then save).
- No count tiles. Cases tab shows its own empty card with the lantern shelf scene and a "Respond to a crisis" button.

## 4. Components and states

| Component | Default | Other states |
|---|---|---|
| Case card (Home) | 48 px crisis tile, title (Fraunces 18, 2 lines max, wraps anywhere), meta "Detention, changed 35 min ago", status chips, action label (Continue or Open) and chevron. Min height 88 px. The whole card is one link. | **In progress:** adds 5 pips (green approved, pulsing amber current, grey pending) and "Stage 3 of 5. Waiting for you." **Saved:** neutral chip with check. **Version 2:** extra chip. **Needs follow-up:** dashed amber chip with flag. **Long title:** clamps at 2 lines, full title shows in the viewer. **Hover:** border turns amber line. **Focus:** 2 px amber outline. |
| Case row (Cases) | 40 px tile, title, crisis name, chips, time, chevron. At 640 px and up it is one line of columns. | Same status chips. No progress pips (the row stays scannable). Long title clamps at 2 lines. |
| Status chip | Icon 14 px plus word, 13 px, 26 px tall. Meaning is never color alone. | In progress (amber fill, progress icon). Saved (muted, check). Version N (surface fill, v2 icon). Needs follow-up (dashed amber, flag). Green is not used for chips, because the brand reserves green for approved and red for rejected. Green appears only in the approved pips. |
| Count tile | Big number in Fraunces, label under it. 68 px tall. | Zero counts still show "0". Links to Cases filtered. |
| Crisis card | 56 px tile, Fraunces 19 title, one line of description, chevron. 96 px tall. | **Coming soon:** dashed border, muted, "Coming soon" tag, not a link, not focusable. |
| Search | 52 px field, 16 px text (stops iOS zoom), visible label for screen readers. | Empty result: "No cases match." with "Clear filters". |
| Filter chips | 44 px tall toggle buttons with `aria-pressed`. Two rows, Crisis and Status. Scroll sideways inside their own row on phone. Wrap on desktop. | Pressed: amber fill and border. |
| Count line | `role="status"`: "6 cases" or "2 of 6 cases shown". | Announced when filters change. |
| Area band | Kicker with icon, H1, one line, a scene. Cases band has ledger lines. Network band has a dot grid. Crisis band has a glow and a doorway or window scene. Home hero has a glow. | Scene hidden from screen readers. |
| Tab bar | Icon above label, 60 px, current tab has a 3 px amber top rule and amber text. | Pills on desktop with amber-soft fill for the current tab. |
| Sheet (About, Settings) | Native `<dialog>`, rises from the bottom on phone, centered 640 px on desktop. Sticky title and a 48 px close button. | Backdrop click and Escape close it. |
| Toast | Prototype only (stands in for screens not built here). | `role="status"`. |
| Workflow rail (crisis page) | Five 44 px nodes joined by dashed lines with a gate diamond. Labels: Triage, Brief, Contacts, Checklist, Message. Nodes link to the stage cards below. | The diamond is decorative. The legend explains it. |
| Stage card | Number, title, two columns "Nury produces" and "You decide" (stacked on phone), then "Your gate: Approve, Edit or Stop". | None. Static content. |

Data cases to test: zero, one, six, long title (a 120 character title with hyphenated names is in the sample data), filter with no match, 30 cases (the Cases list must stay fast: render 20, then a "Show 20 more" button; not built in the prototype).

Sorting on Home: in progress first, then needs follow-up, then most recently changed. Grouping: one card per case family. v1 and v2 are one card with a "Version 2" chip. The card opens the newest version. The viewer already has version chips.

## 5. Icon set

All icons: 24 px grid, 1.75 stroke, round caps and joins, `currentColor`, no fill except one small "ember" dot (`fill:var(--ember)`) where it fits. That ember is the lantern family trait. They are original. No people, no crosses, no flags of any nation, no agency imagery. Defined in `prototype/icons.svg`; the prototype inlines the symbols it uses.

| Id | Used for | Drawing idea |
|---|---|---|
| `i-mark` | Brand lantern (64 grid, from `branding/logo-mark.svg`) | Unchanged brand mark |
| `i-lantern` | Home tab | Small outline lantern with an ember flame |
| `i-cases` | Cases | Folder with a tab and an ember |
| `i-network` | Our network | Three linked nodes, ember at the center |
| `i-settings` | Settings | Two sliders |
| `i-detention` | Detention crisis | Arched doorway with an ember inside |
| `i-hospital` | Hospital crisis | Rounded room with a pulse line (no cross) |
| `i-sudden` | Sudden death (coming soon) | Quiet bench with an ember on the backrest |
| `i-fire` | House fire (coming soon) | House outline with an outlined flame |
| `i-audit` | Audit log | Page with lines |
| `i-save` | Save to case file, package | Arrow into a tray |
| `i-v2` | Version 2 | Two sheets and an ember |
| `i-protect` | Protected names | Brackets around an ember (a token) |
| `i-flag` | Needs follow-up, notes | Pennant |
| `i-progress` | In progress | Ring with an ember |
| `i-triage`, `i-brief`, `i-resources`, `i-checklist`, `i-message` | The five stages | Funnel lines, open book, pin, checklist, speech bubble |
| `i-gate` | Approval gate | Diamond with a check |
| `i-never` | "What Nury will never do" | Circle with a slash |
| `i-check`, `i-edit`, `i-stop`, `i-clock`, `i-search`, `i-plus`, `i-chev`, `i-back`, `i-close`, `i-build`, `i-sun`, `i-moon` | Generic | Plain |

Scenes (320 by 120, decorative, one per area): `s-home` (lantern with dotted halo and a few stars), `s-cases` (shelf of case spines, one raised with an ember above it), `s-network` (five linked nodes, one lit), `s-detention` (doorway with a light on the ground), `s-hospital` (window with a pulse line and a lit corner). Scenes use `color:var(--scene)` and the ember uses `--ember`.

Use pattern: `<svg class="i" aria-hidden="true" focusable="false"><use href="#i-cases"/></svg>`. Inline the symbols once at the top of `index.html`. Do not use `<use href="icons.svg#...">` from a file, it fails on some setups and adds a request.

## 6. Why each area looks different

| Area | Identity |
|---|---|
| Home | Amber glow from the top right, large lantern scene, big primary button. The warmest screen. |
| Crisis detail | Doorway or window scene, the workflow rail and the vertical flow with dashed rails and gate diamonds. A procedural page, not a list. |
| Cases | Ledger-line background, shelf scene, dense rows. Calm and archival. |
| Our network | Dot-grid background, linked-node scene, "Our church's own" labels on every contact. |
| Package and Case viewer | Keep the current reading layout (Fraunces for family-facing words). Add the crisis icon tile to the page title. |

The single accent stays amber. Variety comes from shape, scene, background pattern and layout, not new colors.

## 7. Crisis detail page

Sections, in order (phone and desktop share the order):

1. Back link "All crises" (48 px tall).
2. Header band: kicker with crisis icon, H1 (the title from `/api/playbooks`), lead, three chips (Available now, 5 stages, Family language: Spanish or English), scene.
3. What this covers (3 short bullets) and one callout line: "If anyone is in immediate danger, call 911 first."
4. What you will get: five pieces with stage icons, a package you copy or download and save, an audit log.
5. How it works: the rail (at a glance), a legend ("Each diamond is a gate. Nothing moves on until you decide."), then the flow.
6. What Nury will never do (7 shared lines plus one crisis line, with a slash icon on each).
7. A note on time.
8. "About this build" link.
9. Begin. Phone: fixed bottom bar with a 56 px "Begin the response" button and a small line "About a minute of drafting. You approve each stage." Desktop: sticky right column card "Ready when you are".

The flow (vertical dashed rail, 44 px nodes):
- Cap: "First, you and Nury get ready" (protect icon). You type what the family said, pick the family's language, tick the names to protect.
- Five stage cards. Each has "Stage N of 5", title, "Nury produces", "You decide", and the gate line.
- Cap: "Then the package is yours" (save icon). Copy, download, save to a case file. If something changes, record it and Nury drafts version 2 and keeps version 1 as it was.

Time note, exact copy: "Nury drafts all five stages in about a minute. That is drafting only. You read each stage and decide at each gate, so the whole crisis takes as long as you need. Nury waits for you." Never state a total time for the whole crisis. The only number is "about a minute of drafting". Source: TECH_CLAIMS 30 (50 to 56 s for four full runs, your measured 35 to 55 s agrees).

Data source: render from the playbook, do not hardcode. Proposed `detail` block in `playbook.json`: `lead`, `covers[]`, `gives[]`, `never_extra`, `domain`. Per stage in `stages.json`: `short`, `icon`, `makes`, `decide`. The prototype keeps these in one JS object (`D`) with the same shape. Strip the "1. " prefix from stage titles.

Content check against the repo: detention stages are Triage, Rights brief, Attorney resources, Family checklist, Pastoral message. Hospital stages are Triage, Family information brief, Hospital resources, Family checklist, Pastoral message (checklist headings: DO TONIGHT, DO NOT DO, WHAT TO BRING AND ASK). Official list is Colorado only (FEATURES 5), so the copy says "where we have one (Colorado so far)".

## 8. "How this was made": strip and sheet

### Strip on Home (quiet, one row of small pills, muted)
Label "How this was made", then: Gloo AI Studio, guarded endpoint. Claude Sonnet 4.6. Tokens, not names, reach the model. 20 named checks in the registry, 3 tries. Jev typed judges, a red team, human review. Then a text button "About this build". Names only. No logos.

### Sheet "How this was made" (7 items)

| # | Heading | Statement in the UI | TECH_CLAIMS rows | FEATURES row |
|---|---|---|---|---|
| 1 | Gloo AI Studio and Claude Sonnet 4.6 | Every draft goes through Gloo AI Studio's guarded endpoint, using Claude Sonnet 4.6. | 1 (VERIFIED live) | Safety floor |
| 2 | Tokens, not names | Names you protect, phone numbers, emails, addresses, dates and ID numbers become tokens before anything reaches the model, and come back in the draft. Limit stated: only direct identifiers are removed. | 16 (offline test), 17 (live), 18, 19 (stated limit) | Tokens instead of identifiers |
| 3 | 20 named checks, then 3 tries | 20 named checks in the registry; each stage applies the ones listed for it, plus the safety floor. A failed draft goes back as reasons, not text. Three tries, then it stops and hands over. A rejected draft is never shown. | 4 (live), 5 (offline), 6 (offline) | 20 named checks, Correction loop |
| 4 | Nury sends nothing | No way to email, text or post. The only outgoing call is to Gloo. | 3 (offline test) | No send path |
| 5 | How we test it | Jev typed judges answer fixed questions (testing only, never in the product). A red team of three models from other makers reads what a pastor would see and only advises. People review what is flagged. | 25, 32, 35, 36, 40 | Jev typed judges, Red-team panel, Human review canvas |
| 6 | A crisis is a folder | A crisis is data: prompts, reviewed sources and stages, run by the same engine and the same safety rules. | 10 (offline test) | A crisis is a folder |
| 7 | What we have not done yet | No pastor outside the team has used Nury. Every family in testing is made up. No native Spanish speaker has scored the Spanish. Saved cases are not encrypted. No pass rate is claimed yet. | 19, 43 (stated limits), 12, 29 (PENDING, not quoted) | Section 9: real pastors, native review, encryption NOT BUILT |

Rules I followed:
- Only VERIFIED rows are quoted. Row 40 (red team) is VERIFIED live for the first pass only, and its final run is PENDING, so the copy describes what it is and does ("reads", "advises") and gives no result.
- No pass rate, no skills-improve claim (rows 21, 29 are PENDING), no cost per package in the UI, no claim about states other than Colorado, no claim about sudden death or house fire.
- "Anonymized" is never used. Row 19 says privacy is not anonymization.
- Each list item carries `data-claims="1"` style attributes in the prototype so a reviewer can trace it. They are invisible.
- If any row changes status, update the sheet. Re-check rows 40 and 25 after the final scorecard.

Wording rule (hard): Nury is a web app on a server. Never write "stays on this computer", "local", "on your device", "your machine", "offline" about data. Say instead: "Saved in Nury." "Nothing was sent." "Nury never sends anything." "Tokens, not names, go to the model." Do not mention encryption except in the not-yet list, and do not mention sign-in or accounts at all.

Three existing strings in `index.html` break this rule and must change:
1. Line 135, network link: "Stays on this computer." Replace with the Our network line in section 9.
2. Line 224, case viewer: "Read-only. This case stays on this computer." Replace with "Read-only. Saved in Nury. Nothing was sent."
3. Line 459, save message: "...on this computer in ${r.path}. It stays here. Nothing was sent." Replace with "Saved in Nury as {title}, version {n}. Nothing was sent." Drop the file path.

## 9. Microcopy

Copy is identical in Night and Day. Only the theme control changes (see the last rows). Day tokens are in the table after the copy.

| Key | Text |
|---|---|
| Brand tagline (desktop top bar) | An AI Crisis Response Agent (Juan, 2026-10-07: "solo pastors" is dropped from every positioning place) |
| Tabs | Home, Cases, Our network |
| Settings button (aria-label) | Settings and display |
| Skip link | Skip to content |
| Hero, returning | Welcome back. / Pick up a case, or respond to a new one. Nury drafts. You decide. |
| Hero, first visit | Nury is ready. / When a family calls, respond here. Nury drafts. You decide. Nury never sends anything. |
| Hero button | Respond to a crisis |
| Continue heading | Continue where you left off |
| Continue heading, no cases | Your cases will wait here |
| Continue link | All cases, or "See all 6 cases" when more than 3 |
| First-visit card | No cases yet. / When a family calls, respond to the crisis here. Save the finished package and it waits here, so you can open it later. / 1 Choose the crisis and see how it works. 2 Tell Nury what the family said. 3 Approve each stage, then save. |
| Case card action | Continue (in progress), Open (saved) |
| Case card meta | {Crisis}, changed {time} |
| Pips line | Stage 3 of 5. Waiting for you. |
| Chips | In progress, Saved, Version 2, Needs follow-up |
| Count tiles heading | Your cases |
| Count tiles | All, In progress, Needs follow-up, Version 2, Saved |
| Section heading | A family needs help |
| Section help | Choose what the family is facing. You will see how it works before you begin the response. |
| Detention card | Immigration detention or raid / A family member was detained or taken in a raid. |
| Hospital card | Hospital emergency / A family member is in the emergency room or intensive care. |
| Soon cards | Sudden death in a family, House fire or displacement, tag "Coming soon" |
| Network tile | Our network / Contacts your church has vetted. Nury lists them first and labels them as yours. / Open our network |
| Network page line | Your church's own contacts. Nury lists them first, labeled as yours. Nury never ranks or endorses anyone. Your private note is never sent to the model or put in a family message. |
| Network demo banner | Fictional demo contacts (only in demo mode) |
| Network label on a contact | Our church's own |
| Built strip label | How this was made |
| Built link | About this build |
| Footer | Nury is an AI assistant. It is not a lawyer, doctor, pastor, counselor or therapist. Nury never sends anything. You do. |
| Cases heading | Your cases / Every case you saved or have open. Open one to read it, or to record that something changed. |
| Search | label "Search cases", placeholder "Search by family or place" |
| Filter labels | Crisis (All, Detention, Hospital), Status (All, In progress, Needs follow-up, Version 2, Saved) |
| Count line | 6 cases. / 2 of 6 cases shown. |
| No match | No cases match. / Try another word, or clear the filters. / Clear filters |
| Cases empty | No cases yet. / Finish a crisis and choose Save to case file. It will be here, ready to open. / Respond to a crisis |
| Crisis detail: back | All crises |
| Crisis detail: chips | Available now, 5 stages, Family language: Spanish or English |
| Crisis detail: section heads | What this covers, What you will get, How it works, What Nury will never do, A note on time |
| Crisis detail: callout | If anyone is in immediate danger, call 911 first. |
| Flow legend | Each diamond is a gate. Nothing moves on until you decide. |
| Flow cap 1 | First, you and Nury get ready / You type what the family said, in your own words, and pick the family's language. Nury proposes names to protect. You tick the ones to hide. Tokens, not names, go to the model. |
| Flow cap 2 | Then the package is yours / Copy it, download it, or save it to a case file. If something changes, record what happened. Nury drafts again as version 2 and keeps version 1 as it was. |
| Stage columns | Nury produces, You decide |
| Gate line | Your gate: Approve, Edit or Stop |
| Begin (phone bar) | Begin the response / About a minute of drafting. You approve each stage. |
| Begin (desktop card) | Ready when you are / You will type what the family said, then confirm the names to protect. / Begin the response / About a minute of drafting. You approve each stage. |
| Time note | Nury drafts all five stages in about a minute. That is drafting only. You read each stage and decide at each gate, so the whole crisis takes as long as you need. Nury waits for you. |
| Save success (replaces current) | Saved in Nury. Nothing was sent. Open the case |
| Save success, v2 | Saved in Nury as version 2, beside version 1. Nothing was sent. Open the case |
| Case viewer footer | Read-only. Saved in Nury. Nothing was sent. |
| Follow-up toggle (P2) | Mark for follow-up / Clear follow-up |
| Settings sheet | Settings / Display: Night, Day / About this build |
| Theme control, Night active | Day button label "Day", aria-label "Switch to day mode" (existing) |
| Theme control, Day active | label "Night", aria-label "Switch to night mode" (existing) |
| Error, cases cannot load | Could not load your cases. Check that the server is running. |
| Error, crisis list | Could not load the crisis list. Check that the server is running. (existing) |

Day mode tokens (new and changed):

| Token | Night | Day |
|---|---|---|
| `--bg` | #0d1015 | #f7f3ea |
| `--surface` | #131824 | #fffdf7 |
| `--surface-2` | #1a2233 | #efe8d9 |
| `--line` | rgba(236,231,220,.10) | rgba(13,16,21,.14) |
| `--line-2` (new, stronger edge) | rgba(236,231,220,.20) | rgba(13,16,21,.28) |
| `--amber` (fills) | #e8a33d | #b8680f |
| `--amber-text` | #e8a33d | #8a4a07 |
| `--amber-ink` (text on amber) | #1a1206 | #0d1015 |
| `--muted` | #a79f8d | #5b564b |
| `--ember` (new, icon dot) | #e8a33d | #b8680f |
| `--glow` (new, hero wash) | rgba(232,163,61,.16) | rgba(184,104,15,.14) |
| `--scene` (new, scene lines) | rgba(236,231,220,.42) | rgba(13,16,21,.45) |

Type: H1 30 px phone, 36 px from 640 px (Fraunces 500). H2 22. H3 18 to 20. Body 16/1.55 Inter. Small 14. Chips and meta 13. Uppercase labels 12 with 0.08em tracking. Spacing on the 4/8 grid: 8, 12, 16, 24. Radii 12, 14, 16, 20. No new shadows.

## 10. Accessibility notes

- Contrast, by hand. Night: text on surface about 14:1, muted on surface about 6.7:1, amber text on surface about 8.2:1. Day: muted on surface about 7.2:1, amber text on surface about 6.7:1. Day primary button (ink on #b8680f) is about 4.6:1. That passes 4.5 barely, so do not lighten it. Recheck with a tool.
- Chip and field borders in `--line-2` are about 2:1 on the surface. The label and the fill identify each control, so this is allowed under 1.4.11, but I would not lower it further.
- Focus: `:focus-visible` 2 px outline in `--amber-text`, 2 px offset, on every link, button, input and summary. Do not remove it. The skip link is first in the tab order.
- Targets: primary 56 px. Everything else interactive 44 px or more (tabs 60, filter chips 44, icon buttons 48, tile links 68 to 96). The small sheet "Close" is 48 px.
- Status: the filter count and the toast use `role="status"` (polite). Keep the existing `aria-live` strip in the pipeline. Pips are `aria-hidden`; the line "Stage 3 of 5. Waiting for you." carries the meaning.
- State is never color only: every chip has an icon and a word; pressed filters also have `aria-pressed`.
- Landmarks: one `main`, a `nav` with `aria-label="Main"`, section headings tied with `aria-labelledby`. Current tab uses `aria-current="page"`. One H1 per view, and focus moves to it on a route change (not on first load).
- Sheets use `<dialog>` and `showModal()`, which traps focus and returns it on close. Escape closes. Backdrop click closes.
- Motion: only two animations (pulsing current pip, the step glow). `prefers-reduced-motion` turns all animation and transitions off. Nothing moves on its own otherwise.
- Zoom and text size: no fixed heights, only `min-height`. Titles clamp at 2 lines, so a 200 percent text size still shows all of the key text. The full title is in the viewer.
- Decorative graphics (scenes, icons) are `aria-hidden`. Icon-only buttons have an `aria-label`.
- Language: `lang="en"` for the pastor's screens. Family-facing text keeps its own language where it is shown.
- Not tested with a screen reader. Do not claim it.

## 11. Mapping to the current `index.html`

| New | Current | Change |
|---|---|---|
| Home view `#v-home` | `#v-select` | Replace. Keep `loadSelect()` name or rename and update `show()` list. |
| Crisis cards | `#picks` and `loadSelect()` | Cards link to the crisis detail view. Keep `/api/playbooks`. Soon cards stay non-clickable. |
| Crisis detail view `#v-crisis` | none | New. Its Begin button calls the existing `choose(p)`. Back goes Home. |
| Continue cards | `#cases-list` and `loadCases()` (`.crow`) | New card markup, group versions, sort. `openCase(id)` unchanged. |
| Cases view `#v-cases` | none (list was at the end of select) | New. Search and filters run in the browser over the `/api/cases` array. |
| Our network | `/network` page and `#net-link` | Keep the page. Tab links there. Restyle later with the same band. |
| About sheet | none | New static `<dialog>`. |
| Theme control | `#theme` button | Keep. Add the Night and Day radios in Settings only if time allows. |
| Hash routes | none | Add `#/`, `#/cases`, `#/crisis/:id`. Keep `show()`. Add `hashchange`. |

Use `textContent` for titles from the server (the prototype uses `innerHTML` because its data is hard-coded). Never put server text into `innerHTML`.

## 12. Data and API assumptions (confirm, I did not read the server)

- `/api/cases` today gives `id, title, playbook, created`. For Home add `updated`, `status`, `version`, `version_count`, `family_id` (the id without the `-vN` suffix), and `followup`. Group by `family_id` in the server or the browser.
- In progress: needs `GET /api/sessions` returning live runs (`id, playbook, stage_index, phase, started`) and the pipeline view must be able to attach to a session id. Sessions look like they live in memory. If a restart loses them, say so, and show In progress only for sessions that exist. If this is not feasible in time, ship without the In progress chip. The design still works.
- Needs follow-up: a new field on the case, set by a small toggle in the viewer (`POST /api/case/:id/followup`). Not built. P2.
- Crisis `detail` block: see section 7.

## 13. Decisions for the product owner

1. Order on phone: Continue first (my choice) or the crisis cards first. First visit is the same either way.
2. "Needs follow-up" is a new feature (a flag the pastor sets). Keep, or cut the chip.
3. "In progress" depends on keeping unfinished runs. Is that wanted, and for how long?
4. Cases saved on a server with no sign-in are visible to anyone who can reach the URL. I did not design a sign-in. You told me to leave it out, and the About sheet does not mention it. Please decide how this is protected before real families use it. The sheet already says saved cases are not encrypted.
5. Approve the new copy: the 911 line, the stage descriptions, the "never" list, and the "We have not done yet" item.
6. Show the tab bar on the Cases and Network pages only, or on Home too (design says all three).
7. Should the About sheet name the red-team vendors? I wrote "three models from other makers" to match "names only in text" without adding claims.

## 14. Implementation plan for hack-artisans

Order matters. Stop where time runs out. Hour figures are my estimates, not measurements.

| P | Task | Est. | If short on time |
|---|---|---|---|
| P0 | Fix the 3 banned strings (section 8). Replace the Google Fonts link with self-hosted `@font-face` (find the files first). | 0.5 h | Never cut. |
| P0 | Add tokens `--line-2`, `--ember`, `--glow`, `--scene`. Inline the icon sprite. | 0.5 h | Keep at least the crisis icons. |
| P0 | Home view: hero, Continue (3 cards from `/api/cases`, no In progress yet), crisis cards, first-visit card, footer. | 2 h | Keep the current list with new copy and the crisis cards. |
| P0 | Crisis detail view with the rail, flow, never list, time note and the Begin button. Data in a JS object first, backend later. | 2 h | Drop the rail, keep the flow. Never drop the "never" list or the time note. |
| P0 | Built-with strip and About sheet. | 1 h | Strip only, link to the sheet. Never drop the limits item. |
| P1 | Bottom tabs, hash routes, focus to H1 on route change. | 1 h | Keep Back links only. |
| P1 | Cases view: search, two filter rows, rows, empty states. | 1.5 h | Search only. |
| P1 | Area bands and scenes for Cases, Network, Crisis. | 1 h | Cut scenes, keep icons. Cut first. |
| P2 | Count tiles on Home. | 0.5 h | Cut. |
| P2 | In progress sessions (backend). | 2 h | Cut. |
| P2 | Needs follow-up flag (backend and toggle). | 1.5 h | Cut. |
| P2 | Settings sheet with Night and Day radios. | 0.5 h | Keep the existing Day button. |
| P2 | Show 20 more on the Cases list. | 0.5 h | Only needed above about 30 cases. |

Cut order if time runs short: scenes, count tiles, Settings sheet, Needs follow-up, In progress, rail, Cases filters. Do not cut: wording fixes, crisis detail flow, the never list, the time note, the first-visit empty state, the About limits item, focus rings, reduced motion.

Acceptance checks (do these in a real browser at 390 and 1280 px, Night and Day):
- No horizontal scroll on Home, Crisis detail, Cases, Network.
- The tab bar does not cover the last content (main has 96 px bottom padding on phone).
- Responding to a crisis is one tap from Home, and Begin is reachable from the crisis page on phone without scrolling.
- Zero cases, one case, six cases, the long title and a no-match filter all look right.
- Tab through the page and see the focus ring on every control. Open and close both sheets with the keyboard.
- Turn on reduced motion and see no animation.
- Search the page text for: "computer", "local", "device", "encrypt", "sign in", "account". The only hit allowed is "not encrypted" in the About limits item.
- Read every statement in the About sheet against the TECH_CLAIMS row listed in section 8.

## 15. Prototype notes

- `home.html` has a dashed "Prototype only" bar with three data modes (first visit, one case, six cases). Remove it in the app.
- Routes in the prototype: `#/`, `#/cases`, `#/cases/inprogress|follow|v2|saved`, `#/network`, `#about`, `#start`. Clicking a case or Add a contact shows a toast, because those screens are not part of this work.
- `crisis-detail.html` switches crisis with `#detention` or `#hospital`. The stage rail links use `#s1` to `#s5`. Reloading the page on one of those hashes shows the detention page. That is a prototype limit only.
- Sample families are made up. Contacts are marked fictional. No external requests, no photos, no emoji.

## 16. Copy rule (Juan, 2026-10-07)

The pastor is responding to a family in need. We do not start crises. Use: respond, help, draft, review, approve, save, reopen. Hero button: "Respond to a crisis". Home section: "A family needs help". Crisis page button: "Begin the response". Intake button: "Begin". Halt card: "Try again". "New case" stays only on the saved-package screen.

## 17. Shared shell, chooser, header toggle (Juan, 2026-10-07)

- One shell for every page: `code/app/static/shell.css` and `shell.js` supply the skip link, header (logo, name, "An AI Crisis Response Agent", Home, Cases, Our network, About button, Day/Night toggle), tab bar on phone, and the About sheet. Pages add only `<main id="main">`. An offline test fails if a page defines its own header.
- The Settings sheet is gone. The Day/Night toggle sits in the header on every page. The About button opens "How this was made" from every page.
- "Respond to a crisis" opens a chooser titled "A family needs help": a bottom sheet on phone, a centred modal on laptop. Live crises are large cards with icons; coming-soon cards are muted and not focusable. A primary button never silently scrolls the page.
- About sheet: block "Who writes" (Claude Sonnet 4.6 through Gloo AI Studio, 20 named checks in the registry, up to 3 tries), block "Who checks it before anyone uses it" (Jev from TypeSafe; a red team of three models from three other makers), then what we have not done, and the disclosure line last.
