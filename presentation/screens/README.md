# Deck screenshots (real app, light mode)

Made by `capture_screens.py` from the running app. Day mode, 2x pixel density (a 1280-wide shot is 2560 px; a 390-wide shot is 780 px), cropped tight to the content, no browser chrome, no address bar. Fictional demo data only: Jose and Maria, the Demo Legal Aid contacts, the saved synthetic cases. No keys, no personal data. The app was not changed to take them.

Re-make them: start the two servers (live app on 8080; replay app with `NURY_REPLAY=1 NURY_FEEDBACK=on PORT=8096`, no demo network) and run `python3 presentation/screens/capture_screens.py all` from the repo root. Needs agent-browser, Pillow and pdftoppm. The script uses its own browser session.

Each screen exists at `-1280` (laptop) and `-390` (phone), except the two PDF pages (1200 px wide, one size).

| File (prefix) | What it shows | App state used |
|---|---|---|
| `01-home` | Home: Respond to a crisis, the four crisis cards in a 2 by 2 grid (two live, two coming soon), Our network, Continue where you left off, Your cases | Live app, 5 saved synthetic cases |
| `02-crisis` | Immigration matter crisis page: banner, what this covers, the Begin the response button, what you will get, the flow with a gate after each stage | Replay app, crisis page `#/crisis/detention` |
| `03-chooser` | The crisis chooser popup with the four cards (Immigration, Hospital, Sudden loss and House fire, the last two marked coming soon) | Replay app, opened from Home |
| `04-intake` | Intake with the sample text (Maria's call about Jose), Spanish selected, the notice and Begin | Replay app, "Use the sample intake" pressed |
| `05-gate` | Stage 1 gate (Triage): the draft, the feedback chips (Good as is, Too long, Not my voice, Wrong tone, Inaccurate), Approve, Edit, Stop | Replay app, first gate, feedback on |
| `06-final-es` | The final page in Spanish: headline, key facts, Save to case file, Copy all, Export, the first sections | Live app, the approved text of a saved Spanish detention case, shown on the final page |
| `07-case-overview` | A saved case, Overview tab: header and actions, the tab bar, the five-stage sequence ending in the glowing Case complete marker, Next steps | Live app, the same saved Spanish detention case |
| `08-network` | Our network: the banner and note, the fictional-contacts notice, the contact cards, and the "How the network works" notes band | Live app, demo network on |
| `09-cases` | The Cases list with filters and search | Live app, 5 saved synthetic cases |
| `10-export-menu` | The Export menu open: Family copy (PDF), Pastor copy (PDF), Both in a zip, Print family copy, Print pastor copy | Same final page as `06`, Export pressed |
| `11-pdf-family-1200`, `11-pdf-pastor-1200` | Page 1 of the Spanish family copy PDF and of the English pastor copy PDF, 1200 px wide | Exported from the live app for the same saved Spanish case |
| `12-about` | The top of the About page: banner, the short story note and What Nury is | Live app |

Notes
- `02-crisis`, `03-chooser`, `04-intake` and `05-gate` come from the replay app, which plays a recorded run with no model call. The gate screen therefore carries the recorded draft. The replay line on the intake reads "Demo with a saved example."
- The replay app is started without the demo network. With it on, the recorded attorney-resources stage fails a vetted-contacts check and the run stops at stage 3 (reported to the coordinator).
- The 390 shots are long, tight crops of the whole screen, not phone-frame crops. The fixed bottom tab bar is not in them.
