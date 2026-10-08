# App snippets (for hack-artisans)

hack-ninja does not edit `code/app/`. Copy these in.

## 1. Favicon
Copy `branding/favicon.svg` to `code/app/static/favicon.svg`. The server already serves `/favicon.svg` from that folder (its static rule allows `.svg` names with letters, digits, `-` and `_`).

In the `<head>` of `code/app/static/index.html` (and `network.html`), after the fonts links:

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
```

There is no PNG or `apple-touch-icon`. Raster files are not part of this kit.

## 2. Header
Replace the current header line:

```html
<header><h1>Nury</h1><span>An AI Crisis Response Agent</span></header>
```

with:

```html
<header><svg class="logo" aria-hidden="true" focusable="false" viewBox="0 0 64 64"><g fill="#e8a33d" stroke="#e8a33d"><path fill="none" stroke-width="4.2" stroke-linejoin="round" d="M21 25.4 H43 L40.8 50 H23.2 Z"/><path fill="none" stroke-width="4.2" stroke-linecap="round" d="M16.6 25.4 H47.4 M18.6 53.8 H45.4"/><circle cx="32" cy="12.2" r="4.6" fill="none" stroke-width="2.8"/><path fill="none" stroke-width="2.8" d="M32 16.8 V22"/><path stroke="none" d="M32 31.4 C35.8 35.6 37.4 38.4 37.4 41.2 A5.4 5.4 0 0 1 26.6 41.2 C26.6 38.4 28.2 35.6 32 31.4 Z"/></g></svg><h1>Nury</h1><span>An AI Crisis Response Agent</span></header>
```

and add this CSS next to the existing `header` rules (`index.html`, line 18 to 20). It keeps the lantern at 28 px, centered on the wordmark:

```css
header .logo{width:28px;height:28px;flex:none;align-self:center}
```

The existing `header{display:flex;align-items:baseline;gap:10px}` stays. The mark is 28 px, so use the regular mark here. Under 24 px use the `logo-mark-small.svg` body instead.

## 3. Check
Open the app at 390 and 1280 px. The lantern should sit left of "Nury", amber, and not shrink. The tab should show the lantern.
