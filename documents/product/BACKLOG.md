# Backlog

Written 2026-10-07 by hack-sensei, at Juan's request. This file holds ideas we have NOT built. Nothing here is a claim about the product. Each item says what it is, why it matters, how hard it is, and what to decide first.

Status words: IDEA (no code, no design), SCOPED (read and sized, ready to build), BUILT (moved to FEATURES.md).

---

## B-001. Voice message of the family copy (IDEA, scoped below)

**The idea.** The pastor taps "Voice message" on a saved case. Nury produces a short audio file in the family's language. The pastor sends it by WhatsApp, Signal, SMS or any app he already uses. Nury still sends nothing.

**Why it matters.**
- Some families read poorly, are in the car, or cannot read a four-page PDF at 2 AM. A voice note is the format a family in crisis already uses.
- It keeps the product's rule: Nury has no send path. The pastor owns the file and the delivery.

**What goes into the audio.** Not the whole PDF. The pastoral message (under 120 words) and the "Tonight" list (about 5 lines), in the family's language. The legal brief, the contacts and the verse stay in the PDF. About 60 to 90 seconds.

### Three ways to build it

| Option | What it is | Effort | Cost | Main risk |
|---|---|---|---|---|
| A. Synthetic voice (text to speech) | A provider reads the approved text. We already use ElevenLabs for the film (paid Starter, Eric voice). | 1 to 2 days | about 1 to 3 cents per message | The text leaves the app; a synthetic voice may be taken for the pastor's |
| B. Record your own | The app shows the approved text as a script. The pastor records in the browser (microphone), re-records, and exports. | 0.5 to 1 day | none | The pastor must have a minute and a quiet place |
| C. Local voice | A voice that runs on the pastor's own computer, so no text leaves. | 2 to 3 days | none | Lower quality, especially natural Spanish |

**Recommendation.** Build B first (cheap, most human, no privacy change), then A as an option behind a plain disclosure. Skip C unless a church needs fully offline use.

### The parts of option A, with sizes

| Part | Size | Notes |
|---|---|---|
| Provider adapter (new file, same pattern as `gloo_client.py`) | 3 hours | key in `.env`, bounded retries, timeouts, a ledger line with cost and length |
| Text for speech | 3 hours | strip headings, numbers and phones read slowly ("tres cero tres, cinco cinco cinco..."), verse excluded or read by the same rules, one file per language |
| Privacy | 4 hours | the text sent out must have names replaced by a neutral word or the voice must say "your family" |
| Endpoint and cache | 3 hours | `POST /api/case/<id>/voice`; cache by hash of the approved text; regenerate when the pastor edits |
| UI | 3 hours | one entry in the Export menu ("Voice message"), a small player, a download, a "Copy to share" hint |
| File format | 2 hours | WhatsApp voice notes are Ogg Opus; MP3 and M4A also play. Produce Opus and MP3. |
| Disclosure | 1 hour | the audio opens with one line: "This is an automatic voice reading a message prepared with the pastor." |
| Tests | 3 hours | no network in tests (a stub provider), accents, length cap, cache, privacy leak test |
| Evaluation | 2 hours | read 5 outputs in Spanish with a native speaker; check phone and number reading |

Total for A: about 2 days of one developer, plus a native Spanish listener.

### Questions to decide before building

1. **Whose voice?** A synthetic voice is not the pastor. If the family believes it is, that is a deception. The opening line fixes it. The alternative, the pastor's own voice (option B), avoids it.
2. **What leaves the app?** For option A, text goes to a speech provider. Today only tokens go to Gloo and Jev. The text of a pastoral message has no names after tokenizing, but the family copy has them. Decide: tokens read as "you", or send names with consent, or use option B or C.
3. **Is voice cloning allowed?** No. Do not clone the pastor. Not now, probably never.
4. **Which messages?** Pastoral message only, or also "Tonight"? Default: both, under 90 seconds.
5. **Language.** Natural Spanish needs a good voice (we have not auditioned one for this). English next.
6. **Retention.** Do not keep the audio after export (or keep it only with the case, deleted with it).
7. **Consent.** The pastor must listen before sending. The button should say "Listen, then share".

### Why it fits Nury

- It is another "approved by the pastor" output, like the PDF.
- It is a small addition to the Export menu, the same engine, the same gates.
- It answers a real access problem: families who do not read well or cannot open a file.

### Risks

- A mispronounced name, phone number or word in a crisis is worse than silence. Needs a human listen and a number-reading rule.
- A cheerful synthetic voice can sound wrong for a grave message. Choose a calm voice, test it.
- Cost grows with use (small), and a shared key has no budget cap (see ECONOMICS).

