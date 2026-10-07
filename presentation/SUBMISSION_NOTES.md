# Submission notes (for the notes field of the entry form)

Lines that belong in the submission, outside the 250-word description:

- The video narration is an AI-generated voice (ElevenLabs).
- The Jev decision API from TypeSafe is used as typed judges in our evaluation harness and as a run-time draft classifier; disclosed as third-party technology per the rules.
- Entry by Juan Peláez, 3Metas.
- Built in Boulder, Colorado, during the Gloo AI Hackathon, October 6 to 8, 2026. Every step is in the build log. (link the build log). The planning notes and a small scripted scaffold existed before the event and are kept in `documents/prework` as reference. The first commit of the Nury repository is 2026-10-06 19:36 MDT, and everything in `code/` was written during the event.
- With no Gloo key the app runs a RECORDED run of each sample intake (replay mode). The model's words are recorded; the checks, gates and privacy layer run for real. It is not a live run and is off when a key is present. Also shipped: a read-only CLI and MCP server for Nury's rules (no key, no model call).
- Images and fonts: see `branding/IMAGES.md`.

The first line is disclosure, not attribution: the judges should know the narration is synthetic. It stays out of the description, which stays unchanged.
