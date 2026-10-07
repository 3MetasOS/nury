# Submission notes (for the notes field of the entry form)

Lines that belong in the submission, outside the 250-word description:

- The video narration is an AI-generated voice (ElevenLabs).
- The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules.
- Entry by Juan Peláez, 3Metas.
- Built in Boulder, Colorado, during the Gloo AI Hackathon, October 6 to 8, 2026. Every step is in the build log. (link the build log). The planning notes and a small scripted scaffold existed before the event and are kept in `documents/prework` as reference. The first commit of the Nury repository is 2026-10-06 19:36 MDT, and everything in `code/` was written during the event.
- With no Gloo key the app runs a RECORDED run of each sample intake (replay mode). The model's words are recorded; the checks, gates and privacy layer run for real. It is not a live run and is off when a key is present. Also shipped: a read-only CLI and MCP server for Nury's rules (no key, no model call).
- The shipped build differs from the scored build (9bc5c6d) only in the crisis card titles (for example detention: Immigration matter) and in the title text inside one context string given to the Jev gate; three pipelines run on the shipped build (detention 01 and 14, attacker a02) completed with no draft rejected and with the Jev gate probabilities in their usual range. Three pipelines, one run each, are a smoke check, not a rate.
- Built to grow: a crisis is a defined workflow kept as a folder of plain files (its stages, prompts, vetted sources and possible outcomes). Adding a crisis means adding a folder, not changing the engine. Rules and evaluations can be added too. Evidence: the playbook loader (`code/nury/playbook.py`); `code/tools/new_playbook.py`, which scaffolds a crisis folder that cannot run until a person approves its sources (tested in `code/tests/test_new_playbook.py`); `documents/product/ADD_A_RULE.md` (a rule is one function, a registry line, a stage entry, a sentence for the rules page and a test); and `test_second_playbook_zero_engine_changes` in `code/tests/test_core.py`, which builds a second playbook from scratch and runs it through the same engine.
- Scripture: the model never writes a verse; it picks an id from a list Juan approved, and the engine inserts the exact text from YouVersion (Berean Standard Bible, Biblia Libre Versión Bíblica; version name and copyright shown with every verse) or, if YouVersion is unavailable, from a verified public-domain bank. Credit YouVersion. Not in the 250-word descriptions (no room).
- Images and fonts: see `branding/IMAGES.md`.

The first line is disclosure, not attribution: the judges should know the narration is synthetic. It stays out of the description, which stays unchanged.