### Not in scope

Sending the message. WhatsApp or SMS integration. Voice calls. Voice cloning. Any automatic delivery.

---

## B-002. Capture the family's story by voice (IDEA)

**The idea.** After the call, the pastor speaks what the family said instead of typing it. Nury turns the speech into text in the intake box. The pastor reads it, fixes it, and runs the case as today.

**Why it matters.** The call comes at 2 AM, often with a phone in one hand. Typing four paragraphs is slow. Speaking is natural.

**What already works today, at zero cost.** The keyboard on a phone or a laptop has a microphone key (dictation). It types into the intake box now, with no change to Nury. A pastor who uses a dictation app (for example Wispr Flow) gets the same. The backlog item is only about doing it inside Nury, with a clear flow.

**What Nury would add.** A microphone button in the intake, a short recording, the text appearing in the box for review, a rule that the pastor must read it before "Begin", and deletion of the audio after transcription.

### Options

| Option | How | Effort | Cost | Data leaves the app? |
|---|---|---|---|---|
| 0. Device dictation | The phone or computer keyboard. Nothing to build; add one line of help on the intake. | 1 hour | none | The phone's own provider (Apple or Google) |
| 1. Browser speech recognition | The browser's built-in speech API. Free, quick. | 0.5 day | none | Yes (Chrome sends audio to Google); not in every browser; weak offline |
| 2. Record, then send to a transcription service | The page records (MediaRecorder); the server sends the audio to a speech-to-text API. ElevenLabs has one (Scribe) and we already hold a key. Whisper-class models exist in other APIs. | 1 day | a few cents per minute | Yes: the audio, with real names, before our privacy layer can tokenize them |
| 3. Run Whisper in the browser (the "web problem") | A small Whisper model in WebAssembly runs on the pastor's device. Nothing leaves. The first load downloads 40 to 150 MB. | 2 to 3 days | none | No |
| 4. Run Whisper on our own server | whisper.cpp or similar on a small machine. | 2 days plus hosting | hosting | Only to our server |

**Recommendation.** Ship option 0 as a help line now (free, honest). Build option 3 if "names never leave the app" must hold for voice, as it does for text. Option 2 is the quickest to a good demo, but the audio carries real names to a third party, so it needs a plain consent line.

### Questions to decide
1. **Privacy.** Text goes through the privacy layer before any model call. Audio cannot. Which rule wins: convenience (2) or the same promise as text (3)?
2. **Whose speech?** Dictating the pastor's own notes after the call is simple. Recording the call itself raises consent and legal rules (they differ by state and country). Do not record calls.
3. **Accuracy.** Names, accents, background noise and Spanish need a real test. The pastor must review every transcript.
4. **Delete the audio** right after transcription.

### Risks
A wrong transcription of a name, a date or a place goes straight into a draft if nobody reads it. The review step is the safeguard.

### Not in scope
Recording phone calls. Live transcription during the call. Voice commands.

---

## B-003. A follow-up process for each crisis (IDEA, bigger)

**The idea.** Each workflow carries a default follow-up plan, and the pastor adapts it per case. Examples: hospital emergency: check in with the family the next day, then day 3, then a week; immigration: ask about the attorney and hearing dates after 48 hours, then weekly. Nury lists what is due, drafts the follow-up message or call notes with the same gates, and records what happened.

**Why it matters.** The first call is the start. Families in crisis need the pastor again in a day, a week, a month. Today the app has a "needs follow-up" flag and nothing else: no date, no list, no draft.

**What exists today.** A follow-up flag on a saved case. The "Something changed" flow that drafts a new version. A timeline page in each case. Playbooks as data. These are the seeds.

### Design in one picture
1. A new data file per crisis (for example `followups.json`): a list of steps, each with a label, a delay (hours or days), and a kind (check-in message, call notes, a short checklist, a reminder to ask about a date).
2. When a case is saved, the plan is copied onto the case, with dates.
3. The pastor can skip a step, change a date, add a step, or add a note.
4. Home shows "Due today" and "Due this week".
5. Opening a due step offers a draft (the same pipeline: rules, Jev, gates), built from the case and what changed since.
6. Nothing is sent. Optional: export the due dates to the pastor's calendar (an .ics file).

### Options and sizes

