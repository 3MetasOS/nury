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

## B-002 and later

(Add new items here. Keep each one to: the idea, why it matters, options with effort, questions, risks, not in scope.)
