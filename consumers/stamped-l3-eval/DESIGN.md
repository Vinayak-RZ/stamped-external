# DESIGN.md — L3 Eval Lab

## Scene

Engineer at a desk auditing why MD fired — bright office or dim evening — needs density and tabular numbers, not a hero.

## Theme

**Light laboratory.** Cool gray surfaces tinted toward steel blue (OKLCH). Not cream, not purple-dark.

## Color strategy

**Restrained**

| Token | Role |
| --- | --- |
| `--lab-bg` | Page background (cool gray) |
| `--lab-panel` | Side/nav panel (slightly cooler) |
| `--lab-ink` | Primary text |
| `--lab-muted` | Secondary labels |
| `--lab-accent` | Selection / primary action (steel blue) |
| `--status-emitted` | Amber/orange signal |
| `--status-suppressed` | Muted slate |
| `--status-shadow` | Info teal |
| `--status-error` | Red |
| delivery-l4 / lab_only chips | Green-tint vs slate — lane primary |
| hypothesis chip | Warm muted — weak signal, not error |

Accent ≤10% of surface. Status chips carry semantic meaning.

## Typography

- Family: **IBM Plex Sans** (+ IBM Plex Mono for refs/IDs)
- Tabular nums for kW / ₹ / kVA
- Scale ratio ~1.125–1.2; no display fonts in labels

## Layout

- App shell: left nav (Corpus / Detectors / Compare / Live) + main stage
- No cards in first viewport; tables are the primary affordance
- Window forensic: timeline | detection table | inspector

## Motion

150–250ms ease-out: row select, inspector reveal, live pulse. Honor `prefers-reduced-motion`.

## Components

Inline filters, dense tables, status chips, split panes. Skeletons for loading; empty states teach CLI commands.
