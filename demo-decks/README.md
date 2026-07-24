# Demo decks

Client-facing HTML presentation decks for Stamped Energy: one walkthrough per industry.

| Path | Use |
|------|-----|
| [index.html](./index.html) | Industry picker (hub) |
| [cement.html](./cement.html) | Cement: kiln, mills, WHR |
| [steel.html](./steel.html) | Steel: furnace, rolling mill |
| [pharma.html](./pharma.html) | Pharma: load management, HVAC, chillers |
| [pharma/](./pharma/) | Pharma Vercel deploy root (`index.html`; `vercel --prod`) |
| [tech/](./tech/) | Tech deep-dives linked from the Technology slide |
| [assets/](./assets/) | Industry hero photos |
| [/index.html](../index.html) | Same hub at repo root for GitHub Pages |

**Tech deep-dives** (shared across industries; open from `#scene-tech` cards):

| Page | Pillar |
|------|--------|
| [tech/physics.html](./tech/physics.html) | Versioned industrial physics & rulepacks |
| [tech/models.html](./tech/models.html) | Plant-calibrated industrial ML |
| [tech/agents.html](./tech/agents.html) | Bounded prescription agents |
| [tech/evidence.html](./tech/evidence.html) | Verified with evidence (calculation engine) |

Back-links use `?from={cement|steel|pharma}` → `{industry}.html#scene-tech`. Citation SSOT: [`../technical/stamped-research-and-ml-citations.md`](../technical/stamped-research-and-ml-citations.md).

Each industry deck keeps the same Proof Run structure. What changes:

- **Prescriptions** (short, readable actions + evidence tags)
- **Data sources** called out in the hook / gap / “what we read” slides
- **Optimisation targets** on the savings map (what we check first)
- **Hero photo** matched to the industry

Open an industry file in a browser. Arrow keys, space, or on-screen controls navigate. On phones, the title slide is **text → Begin → plant photo**; the simulated Sample workspace slide is skipped. On the **floor** slide, Snooze / Acknowledge cycle three prescriptions on the phone, then show **Stamped Energy**.

**Rebuild from base:** edit `demo-decks/_base.snapshot.html` (generic template) and/or `scripts/build-industry-decks.py`, then:

```bash
python3 scripts/build-industry-decks.py
```

**GitHub Pages:** enable Pages from the repo root so `/` serves the hub and `/demo-decks/*.html` serves each deck.

**Vercel (pharma only):** deploy the standalone folder:

```bash
cd demo-decks/pharma && vercel --prod
```

**Floor / verify check:**

```bash
python3 scripts/check-floor-phone.py
```
