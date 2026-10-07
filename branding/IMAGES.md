# Images and credits

Rule: no photos of real detainees or children, no people who can be identified, no agency imagery. Each photo comes from a source with a license we checked on the file's own page. If a license was unclear, we skipped the image. Files are local and compressed, with no hotlinks.

## Photos
| File | What it shows | Author | License | Source |
|---|---|---|---|---|
| `presentation/images/porch-light.jpg` | A porch light glowing on a stucco wall at night. No people. | Henryemix | CC0 1.0 (own work, public domain dedication) | https://commons.wikimedia.org/wiki/File:Porch_Light.png |
| `presentation/images/lanterns-hand.jpg` | A hand lighting small glowing lanterns at night. No face. | Peter Hershey (peterhershey) | CC0 1.0. The file page says the photo was published on Unsplash before 5 June 2017, under CC0. | https://commons.wikimedia.org/wiki/File:Glowing_Paper_Lanterns_(Unsplash).jpg (original: https://unsplash.com/photos/89S4s-cKPmU) |

License checks, 2026-10-06: read the license text on each Commons file page. Both pages state CC0 1.0. CC0 needs no credit; we credit anyway on the credits slide.
Processing: resized (900 px and 1200 px wide), JPEG quality 74 to 76, metadata stripped. About 100 KB each. The original files were downloaded at build time from Wikimedia Commons.

## Considered and not used
- Ely Cathedral at night (CC BY 2.0): a crowd appears in silhouette. Skipped.
- A house at night (CC BY-SA 4.0): not needed, and share-alike adds a condition.
- "Empty chair" memorial photos: tied to real tragedies. Skipped.
- A phone lit in a dark room: no licensed photo found. We drew one.

## Our own illustrations
Drawn for this project in the lantern style, flat shapes, no faces and no figures with identities. Files in `presentation/images/`: `phone-night.svg`, `family-silhouette.svg`, `shoes-door.svg`, `window-night.svg`. The lantern mark is in `branding/`.

## Fonts
Fraunces and Inter, SIL Open Font License, loaded from Google Fonts in the deck. If the venue has no internet, the deck falls back to Georgia and the system sans.

## Fonts (self-hosted in the app)
- Fraunces 400 and 600, and Inter 400 and 500, served from `code/app/static/fonts/` as woff2. Both families are open source under the SIL Open Font License 1.1. The app no longer loads fonts from Google.
- Gochi Hand 400, self-hosted at `code/app/static/fonts/GochiHand-400.woff2`, used only for the hand-written notes (decoration, aria-hidden). Open source under the SIL Open Font License 1.1 (Google Fonts). No font is loaded from a CDN at run time.