| Slice | What | Effort |
|---|---|---|
| 1. Plan as data plus a list | `followups.json`, dates on the case, a due list, mark done, skip, move | 2 to 3 days |
| 2. Calendar export | an .ics file per case or per step | 0.5 day |
| 3. Drafts for follow-ups | a follow-up stage per crisis, its prompts, checks and tests; uses the case so far | 3 to 4 days (prompts and evaluation are the cost) |
| 4. Reminders | email or push when something is due. Needs hosting, accounts and consent. | 3 days plus infrastructure |

### Questions to decide
1. **Who defines the defaults?** The sequence is pastoral and chaplaincy practice, not legal text. Ask chaplains and an immigration attorney for the right intervals. Do not invent them.
2. **Reminders and privacy.** A reminder that names a family is sensitive. No sign-in and no encryption at rest today.
3. **Scope.** This moves Nury closer to a case-management system. The standards page says it is not one. Keep it as a drafting aid with a due list, not a tracker.

### Risks
Wrong default intervals presented as advice. Reminders that nobody reads. A larger evaluation set (each follow-up needs its own scenarios).

### Not in scope
Sending messages. Tracking outcomes for reports. Anything that contacts the family.

---

## B-004. A knowledge base for each case (IDEA, biggest)

**The idea.** Each case gets its own folder of material: documents, forwarded messages, notes, what the family said later. Nury keeps a small structured wiki of the case from that material (people, dates, documents, open questions, what changed), and uses it when it drafts the next stage, a follow-up, or a "something changed" version.

**The pattern.** Andrej Karpathy described an "LLM wiki" in April 2026: raw sources stay untouched in one place; a model reads each new source and keeps a set of markdown pages up to date; a short schema file says how the model must do it. Applied here: `raw/` holds what the pastor adds, `wiki/` holds the pages Nury maintains, and a rules file (our floor and the case rules) governs it. (Sources: public write-ups of the pattern, for example blog.pebblous.ai/report/karpathy-llm-wiki and aibuilderclub.com/blog/karpathy-llm-wiki. We have not tested it.)

**What exists today.** Each saved case already has pages for people, documents, timeline, intake and log. That is a seed of the wiki, written once when the case is saved, not updated as material arrives.

### Options and sizes

| Slice | What | Effort |
|---|---|---|
| 1. Notes and pasted messages | The pastor adds a text note or pastes a message to a case. Stored on the case, shown in a tab. | 1 to 2 days |
| 2. Documents | Upload a PDF or a photo; extract the text (PDF text, then OCR for photos). Shown in the Documents tab. | 3 to 5 days, OCR is the hard part |
| 3. A maintained wiki | After each new item, Nury updates the people, timeline and open-questions pages and keeps a change log. | 4 to 6 days plus an evaluation set |
| 4. Using it in drafts | The case wiki (not the raw files) goes into the prompt of later stages and follow-ups, with new checks. | 3 to 4 days plus prompt, check and Jev work |

Using the material safely is the real work.

### The hard questions (decide before slice 2)
1. **Vetted sources only.** Today the rule is: legal points come only from approved sources, and no open web. Case material is not a vetted legal source. The case wiki may supply facts about this family (names, dates, where someone is held). It must never supply legal conclusions. The prompts and the checks need two lanes: "facts of this case" and "approved legal points". This is the main design change.
2. **Untrusted text.** A document or a forwarded message can contain instructions ("ignore the rules"). It is data, never instructions. The attacker set needs new cases for it.
3. **Privacy.** Uploaded text has names and numbers. It must go through the privacy layer before any model sees it. Photos and PDFs need extraction on our side first.
4. **Cost.** Input tokens are 72 percent of the cost today. A bigger context raises it. Send the short wiki, not the raw files.
5. **Storage.** Documents are the most sensitive thing the app would hold. No sign-in, no encryption at rest, one shared pool of cases today: not acceptable for documents until that changes.
6. **Wrong facts.** A model that summarizes a document can get a date wrong. Every wiki line should point to its source and be editable by the pastor.
7. **Evaluation.** New scenarios: notes that conflict, a document with an injection, a date that changed.

### Not in scope
Reading the open web. Legal analysis of a document. Sharing documents. Anything automatic toward the family.

---

## Order I would build them in (for discussion, not a plan)
1. B-001 option B (record your own voice message): small, human, no privacy change.
2. B-002 option 0 (a help line about dictation): one hour.
3. B-003 slice 1 and 2 (plan as data, a due list, calendar export), after chaplains and an attorney set the intervals.
4. B-004 slice 1 (notes), then decide on documents only after storage and sign-in exist.

## B-005 and later

(Add new items here. Keep each one to: the idea, why it matters, options with effort, questions, risks, not in scope.)
