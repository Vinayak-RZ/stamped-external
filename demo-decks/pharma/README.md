# Pharma demo — Vercel deploy root

This folder is a standalone static site. `index.html` is the pharma deck (same content as [`../pharma.html`](../pharma.html)).

## Deploy

From this directory:

```bash
cd demo-decks/pharma
vercel --prod
```

Or with an explicit path:

```bash
vercel --prod demo-decks/pharma
```

## Rebuild

Do not edit `index.html` by hand. Regenerate from the shared builder (keeps the interactive floor phone + verify table in sync):

```bash
python3 scripts/build-industry-decks.py
```

Then redeploy:

```bash
cd demo-decks/pharma && vercel --prod
```