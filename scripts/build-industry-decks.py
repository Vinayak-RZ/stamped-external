#!/usr/bin/env python3
"""Build cement/steel/pharma demo decks from the shared base HTML.

ponytail: one base file + industry packs; three entry HTML files share the same body.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path("/workspace")
BASE = ROOT / "demo-decks" / "index.html"
DECKS_DIR = ROOT / "demo-decks"

# Industry heroes: local assets/ paths, or absolute URL (e.g. Cloudinary)
HERO_BY_INDUSTRY = {
    "cement": "assets/cement-hero.jpg",
    "steel": "assets/steel-hero.jpg",
    "pharma": "https://res.cloudinary.com/ddpyjpt4v/image/upload/v1784561673/pharma-hero_blsn7j.jpg",
}
HERO_ALT = {
    "cement": "Cement plant operations",
    "steel": "Steel fabrication and welding",
    "pharma": "Pharmaceutical production line",
}
PACKS = {
    "cement": {
        "label": "Cement",
        "docTitle": "Stamped Energy · Cement demo",
        "chromeHint": "Cement",
        "title": {
            "eyebrowD": "Cement · kiln, mills, and WHR decisions verified on the bill",
            "eyebrowM": "Cement · bill-verified decisions",
            "h1D": "Kiln and mill data, priced onto the bill.",
            "h1M": "Kiln & mill ₹ actions on the bill.",
            "ledeD": "You already run kiln, mill, WHR, and EMS data. Stamped ranks floor work in rupees, then checks it on the next DISCOM bill.",
            "ledeM": "Ranked kiln, mill, and WHR actions. Verified on the DISCOM bill.",
        },
        "hook": {
            "eyebrow": "Monday 06:40 · Kiln / mill handover",
            "h2": "Your plant already logs this. Nobody owns the fix.",
            "ledeD": "Mill and kiln fans overlapped. EMS logged it. No work order went out.",
            "ledeM": "Mill and kiln fans overlapped. No work order went out.",
            "t1s": "Mill start and kiln fans overlap",
            "t1p": "Shift B brings mill and kiln auxiliaries online together.",
            "t2s": "MD spike hits the incomer",
            "t2p": "EMS threshold crossed. Alert created. Still no assigned owner.",
            "t3s": "Clinker and grinding continue as usual",
            "t3p": "The bill will price this later. The floor never saw the fix.",
            "meterNote": "The EMS recorded the spike, but nobody was assigned to change the next mill start sequence.",
            "statImpact": "₹55k",
            "statImpactLabel": "Monthly demand impact",
        },
        "gapHas": {
            "scada": "Has: kiln, mill, WHR run states",
            "ems": "Has: spike logged at 06:40",
            "meters": "Has: MD window and mill/kiln load profile",
            "bill": "Has: MD, energy, PF line items",
        },
        "whatLede": "Stamped sits on top of the EMS and EnMS you already run. It reads kiln, mill, WHR, and incomer data, issues a ranked action in rupees, sends it to the floor, and closes the result on the next bill.",
        "whatStep1": "Kiln / mill / WHR meters, SCADA and PLC states, and utility line items. Read-only. No control writes to the plant.",
        "rx1": {
            "badge": "Rx · MD coincidence",
            "aria": "Stagger mill and kiln fans. Show evidence.",
            "action": "Stagger mill start and kiln fans by 10 minutes",
            "why": "They started together and pushed MD over the limit",
            "bill": "MD (kVA)",
            "owner": "Grinding supervisor · Shift B",
            "impact": "₹3-5L / month",
            "effort": "Sequence change · no new equipment",
            "rule": "md_overlap@v2.4 · High",
            "due": "This week",
            "evTitle": "Signal window · Mon 06:35-06:50",
            "tags": [
                ("HT_INCOMER.MD", "1,240 kVA", "06:42-06:46"),
                ("CEMENT_MILL.START", "TRUE", "06:38"),
                ("KILN_IDFAN.RAMP", "ON", "06:40+"),
                ("RAW_MILL.RUN", "ON", "06:41+"),
            ],
            "cite": "physics/md_overlap@v2.4 · model conf 0.91 · tariff MD slab · baseline Apr peak week",
        },
        "rx2": {
            "badge": "Rx · WHR / tariff",
            "aria": "Use more WHR in the evening peak. Show evidence.",
            "action": "Use more WHR in the evening peak; cut grid import",
            "why": "WHR was available while the plant still bought peak power",
            "bill": "Energy (kWh) · peak",
            "owner": "Power desk · evening block",
            "impact": "₹2-4L / month",
            "effort": "Dispatch schedule · no new equipment",
            "rule": "whr_peak@v1.3 · High",
            "due": "Next peak block",
            "evTitle": "Peak windows · last 5 evenings",
            "tags": [
                ("WHR.MW", "1.8-2.2 MW avail", "18:00-22:00"),
                ("GRID.IMPORT", "High", "same window"),
                ("CEMENT_MILL.kWh", "Peak draw", "ToD peak"),
                ("TOD.PEAK_FLAG", "TRUE", "scheduled"),
            ],
            "cite": "physics/whr_peak@v1.3 · model conf 0.88 · ToD peak line · baseline last 5 evenings",
        },
        "floor": [
            {
                "title": "Stagger mill start and kiln fans by 10 min",
                "why": "MD peak from Monday overlap",
                "impact": "₹3-5L/mo on MD line",
                "owner": "Grinding supervisor · B",
                "priority": "High",
                "due": "This week · before next peak",
            },
            {
                "title": "Raise WHR draw in the ToD peak window",
                "why": "Peak grid import while WHR capacity sits idle",
                "impact": "₹1.2-2.4L/mo on ToD line",
                "owner": "Power plant lead · A",
                "priority": "High",
                "due": "Next ToD peak",
            },
            {
                "title": "Stage idle mill offline on kiln stop",
                "why": "Mill left online across kiln stop with no clinker pull",
                "impact": "₹0.8-1.5L/mo on energy",
                "owner": "Grinding supervisor · B",
                "priority": "Med",
                "due": "Next kiln stop",
            },
        ],
        "verify": [
            ("MD stagger · mill/kiln", "Apr MD peak", "10-min mill lag", "VERIFIED"),
            ("WHR peak dispatch", "Peak grid import", "Raise WHR draw", "PENDING"),
            ("Idle mill on kiln stop", "Night unload hours", "Staging rule", "IN REVIEW"),
        ],
        "math": {
            "eyebrow": "Where cement electricity cost usually hides",
            "h2": "Where we look first in cement",
            "ledeD": "Avoidable ₹ on a cement HT bill, starting with kiln, mills, and WHR.",
            "ledeM": "Avoidable ₹ on a cement HT bill.",
            "cards": [
                (
                    "MD / demand",
                    ["Mill + kiln aux overlap", "Baghouse / ID-fan coincidence", "Contract demand headroom"],
                    "Bill line · MD (kVA)",
                    "Sample: cement mill and kiln ID-fan ramping together at 06:40",
                ),
                (
                    "Kiln & mills",
                    ["Specific power drift (kWh/t)", "Raw mill idle on kiln stop", "Unnecessary pre-grinding windows"],
                    "Bill line · Energy (kWh)",
                    "Sample: mill left online across a kiln stop with no clinker pull",
                ),
                (
                    "WHR / captive",
                    ["WHR under-draw in peak", "Grid import while WHR available", "TOU mistiming"],
                    "Bill line · ToD energy",
                    "Sample: peak grid draw with WHR capacity sitting idle",
                ),
                (
                    "Fans & utilities",
                    ["Baghouse fan staging", "Idle compressor banks", "Utility run-on across stops"],
                    "Bill line · Energy + MD",
                    "Sample: baghouse fans at full duty during reduced kiln feed",
                ),
                (
                    "SEC / intensity",
                    ["kWh per ton clinker", "kWh per ton cement", "PAT-aligned drift signals"],
                    "Bill + production tag",
                    "Sample: grinding SEC drift without an owned corrective action",
                ),
            ],
        },
        "techBullet": "MD coincidence, mill/kiln idle, WHR vs peak grid, fan staging",
        "offerLedeD": "Start with one cement line or grinding circuit. Audit the data, run prescriptions on the floor, then go or no-go at Day 60: on ₹ savings and plant fit.",
        "offerLedeM": "One cement circuit. Audit → floor → go / no-go at Day 60.",
    },
    "steel": {
        "label": "Steel",
        "docTitle": "Stamped Energy · Steel demo",
        "chromeHint": "Steel",
        "title": {
            "eyebrowD": "Steel · furnace and mill decisions verified on the bill",
            "eyebrowM": "Steel · bill-verified decisions",
            "h1D": "Furnace and mill data, priced onto the bill.",
            "h1M": "Furnace & mill ₹ actions on the bill.",
            "ledeD": "You already run furnace, rolling, and EMS data. Stamped ranks floor work in rupees, then checks it on the next DISCOM bill.",
            "ledeM": "Ranked furnace and mill actions. Verified on the DISCOM bill.",
        },
        "hook": {
            "eyebrow": "Monday 07:15 · Melt / roll handover",
            "h2": "Your plant already logs this. Nobody owns the fix.",
            "ledeD": "Furnace and mill overlapped. EMS logged it. No work order went out.",
            "ledeM": "Furnace and mill overlapped. No work order went out.",
            "t1s": "Furnace restart and mill start overlap",
            "t1p": "Shift B brings melt and roll online together.",
            "t2s": "MD spike hits the incomer",
            "t2p": "EMS threshold crossed. Alert created. Still no assigned owner.",
            "t3s": "Rolling continues as usual",
            "t3p": "The bill will price this later. The floor never saw the fix.",
            "meterNote": "The EMS recorded the spike, but nobody was assigned to change the next furnace–mill sequence.",
            "statImpact": "₹48k",
            "statImpactLabel": "Monthly demand impact",
        },
        "gapHas": {
            "scada": "Has: furnace, mill, utility run states",
            "ems": "Has: spike logged at 07:15",
            "meters": "Has: MD window and melt/roll load profile",
            "bill": "Has: MD, energy, PF line items",
        },
        "whatLede": "Stamped sits on top of the EMS and EnMS you already run. It reads furnace, mill, and incomer data, issues a ranked action in rupees, sends it to the floor, and closes the result on the next bill.",
        "whatStep1": "Furnace / mill / utility meters, SCADA and PLC states, and utility line items. Read-only. No control writes to the plant.",
        "rx1": {
            "badge": "Rx · MD coincidence",
            "aria": "Stagger furnace and mill start. Show evidence.",
            "action": "Stagger furnace and mill start by 8 minutes",
            "why": "They started together and pushed MD over the limit",
            "bill": "MD (kVA)",
            "owner": "Melt-shop supervisor · Shift B",
            "impact": "₹2.5-4.5L / month",
            "effort": "Sequence change · no new equipment",
            "rule": "md_overlap@v2.4 · High",
            "due": "This week",
            "evTitle": "Signal window · Mon 07:10-07:22",
            "tags": [
                ("HT_INCOMER.MD", "1,180 kVA", "07:14-07:18"),
                ("FURNACE.RESTART", "TRUE", "07:12"),
                ("MILL.BITE", "ON", "07:14+"),
                ("COMP_BANK.RUN", "ON", "07:13+"),
            ],
            "cite": "physics/md_overlap@v2.4 · model conf 0.91 · tariff MD slab · baseline Apr peak week",
        },
        "rx2": {
            "badge": "Rx · Idle / holding",
            "aria": "Cut furnace holding on long delays. Show evidence.",
            "action": "Cut furnace holding on delays longer than 30 minutes",
            "why": "Holding power with no cast or roll on 3 of last 5 delays",
            "bill": "Energy (kWh)",
            "owner": "Melt-shop supervisor · Furnace 2",
            "impact": "₹1-1.8L / month",
            "effort": "Holding SOP · no new equipment",
            "rule": "idle_hold@v1.8 · High",
            "due": "Next delay window",
            "evTitle": "Delay / holding windows · last 5 events",
            "tags": [
                ("FURNACE2.HOLD", "ON", "35 min avg"),
                ("CAST.PROD", "0 heats", "same window"),
                ("FURNACE2.kWh", "180 kWh", "per event"),
                ("DELAY.FLAG", "TRUE", "planned"),
            ],
            "cite": "physics/idle_hold@v1.8 · model conf 0.87 · ToD energy line · baseline last 5 delays",
        },
        "floor": [
            {
                "title": "Stagger furnace and mill start by 8 min",
                "why": "MD peak from Monday overlap",
                "impact": "₹2.5-4.5L/mo on MD line",
                "owner": "Melt-shop supervisor · B",
                "priority": "High",
                "due": "This week · before next peak",
            },
            {
                "title": "Cut furnace holding on planned delay",
                "why": "Holding power during cast delay with no production",
                "impact": "₹1.5-2.8L/mo on energy",
                "owner": "Melt-shop supervisor · B",
                "priority": "High",
                "due": "Next delay window",
            },
            {
                "title": "Shift non-critical load off peak tariff",
                "why": "Peak grid draw that can move to shoulder",
                "impact": "₹0.9-1.8L/mo on ToD",
                "owner": "Electrical lead · A",
                "priority": "Med",
                "due": "Next tariff window",
            },
        ],
        "verify": [
            ("MD stagger · furnace/mill", "Apr MD peak", "8-min furnace lag", "VERIFIED"),
            ("Furnace holding cut", "Delay holding hrs", "Holding SOP", "PENDING"),
            ("Tariff window import", "Peak grid draw", "Dispatch nudge", "IN REVIEW"),
        ],
        "math": {
            "eyebrow": "Where steel electricity cost usually hides",
            "h2": "Where we look first in steel",
            "ledeD": "Avoidable ₹ on a steel HT bill, starting with furnace and mill loads.",
            "ledeM": "Avoidable ₹ on a steel HT bill.",
            "cards": [
                (
                    "MD / demand",
                    ["Furnace + mill coincidence", "Auxiliary bank overlap", "Contract demand headroom"],
                    "Bill line · MD (kVA)",
                    "Sample: furnace restart and rolling-mill bite at 07:15",
                ),
                (
                    "Process heat",
                    ["Furnace holding loads", "Reheat setback gaps", "Unnecessary preheat windows"],
                    "Bill line · Energy (kWh)",
                    "Sample: holding heat across a long delay with no cast tag",
                ),
                (
                    "Idle loads",
                    ["Utilities across delays", "Compressor unload with no roll", "Cooling pumps run-on"],
                    "Bill line · Energy (kWh)",
                    "Sample: compressor bank unload with zero mill production",
                ),
                (
                    "Air / utilities",
                    ["Unload hours", "Staging discipline", "Simultaneous bank starts"],
                    "Bill line · Energy + MD",
                    "Sample: two utility banks starting into the same demand window",
                ),
                (
                    "Tariff dispatch",
                    ["Peak import timing", "Captive / grid mix", "TOU mistiming"],
                    "Bill line · ToD energy",
                    "Sample: peak grid draw while captive capacity sits idle",
                ),
            ],
        },
        "techBullet": "MD coincidence, furnace holding, mill idle, compressed air, tariff dispatch",
        "offerLedeD": "Start with one melt shop or rolling line. Audit the data, run prescriptions on the floor, then go or no-go at Day 60: on ₹ savings and plant fit.",
        "offerLedeM": "One melt or roll line. Audit → floor → go / no-go at Day 60.",
    },
    "pharma": {
        "label": "Pharma",
        "docTitle": "Stamped Energy · Pharma demo",
        "chromeHint": "Pharma",
        "title": {
            "eyebrowD": "Pharma · load management and HVAC decisions verified on the bill",
            "eyebrowM": "Pharma · load management, verified",
            "h1D": "Chiller and HVAC load, priced onto the bill.",
            "h1M": "Load management ₹ actions on the bill.",
            "ledeD": "Pharma sites run chillers, HVAC, and batch utilities around the clock. Stamped ranks the fix in rupees and checks it on the next DISCOM bill.",
            "ledeM": "Load management for chillers, HVAC, and batch utilities. Verified on the DISCOM bill.",
        },
        "hook": {
            "eyebrow": "Monday 07:05 · Utilities handover",
            "h2": "Your plant already logs this. Nobody owns the fix.",
            "ledeD": "Chillers and autoclave overlapped. EMS logged it. No work order went out.",
            "ledeM": "Chillers and autoclave overlapped. No work order went out.",
            "t1s": "Chillers and autoclave start together",
            "t1p": "Shift B brings heavy utilities online in the same window.",
            "t2s": "MD spike hits the incomer",
            "t2p": "EMS threshold crossed. Alert created. Still no assigned owner.",
            "t3s": "Batch schedule continues as usual",
            "t3p": "The bill will price this later. The floor never saw the fix.",
            "meterNote": "The EMS recorded the spike, but nobody was assigned to change the next utility sequence.",
            "statImpact": "₹36k",
            "statImpactLabel": "Monthly demand impact",
        },
        "gapHas": {
            "scada": "Has: AHU, chiller, batch utility states",
            "ems": "Has: load spike logged at 07:05",
            "meters": "Has: MD window and HVAC load profile",
            "bill": "Has: MD, energy, PF line items",
        },
        "whatLede": "Stamped sits on top of the EMS and EnMS you already run. It reads HVAC, chiller, and batch utility data, finds load-management and idle-waste opportunities, issues a ranked action in rupees, and closes the result on the next bill.",
        "whatStep1": "HVAC, chiller, and batch utility meters, BMS and PLC states, and utility line items. Read-only. No control writes to the plant.",
        "rx1": {
            "badge": "Rx · Load management",
            "aria": "Stagger chillers and autoclave. Show evidence.",
            "action": "Stagger chillers and autoclave by 10 minutes",
            "why": "They started together and pushed MD over the limit",
            "bill": "MD (kVA)",
            "owner": "Utilities supervisor · Shift B",
            "impact": "₹1.8-3.2L / month",
            "effort": "Sequence change · no new equipment",
            "rule": "md_overlap@v2.4 · High",
            "due": "This week",
            "evTitle": "Signal window · Mon 07:00-07:15",
            "tags": [
                ("HT_INCOMER.MD", "920 kVA", "07:06-07:10"),
                ("CHILLER_B.START", "TRUE", "07:02"),
                ("AUTOCLAVE.HEAT", "ON", "07:05+"),
                ("AHU_SUITE3.RUN", "ON", "07:04+"),
            ],
            "cite": "physics/md_overlap@v2.4 · model conf 0.90 · tariff MD slab · baseline Apr peak week",
        },
        "rx2": {
            "badge": "Rx · HVAC idle",
            "aria": "Turn down idle suite HVAC. Show evidence.",
            "action": "Turn down Suite 3 HVAC when no batch is running",
            "why": "Full HVAC with no batch on 4 of last 6 idle windows",
            "bill": "Energy (kWh)",
            "owner": "HVAC / engineering · Suite 3",
            "impact": "₹70k-1.1L / month",
            "effort": "Validated setback · no new equipment",
            "rule": "hvac_idle@v1.5 · High",
            "due": "Next idle window",
            "evTitle": "Idle suite windows · last 6 events",
            "tags": [
                ("AHU_S3.RUN", "Full duty", "40 min avg"),
                ("BATCH.OCCUPANCY", "0", "same window"),
                ("AHU_S3.kWh", "95 kWh", "per event"),
                ("IDLE_WINDOW.FLAG", "TRUE", "validated"),
            ],
            "cite": "physics/hvac_idle@v1.5 · model conf 0.86 · ToD energy line · baseline last 6 idle windows",
        },
        "floor": [
            {
                "title": "Stagger chillers and autoclave by 10 min",
                "why": "MD peak from Monday load overlap",
                "impact": "₹1.8-3.2L/mo on MD line",
                "owner": "Utilities supervisor · B",
                "priority": "High",
                "due": "This week · before next peak",
            },
            {
                "title": "Set back AHU Suite 3 in idle window",
                "why": "Full duty HVAC with no batch occupancy",
                "impact": "₹0.7-1.4L/mo on energy",
                "owner": "HVAC lead · A",
                "priority": "High",
                "due": "Next idle window",
            },
            {
                "title": "Stage utility island off across changeover",
                "why": "Non-critical loads left on between batches",
                "impact": "₹0.5-1.1L/mo on energy",
                "owner": "Utilities supervisor · B",
                "priority": "Med",
                "due": "Next changeover",
            },
        ],
        "verify": [
            ("MD stagger · chiller/autoclave", "Apr MD peak", "10-min chiller lag", "VERIFIED"),
            ("AHU Suite 3 setback", "Idle suite hours", "Setback SOP", "PENDING"),
            ("Tariff window import", "Peak grid draw", "Dispatch nudge", "IN REVIEW"),
        ],
        "math": {
            "eyebrow": "Where pharma electricity cost usually hides",
            "h2": "Where we look first in pharma",
            "ledeD": "Avoidable ₹ on a pharma HT bill: load, idle HVAC, tariff, early warnings.",
            "ledeM": "Load management, HVAC & chillers, idle utilities, tariff, and early warnings before breakdowns.",
            "cards": [
                (
                    "Load management",
                    ["Chiller + autoclave overlap", "AHU bank coincidence", "Contract demand headroom"],
                    "Bill line · MD (kVA)",
                    "Sample: chillers and autoclave heat-up in the same window",
                ),
                (
                    "HVAC & chillers",
                    ["Idle-suite overcool", "Chiller staging discipline", "Unload / bypass hours"],
                    "Bill line · Energy + MD",
                    "Sample: Suite HVAC at full duty with no batch; second chiller into the same peak",
                ),
                (
                    "Utilities & idle loads",
                    ["Non-critical loads left on", "Changeover utility islands", "Idle CIP / WIP holding"],
                    "Bill line · Energy (kWh)",
                    "Sample: utility island left running across an idle window",
                ),
                (
                    "Tariff & intensity",
                    ["Peak import timing", "kWh per batch drift", "TOU mistiming"],
                    "Bill + batch tag",
                    "Sample: peak grid draw during a non-critical utility window",
                ),
                (
                    "Early warnings",
                    ["Catch drift before a breakdown", "Compressed-air / utility leaks", "Repair signal before the trip"],
                    "Ops + bill impact",
                    "Sample: rising specific power and leak signature flagged before a chiller trip",
                ),
            ],
        },
        "techBullet": "Load management, HVAC & chillers, idle utilities, tariff intensity, early fault warnings",
        "offerLedeD": "Start with one HVAC / utilities island or production block. Audit the data, run prescriptions on the floor, then go or no-go at Day 60: on ₹ savings and plant fit.",
        "offerLedeM": "One utilities island. Audit → floor → go / no-go at Day 60.",
    },
}


HERO_CSS = """
    .hero-photo {
      margin: 0;
      border-radius: var(--radius-lg);
      border: 1px solid var(--outline-variant);
      overflow: hidden;
      background: var(--surface-low);
      box-shadow: 0 18px 40px -28px rgba(5,31,19,0.18);
      position: relative;
    }
    .hero-photo img {
      display: block;
      width: 100%;
      height: 100%;
      min-height: 220px;
      max-height: none;
      object-fit: cover;
      object-position: center;
    }
    /* ponytail: no bottom scrim - it read as a broken/wrong image block */
    .hero-photo__scrim { display: none !important; }
    .industry-chip {
      display: inline-flex; align-items: center;
      font-size: 0.68rem; font-weight: 700; letter-spacing: 0.08em;
      text-transform: uppercase; color: var(--tertiary);
      background: color-mix(in srgb, var(--tertiary) 10%, var(--white));
      border: 1px solid color-mix(in srgb, var(--tertiary) 28%, transparent);
      padding: 0.28rem 0.55rem; border-radius: 999px;
      margin-bottom: var(--space-3);
    }
    #chromeIndustry {
      font-size: 0.72rem; font-weight: 650; letter-spacing: 0.04em;
      color: var(--on-surface-variant); margin-left: 0.55rem;
      padding-left: 0.55rem; border-left: 1px solid var(--outline-variant);
      text-transform: uppercase;
    }

"""

MOBILE_HERO_CSS = """
      /* Title: text → Begin → photo, fills the first screen */
      #scene-title.slide {
        justify-content: flex-start;
        overflow: hidden;
        padding-top: calc(var(--chrome-h) + var(--progress-h) + var(--safe-t) + 1.1rem);
        padding-bottom: max(4.75rem, calc(var(--safe-b) + 4.25rem));
      }
      #scene-title .slide__inner {
        width: 100%;
        min-height: 0;
        height: 100%;
        display: flex;
        flex-direction: column;
        transform: none !important;
        animation: none !important;
      }
      #scene-title .hero-shell {
        width: 100%;
        flex: 1;
        min-height: 0;
        display: flex;
        flex-direction: column;
        gap: 0.85rem;
        align-items: stretch;
        justify-content: flex-start;
      }
      #scene-title .hero-copy {
        width: 100%;
        max-width: 100%;
        margin: 0;
        flex: 0 0 auto;
      }
      #scene-title .hero-canvas { display: none !important; }
      #scene-title .hero-photo {
        flex: 1 1 auto;
        min-height: 140px;
        margin-top: 0.15rem;
        display: flex;
        flex-direction: column;
      }
      #scene-title .hero-photo img {
        flex: 1 1 auto;
        min-height: 140px;
        height: 100%;
        max-height: none;
        aspect-ratio: auto;
      }
      #scene-title .brand-name {
        font-size: clamp(2.15rem, 9.5vw, 2.75rem);
        margin-bottom: 0.45rem;
        line-height: 0.95;
      }
      #scene-title h1 {
        font-size: clamp(1.05rem, 4.4vw, 1.25rem);
        font-weight: 650;
        max-width: 18em;
        margin-bottom: 0.5rem;
        line-height: 1.3;
      }
      #scene-title .lede {
        font-size: 0.88rem;
        line-height: 1.35;
        margin-bottom: 0.85rem;
        max-width: 32em;
        color: var(--on-surface-variant);
      }
      #scene-title .btn-row {
        margin-top: 0;
        margin-bottom: 0.15rem;
        width: 100%;
        max-width: 20rem;
      }
      #scene-title .btn {
        width: 100%;
        height: 48px;
        font-size: 1rem;
      }
      #scene-title .industry-chip { margin-bottom: 0.45rem; }
      #scene-title .reveal {
        opacity: 1 !important;
        transform: none !important;
        animation: none !important;
      }

      /* Prescriptions: breathing room + readable action titles */
      #scene-prescription.slide {
        padding-left: max(1.55rem, calc(var(--safe-l) + 0.35rem));
        padding-right: max(1.55rem, calc(var(--safe-r) + 0.35rem));
      }
      #scene-prescription .eyebrow {
        color: var(--primary);
        opacity: 1;
      }
      #scene-prescription .lede {
        margin-bottom: 0.85rem;
      }
      #scene-prescription .rx-layout {
        width: 100%;
        max-width: 100%;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      #scene-prescription .rx-flip {
        width: 100%;
        max-width: 100%;
        margin: 0;
        box-sizing: border-box;
      }
      #scene-prescription .rx-flip__inner,
      #scene-prescription .rx-face {
        box-sizing: border-box;
        max-width: 100%;
      }
      #scene-prescription .rx-hero__head {
        padding: 0.75rem 1.1rem;
      }
      #scene-prescription .rx-hero__body {
        padding: 1rem 1.15rem 1.15rem;
      }
      #scene-prescription .rx-action {
        font-size: 1.08rem;
        line-height: 1.32;
        margin: 0 0 0.85rem;
        padding: 0;
      }
      #scene-prescription .rx-row {
        grid-template-columns: 72px 1fr;
        gap: 0.5rem;
        font-size: 0.82rem;
      }
      #scene-prescription .rx-row:nth-child(n+6) { display: none; }
      #scene-prescription .rx-flip-cue {
        margin-top: 0.85rem;
        font-weight: 650;
      }
      #scene-prescription h2 {
        font-size: clamp(1.25rem, 5.5vw, 1.55rem);
        max-width: 14em;
      }
"""


def rx_tags_html(tags: list[tuple[str, str, str]]) -> str:
    rows = []
    for code, val, window in tags:
        rows.append(
            f"<tr><td><code>{code}</code></td><td>{val}</td><td>{window}</td></tr>"
        )
    return "\n                      ".join(rows)


def waste_cards_html(cards: list) -> str:
    parts = []
    for title, bullets, bill, sample in cards:
        lis = "\n".join(f"              <li>{b}</li>" for b in bullets)
        parts.append(
            f"""          <article class="waste-card">
            <h3>{title}</h3>
            <ul>
{lis}
            </ul>
            <div class="waste-bill">{bill}</div>
            <p class="waste-sample hide-mobile">{sample}</p>
          </article>"""
        )
    return "\n".join(parts)


def verify_rows_html(rows: list[tuple[str, str, str, str]]) -> str:
    out = []
    for a, b, c, d in rows:
        out.append(
            f"""              <tr>
                <td>{a}</td>
                <td>{b}</td>
                <td>{c}</td>
                <td>{d}</td>
              </tr>"""
        )
    return "\n".join(out)


def inject_css(html: str) -> str:
    # desktop hero grid stays; add photo styles after .hero-canvas svg rule
    html = html.replace(
        ".hero-canvas svg { width: 100%; height: auto; aspect-ratio: 420 / 280; display: block; }",
        ".hero-canvas svg { width: 100%; height: auto; aspect-ratio: 420 / 280; display: block; }\n"
        + HERO_CSS,
    )
    # Replace the old mobile title block with the new photo-first layout
    pattern = re.compile(
        r"/\* Title: content starts in upper third, full width, no dead top \*/.*?/\* Floor: proper phone",
        re.S,
    )
    repl = MOBILE_HERO_CSS + "\n      /* Floor: proper phone"
    html, n = pattern.subn(repl, html, count=1)
    if n != 1:
        raise SystemExit(f"mobile title CSS block not replaced (n={n})")
    return html


def inject_chrome_industry(html: str) -> str:
    # After chrome logo block, add industry label
    old = '<div class="chrome-logo" id="chromeLogo">'
    # find closing of chrome-logo div is complex; instead insert after sceneCounter sibling area
    # Insert industry span inside chrome next to logo
    html = html.replace(
        '<span class="chrome-fallback">Stamped</span>\n      </div>',
        '<span class="chrome-fallback">Stamped</span>\n      </div>\n'
        '      <span id="chromeIndustry" aria-live="polite"></span>',
        1,
    )
    return html


def inject_hero_photo(html: str, industry: str) -> str:
    # Add industry chip + photo; keep SVG for desktop as secondary (hide via CSS preference: show photo instead)
    # Replace hero-copy opening content to add chip after brand area
    html = html.replace(
        '<p class="eyebrow reveal hide-mobile">Operational energy decisions, verified on the bill</p>\n'
        '            <p class="eyebrow reveal show-mobile">Bill-verified decisions</p>\n'
        '            <p class="brand-name reveal">Stamped Energy</p>\n'
        '            <h1 class="reveal hide-mobile">From plant meters to bill-line actions.</h1>\n'
        '            <h1 class="reveal show-mobile">Owned ₹ actions on the bill.</h1>\n'
        '            <p class="lede reveal hide-mobile">You already have meters and EMS. Stamped ranks floor work in rupees, then checks the result on the next DISCOM bill.</p>\n'
        '            <p class="lede reveal show-mobile">Ranked floor actions from your meters and EMS. Verified on the DISCOM bill.</p>',
        '<p class="industry-chip reveal" id="industryChip">Industry</p>\n'
        '            <p class="eyebrow reveal hide-mobile" id="titleEyebrowD">Operational energy decisions, verified on the bill</p>\n'
        '            <p class="eyebrow reveal show-mobile" id="titleEyebrowM">Bill-verified decisions</p>\n'
        '            <p class="brand-name reveal">Stamped Energy</p>\n'
        '            <h1 class="reveal hide-mobile" id="titleH1D">From plant meters to bill-line actions.</h1>\n'
        '            <h1 class="reveal show-mobile" id="titleH1M">Owned ₹ actions on the bill.</h1>\n'
        '            <p class="lede reveal hide-mobile" id="titleLedeD">You already have meters and EMS. Stamped ranks floor work in rupees, then checks the result on the next DISCOM bill.</p>\n'
        '            <p class="lede reveal show-mobile" id="titleLedeM">Ranked floor actions from your meters and EMS. Verified on the DISCOM bill.</p>',
        1,
    )

    # Use path relative to the HTML file (no ./ and no query) for max compatibility
    src = HERO_BY_INDUSTRY[industry].lstrip("./")
    alt = HERO_ALT[industry]
    # ponytail: never fall back to how-it-works-poster (cement dashboard UI)
    photo_block = f"""
          <figure class="hero-photo reveal" id="heroPhoto">
            <img
              id="heroPhotoImg"
              src="{src}"
              alt="{alt}"
              width="1800"
              height="1200"
              loading="eager"
              decoding="async"
              fetchpriority="high"
            />
          </figure>"""

    # Insert photo before hero-canvas; keep canvas for desktop optional - hide canvas with CSS on all sizes in favor of photo
    html = html.replace(
        '<div class="hero-canvas reveal hide-mobile" aria-hidden="true">',
        photo_block + '\n          <div class="hero-canvas reveal hide-mobile" aria-hidden="true" hidden>',
        1,
    )
    # Preload so the hero is requested immediately
    if '<link rel="preload" as="image"' not in html:
        html = html.replace(
            "</title>",
            f'</title>\n  <link rel="preload" as="image" href="{src}" />',
            1,
        )
    return html


def inject_ids_and_hooks(html: str) -> str:
    replacements = [
        (
            '<p class="eyebrow reveal">Monday 07:15 · Shift handover</p>\n'
            '        <h2 class="reveal">Your plant already logs this. Nobody owns the fix.</h2>\n'
            '        <p class="lede reveal hide-mobile">MD spiked. EMS logged it. No work order went out.</p>\n'
            '        <p class="lede reveal show-mobile">MD spiked. EMS logged it. No work order went out.</p>',
            '<p class="eyebrow reveal" id="hookEyebrow">Monday 07:15 · Shift handover</p>\n'
            '        <h2 class="reveal" id="hookH2">Your plant already logs this. Nobody owns the fix.</h2>\n'
            '        <p class="lede reveal hide-mobile" id="hookLedeD">MD spiked. EMS logged it. No work order went out.</p>\n'
            '        <p class="lede reveal show-mobile" id="hookLedeM">MD spiked. EMS logged it. No work order went out.</p>',
        ),
        (
            '<strong>Compressors + furnace bay start together</strong>\n'
            '                <p class="hide-mobile">Shift B brings utilities online together.</p>',
            '<strong id="hookT1s">Compressors + furnace bay start together</strong>\n'
            '                <p class="hide-mobile" id="hookT1p">Shift B brings utilities online together.</p>',
        ),
        (
            '<strong>MD spike hits the incomer</strong>\n'
            '                <p class="hide-mobile">Alert created. Still no owner.</p>',
            '<strong id="hookT2s">MD spike hits the incomer</strong>\n'
            '                <p class="hide-mobile" id="hookT2p">Alert created. Still no owner.</p>',
        ),
        (
            '<strong>Production continues as usual</strong>\n'
            '                <p class="hide-mobile">The floor never saw the fix.</p>',
            '<strong id="hookT3s">Production continues as usual</strong>\n'
            '                <p class="hide-mobile" id="hookT3p">The floor never saw the fix.</p>',
        ),        (
            "<strong>₹42k</strong>\n"
            '                <span>Monthly demand impact</span>',
            '<strong id="hookStatImpact">₹42k</strong>\n'
            '                <span id="hookStatImpactLabel">Monthly demand impact</span>',
        ),
        (
            '<div class="has">Has: run states, starts, setpoints</div>',
            '<div class="has" id="gapScadaHas">Has: run states, starts, setpoints</div>',
        ),
        (
            '<div class="has">Has: spike logged at 07:15</div>',
            '<div class="has" id="gapEmsHas">Has: spike logged at 07:15</div>',
        ),
        (
            '<div class="has">Has: MD window and load profile</div>',
            '<div class="has" id="gapMetersHas">Has: MD window and load profile</div>',
        ),
        (
            '<div class="has">Has: MD, energy, PF line items</div>',
            '<div class="has" id="gapBillHas">Has: MD, energy, PF line items</div>',
        ),
        (
            "<p>Incomer, sub-meters, SCADA and PLC states, and utility line items. Read-only. No control writes to the plant.</p>",
            '<p id="whatStep1">Incomer, sub-meters, SCADA and PLC states, and utility line items. Read-only. No control writes to the plant.</p>',
        ),
        (
            '<p class="lede reveal show-mobile">Audit → floor execution → go / no-go at Day 60.</p>',
            '<p class="lede reveal show-mobile" id="offerLedeM">Audit → floor execution → go / no-go at Day 60.</p>',
        ),
    ]
    for old, new in replacements:
        if old not in html:
            raise SystemExit(f"missing fragment for ID injection:\n{old[:120]}...")
        html = html.replace(old, new, 1)
    if 'id="techPhysicsBullet"' not in html:
        raise SystemExit("techPhysicsBullet id missing from base tech card")
    return html


def replace_rx_block(html: str, pack: dict) -> str:
    r1, r2 = pack["rx1"], pack["rx2"]
    # Replace first rx-action and fields via unique current strings - do after generic IDs
    # Wrap rx sections with ids by replacing the whole two buttons' key lines

    def patch_rx(html: str, which: str, r: dict, action_old: str) -> str:
        if action_old not in html:
            raise SystemExit(f"rx action not found: {action_old}")
        html = html.replace(
            f'<p class="rx-action">{action_old}</p>',
            f'<p class="rx-action" id="{which}Action">{r["action"]}</p>',
            1,
        )
        return html

    # We'll rebuild prescription + floor + verify + math from pack after marking containers
    # Find waste-grid and replace inner cards
    m = re.search(
        r'(<div class="waste-grid reveal">)(.*?)(</div>\s*<div class="bill-table-wrap)',
        html,
        re.S,
    )
    if not m:
        raise SystemExit("waste-grid not found")
    html = html[: m.start(1)] + m.group(1) + "\n" + waste_cards_html(pack["math"]["cards"]) + "\n        " + m.group(3) + html[m.end(3) :]

    # verify tbody
    m = re.search(
        r'(<div class="ledger-wrap reveal">\s*<table class="ledger-table">\s*<thead>.*?</thead>\s*<tbody>)(.*?)(</tbody>)',
        html,
        re.S,
    )
    if not m:
        raise SystemExit("ledger tbody not found")
    html = html[: m.start(2)] + "\n" + verify_rows_html(pack["verify"]) + "\n            " + html[m.start(3) :]

    # math headers
    html = html.replace(
        '<p class="eyebrow reveal">Where electricity cost usually hides</p>\n'
        '        <h2 class="reveal">Where we look first</h2>\n'
        '        <p class="lede reveal">Avoidable ₹ on the HT bill, starting with these lines.</p>',
        f'<p class="eyebrow reveal" id="mathEyebrow">{pack["math"]["eyebrow"]}</p>\n'
        f'        <h2 class="reveal" id="mathH2">{pack["math"]["h2"]}</h2>\n'
        f'        <p class="lede reveal" id="mathLede">{pack["math"].get("ledeM") or pack["math"].get("ledeD")}</p>',
        1,
    )

    # Prescription card 1 - replace whole first button front+back key content by unique block
    rx1_front = f'''                  <span class="rx-badge" id="rx1Badge">{r1["badge"]}</span>
                  <span class="rx-priority">Priority · High</span>
                </div>
                <div class="rx-hero__body">
                  <p class="rx-action" id="rx1Action">{r1["action"]}</p>
                  <dl class="rx-fields">
                    <div class="rx-row"><dt>Why</dt><dd id="rx1Why">{r1["why"]}</dd></div>
                    <div class="rx-row"><dt>Bill line</dt><dd id="rx1Bill">{r1["bill"]}</dd></div>
                    <div class="rx-row"><dt>Owner</dt><dd id="rx1Owner">{r1["owner"]}</dd></div>
                    <div class="rx-row"><dt>Impact</dt><dd><strong id="rx1Impact">₹{r1["impact"].replace("₹", "") if r1["impact"].startswith("₹") else r1["impact"]}</strong></dd></div>
                    <div class="rx-row"><dt>Effort</dt><dd id="rx1Effort">{r1["effort"]}</dd></div>
                    <div class="rx-row"><dt>Rule</dt><dd id="rx1Rule">{r1["rule"]}</dd></div>
                    <div class="rx-row"><dt>Due</dt><dd id="rx1Due">{r1["due"]}</dd></div>
                  </dl>'''

    # Fix impact - packs already include ₹
    impact1 = r1["impact"] if r1["impact"].startswith("₹") else "₹" + r1["impact"]
    rx1_front = rx1_front.replace(
        f'<strong id="rx1Impact">₹{r1["impact"].replace("₹", "") if r1["impact"].startswith("₹") else r1["impact"]}</strong>',
        f'<strong id="rx1Impact">{impact1}</strong>',
    )

    old_rx1_front = '''                  <span class="rx-badge">Rx · MD coincidence</span>
                  <span class="rx-priority">Priority · High</span>
                </div>
                <div class="rx-hero__body">
                  <p class="rx-action">Stagger Compressors 1 &amp; 3 vs furnace-bay start by ≥8 min at Shift B handover</p>
                  <dl class="rx-fields">
                    <div class="rx-row"><dt>Why</dt><dd>Mon 07:12-07:20 overlap drove the incomer MD window</dd></div>
                    <div class="rx-row"><dt>Bill line</dt><dd>MD (kVA) · billing demand</dd></div>
                    <div class="rx-row"><dt>Owner</dt><dd>Electrical shift supervisor · Shift B</dd></div>
                    <div class="rx-row"><dt>Impact</dt><dd><strong>₹2.5-4L / month</strong></dd></div>
                    <div class="rx-row"><dt>Effort</dt><dd>Sequence only · no capex · no PLC write</dd></div>
                    <div class="rx-row"><dt>Rule</dt><dd>md_overlap@v2.4 · Confidence High</dd></div>
                    <div class="rx-row"><dt>Due</dt><dd>This week · verify on next MD line</dd></div>
                  </dl>'''
    if old_rx1_front not in html:
        raise SystemExit("rx1 front not found")
    html = html.replace(old_rx1_front, rx1_front, 1)

    html = html.replace(
        'aria-label="MD stagger prescription. Show evidence."',
        f'aria-label="{r1["aria"]}"',
        1,
    )

    old_rx1_back_table = '''                    <tbody>
                      <tr><td><code>HT_INCOMER.MD</code></td><td>1,180 kVA</td><td>07:14-07:18</td></tr>
                      <tr><td><code>COMP1.RUN</code></td><td>ON</td><td>07:12+</td></tr>
                      <tr><td><code>COMP3.RUN</code></td><td>ON</td><td>07:13+</td></tr>
                      <tr><td><code>FURNACE_BAY.START</code></td><td>TRUE</td><td>07:14</td></tr>
                    </tbody>'''
    new_rx1_back_table = (
        "                    <tbody>\n                      "
        + rx_tags_html(r1["tags"])
        + "\n                    </tbody>"
    )
    html = html.replace(old_rx1_back_table, new_rx1_back_table, 1)
    html = html.replace(
        '<p class="rx-ev-title">Signal window · Mon 07:10-07:22</p>',
        f'<p class="rx-ev-title" id="rx1EvTitle">{r1["evTitle"]}</p>',
        1,
    )
    html = html.replace(
        '<p class="rx-cite"><strong>physics/md_overlap@v2.4</strong> · model conf 0.91 · tariff MD slab · baseline Apr peak week</p>',
        f'<p class="rx-cite" id="rx1Cite"><strong>{r1["cite"].split(" · ")[0] if " · " in r1["cite"] else r1["cite"]}</strong> · {" · ".join(r1["cite"].split(" · ")[1:])}</p>'
        if False
        else f'<p class="rx-cite" id="rx1Cite">{r1["cite"]}</p>',
        1,
    )

    # rx2
    impact2 = r2["impact"] if r2["impact"].startswith("₹") else "₹" + r2["impact"]
    old_rx2_front = '''                  <span class="rx-badge">Rx · Idle / holding</span>
                  <span class="rx-priority rx-priority--med">Priority · Med</span>
                </div>
                <div class="rx-hero__body">
                  <p class="rx-action">Stage Compressor Bank B offline during the planned 45-min changeover window</p>
                  <dl class="rx-fields">
                    <div class="rx-row"><dt>Why</dt><dd>Unload kWh with no production tag on 3 of last 5 changeovers</dd></div>
                    <div class="rx-row"><dt>Bill line</dt><dd>Energy (kWh) · ToD shoulder</dd></div>
                    <div class="rx-row"><dt>Owner</dt><dd>Utilities supervisor · Line 2</dd></div>
                    <div class="rx-row"><dt>Impact</dt><dd><strong>₹80k-1.2L / month</strong></dd></div>
                    <div class="rx-row"><dt>Effort</dt><dd>Staging SOP · no capex · no PLC write</dd></div>
                    <div class="rx-row"><dt>Rule</dt><dd>idle_hold@v1.8 · Confidence High</dd></div>
                    <div class="rx-row"><dt>Due</dt><dd>Next changeover · verify on energy line</dd></div>
                  </dl>'''
    new_rx2_front = f'''                  <span class="rx-badge" id="rx2Badge">{r2["badge"]}</span>
                  <span class="rx-priority rx-priority--med">Priority · Med</span>
                </div>
                <div class="rx-hero__body">
                  <p class="rx-action" id="rx2Action">{r2["action"]}</p>
                  <dl class="rx-fields">
                    <div class="rx-row"><dt>Why</dt><dd id="rx2Why">{r2["why"]}</dd></div>
                    <div class="rx-row"><dt>Bill line</dt><dd id="rx2Bill">{r2["bill"]}</dd></div>
                    <div class="rx-row"><dt>Owner</dt><dd id="rx2Owner">{r2["owner"]}</dd></div>
                    <div class="rx-row"><dt>Impact</dt><dd><strong id="rx2Impact">{impact2}</strong></dd></div>
                    <div class="rx-row"><dt>Effort</dt><dd id="rx2Effort">{r2["effort"]}</dd></div>
                    <div class="rx-row"><dt>Rule</dt><dd id="rx2Rule">{r2["rule"]}</dd></div>
                    <div class="rx-row"><dt>Due</dt><dd id="rx2Due">{r2["due"]}</dd></div>
                  </dl>'''
    if old_rx2_front not in html:
        raise SystemExit("rx2 front not found")
    html = html.replace(old_rx2_front, new_rx2_front, 1)
    html = html.replace(
        'aria-label="Idle compressor prescription. Show evidence."',
        f'aria-label="{r2["aria"]}"',
        1,
    )
    old_rx2_table = '''                    <tbody>
                      <tr><td><code>BANK_B.RUN</code></td><td>ON · unload</td><td>45 min avg</td></tr>
                      <tr><td><code>LINE2.PROD</code></td><td>0 units</td><td>same window</td></tr>
                      <tr><td><code>BANK_B.kWh</code></td><td>210 kWh</td><td>per event</td></tr>
                      <tr><td><code>CHANGEOVER.FLAG</code></td><td>TRUE</td><td>planned</td></tr>
                    </tbody>'''
    new_rx2_table = (
        "                    <tbody>\n                      "
        + rx_tags_html(r2["tags"])
        + "\n                    </tbody>"
    )
    html = html.replace(old_rx2_table, new_rx2_table, 1)
    html = html.replace(
        '<p class="rx-ev-title">Changeover windows · last 5 events</p>',
        f'<p class="rx-ev-title" id="rx2EvTitle">{r2["evTitle"]}</p>',
        1,
    )
    html = html.replace(
        '<p class="rx-cite"><strong>physics/idle_hold@v1.8</strong> · model conf 0.87 · ToD energy line · baseline last 5 changeovers</p>',
        f'<p class="rx-cite" id="rx2Cite">{r2["cite"]}</p>',
        1,
    )

    # floor bubble - first of 3 interactive prescriptions (rest via __FLOOR_RX__)
    floors = pack["floor"]
    if not isinstance(floors, list) or len(floors) != 3:
        raise SystemExit("pack['floor'] must be a list of 3 prescriptions")
    f = floors[0]
    old_floor = '''                        <span class="tag" id="floorTag">Alarm · High</span>
                        <h4 id="floorTitle">Stagger Comp 1 &amp; 3 vs furnace bay ≥8 min</h4>
                        <div class="wa-bubble__divider" aria-hidden="true"></div>
                        <p class="wa-line" id="floorWhy"><b>Alarm:</b> MD peak Mon 07:12-07:20 · Comp 1 &amp; 3 overlapped furnace bay</p>
                        <p class="wa-line" id="floorImpact"><b>Impact:</b> ₹2.5-4L/mo on MD line</p>
                        <p class="wa-line" id="floorOwner"><b>Owner:</b> Electrical shift supervisor · B</p>
                        <p class="wa-line" id="floorDue"><b>Due:</b> This week · before next peak</p>'''
    new_floor = f'''                        <span class="tag" id="floorTag">Alarm · {f.get("priority", "High")}</span>
                        <h4 id="floorTitle">{f["title"]}</h4>
                        <div class="wa-bubble__divider" aria-hidden="true"></div>
                        <p class="wa-line" id="floorWhy"><b>Alarm:</b> {f["why"]}</p>
                        <p class="wa-line" id="floorImpact"><b>Impact:</b> {f["impact"]}</p>
                        <p class="wa-line" id="floorOwner"><b>Owner:</b> {f["owner"]}</p>
                        <p class="wa-line" id="floorDue"><b>Due:</b> {f.get("due", "This week · before next peak")}</p>'''
    if old_floor not in html:
        raise SystemExit("floor bubble not found")
    html = html.replace(old_floor, new_floor, 1)
    return html


def apply_static_pack_fields(html: str, pack: dict) -> str:
    t = pack["title"]
    h = pack["hook"]
    html = html.replace(
        "<title>Stamped Energy - Demo Deck</title>",
        f"<title>{pack['docTitle']}</title>",
        1,
    )
    pairs = {
        "industryChip": pack["label"],
        "titleEyebrowD": t["eyebrowD"],
        "titleEyebrowM": t["eyebrowM"],
        "titleH1D": t["h1D"],
        "titleH1M": t["h1M"],
        "titleLedeD": t["ledeD"],
        "titleLedeM": t["ledeM"],
        "hookEyebrow": h["eyebrow"],
        "hookH2": h["h2"],
        "hookLedeD": h["ledeD"],
        "hookLedeM": h["ledeM"],
        "hookT1s": h["t1s"],
        "hookT1p": h["t1p"],
        "hookT2s": h["t2s"],
        "hookT2p": h["t2p"],
        "hookT3s": h["t3s"],
        "hookT3p": h["t3p"],
        "hookStatImpact": h["statImpact"],
        "gapScadaHas": pack["gapHas"]["scada"],
        "gapEmsHas": pack["gapHas"]["ems"],
        "gapMetersHas": pack["gapHas"]["meters"],
        "gapBillHas": pack["gapHas"]["bill"],
        "whatStep1": pack["whatStep1"],
        "techPhysicsBullet": pack["techBullet"],
        "offerLedeM": pack["offerLedeM"],
    }
    for eid, text in pairs.items():
        # replace >old</ or content between id="eid">...</
        pattern = re.compile(
            rf'(id="{eid}"[^>]*>)(.*?)(</)',
            re.S,
        )
        html, n = pattern.subn(rf"\g<1>{text}\g<3>", html, count=1)
        if n != 1:
            raise SystemExit(f"failed to set #{eid} (n={n})")

    # hookStatImpactLabel allows HTML
    pattern = re.compile(
        r'(id="hookStatImpactLabel"[^>]*>)(.*?)(</)',
        re.S,
    )
    html, n = pattern.subn(
        rf'\g<1>{h["statImpactLabel"]}\g<3>', html, count=1
    )
    if n != 1:
        raise SystemExit("hookStatImpactLabel failed")

    # chrome industry via JS still; also set a data attribute on html
    html = html.replace(
        "<html lang=\"en\">",
        f'<html lang="en" data-industry="{pack["label"].lower()}">',
        1,
    )
    return html


def inject_boot_script(html: str, industry: str) -> str:
    hero_rel = HERO_BY_INDUSTRY[industry].lstrip("./")
    floor_rx = json.dumps(PACKS[industry]["floor"], ensure_ascii=False)
    boot = f"""
  <script>
    /* Industry chrome + floor prescriptions + resolve hero against this HTML file's URL */
    window.__FLOOR_RX__ = {floor_rx};
    (function () {{
      var el = document.getElementById("chromeIndustry");
      if (el) el.textContent = {json.dumps(PACKS[industry]["chromeHint"])};
      var img = document.getElementById("heroPhotoImg");
      if (!img) return;
      var rel = {json.dumps(hero_rel)};
      var resolved = new URL(rel, window.location.href).href;
      if (img.src !== resolved) img.src = resolved;
      img.addEventListener("error", function onHeroErr() {{
        img.removeEventListener("error", onHeroErr);
        // one retry with cache-bust - still the local industry photo, never the cement poster
        img.src = new URL(rel + "?t=" + Date.now(), window.location.href).href;
      }});
    }})();
  </script>
"""
    html = html.replace("<script>\n    (function () {\n      const isMobileDeck", boot + "<script>\n    (function () {\n      const isMobileDeck", 1)
    return html


def build_one(base_html: str, industry: str) -> str:
    pack = PACKS[industry]
    html = base_html
    html = html.replace("__INDUSTRY__", industry)
    html = inject_css(html)
    html = inject_chrome_industry(html)
    html = inject_hero_photo(html, industry)
    html = inject_ids_and_hooks(html)
    html = replace_rx_block(html, pack)
    html = apply_static_pack_fields(html, pack)
    html = inject_boot_script(html, industry)
    # desktop: prefer photo over SVG - hide canvas always when photo present
    html = html.replace(
        "#scene-title .hero-shell {\n"
        "      display: grid;\n"
        "      grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);\n"
        "      gap: clamp(1.75rem, 4.5vw, 3.25rem);\n"
        "      align-items: center;\n"
        "    }",
        "#scene-title .hero-shell {\n"
        "      display: grid;\n"
        "      grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);\n"
        "      gap: clamp(1.75rem, 4.5vw, 3.25rem);\n"
        "      align-items: center;\n"
        "    }\n"
        "    #scene-title .hero-canvas[hidden] { display: none !important; }\n"
        "    #scene-title .hero-photo {\n"
        "      align-self: stretch;\n"
        "      min-height: 0;\n"
        "      height: 100%;\n"
        "      max-height: min(62vh, 520px);\n"
        "      display: flex;\n"
        "    }\n"
        "    #scene-title .hero-photo img {\n"
        "      flex: 1 1 auto;\n"
        "      width: 100%;\n"
        "      height: 100%;\n"
        "      min-height: 320px;\n"
        "      max-height: none;\n"
        "      object-fit: cover;\n"
        "      object-position: center;\n"
        "    }",
        1,
    )
    return html


HUB = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>Stamped Energy · Industry demo decks</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@700;800&display=swap" rel="stylesheet" />
  <style>
    :root {
      --primary: #F75440; --secondary: #051F13; --surface: #f7faf5;
      --on-surface: #191c1a; --muted: #5a403c; --line: #e3beb8;
      --font-d: "Plus Jakarta Sans", system-ui, sans-serif;
      --font-b: Inter, system-ui, sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; min-height: 100dvh; font-family: var(--font-b);
      color: var(--on-surface); background:
        radial-gradient(1200px 600px at 10% -10%, rgba(247,84,64,0.12), transparent 55%),
        radial-gradient(900px 500px at 100% 0%, rgba(0,102,107,0.08), transparent 50%),
        var(--surface);
      padding: max(1.5rem, env(safe-area-inset-top)) 1.25rem max(2rem, env(safe-area-inset-bottom));
    }
    main { max-width: 720px; margin: 0 auto; }
    .logo { height: 36px; width: auto; margin-bottom: 1.25rem; }
    h1 {
      font-family: var(--font-d); font-weight: 800; letter-spacing: -0.04em;
      font-size: clamp(1.8rem, 5vw, 2.4rem); line-height: 1.05; margin: 0 0 0.65rem;
      color: var(--secondary);
    }
    .lede { color: var(--muted); line-height: 1.5; margin: 0 0 1.75rem; max-width: 36em; }
    .grid { display: grid; gap: 0.85rem; }
    a.card {
      display: block; text-decoration: none; color: inherit;
      background: #fff; border: 1px solid var(--line); border-radius: 14px;
      padding: 1.15rem 1.25rem; transition: border-color 0.15s, transform 0.15s;
    }
    a.card:hover { border-color: var(--primary); transform: translateY(-1px); }
    a.card strong {
      display: block; font-family: var(--font-d); font-size: 1.2rem;
      margin-bottom: 0.35rem; color: var(--secondary);
    }
    a.card span { display: block; color: var(--muted); font-size: 0.92rem; line-height: 1.4; }
    a.card em {
      display: inline-block; margin-top: 0.75rem; font-style: normal;
      font-size: 0.8rem; font-weight: 700; color: var(--primary);
    }
    footer { margin-top: 2rem; font-size: 0.85rem; color: var(--muted); }
    footer a { color: var(--secondary); }
  </style>
</head>
<body>
  <main>
    <img class="logo" src="https://stamped.work/LogoOrange.png" alt="Stamped Energy" width="140" height="36" />
    <h1>Pick your industry deck</h1>
    <p class="lede">Same Proof Run walkthrough: prescriptions, data sources, and optimisation targets tuned for each plant type.</p>
    <div class="grid">
      <a class="card" href="./cement.html">
        <strong>Cement</strong>
        <span>Kiln, mills, WHR dispatch, and kWh/ton: MD and peak-grid actions.</span>
        <em>Open cement deck →</em>
      </a>
      <a class="card" href="./steel.html">
        <strong>Steel</strong>
        <span>Furnace holding, rolling-mill coincidence, and melt-shop utilities.</span>
        <em>Open steel deck →</em>
      </a>
      <a class="card" href="./pharma.html">
        <strong>Pharma</strong>
        <span>Load management, chillers, HVAC setbacks, and batch-utility peaks.</span>
        <em>Open pharma deck →</em>
      </a>
    </div>
    <footer>
      <a href="https://stamped.work">stamped.work</a>
      · Demo decks for first meetings / Proof Run
    </footer>
  </main>
</body>
</html>
"""


def main() -> None:
    # Prefer regenerating from a snapshot if present; else current index if it's still the generic deck
    snapshot = DECKS_DIR / "_base.snapshot.html"
    if snapshot.exists():
        base = snapshot.read_text(encoding="utf-8")
    else:
        base = BASE.read_text(encoding="utf-8")
        # Save snapshot of pre-industry base once
        if "data-industry=" not in base and "hero-photo" not in base:
            snapshot.write_text(base, encoding="utf-8")
        elif "hero-photo" in base:
            raise SystemExit(
                "index.html already transformed and no _base.snapshot.html - restore base first"
            )

    for industry in ("cement", "steel", "pharma"):
        out = build_one(base, industry)
        path = DECKS_DIR / f"{industry}.html"
        path.write_text(out, encoding="utf-8")
        print(f"wrote {path} ({len(out)} bytes)")
        # Standalone Vercel root: demo-decks/<industry>/index.html
        if industry == "pharma":
            deploy_dir = DECKS_DIR / "pharma"
            deploy_dir.mkdir(parents=True, exist_ok=True)
            deploy_index = deploy_dir / "index.html"
            # Tech deep-dives live in demo-decks/tech/; rewrite relative links from pharma/
            deploy_html = out.replace('href="tech/', 'href="../tech/')
            deploy_index.write_text(deploy_html, encoding="utf-8")
            print(f"wrote {deploy_index} ({len(deploy_html)} bytes)")

    hub = HUB
    (DECKS_DIR / "index.html").write_text(hub, encoding="utf-8")
    (ROOT / "index.html").write_text(
        hub.replace('href="./cement.html"', 'href="./demo-decks/cement.html"')
        .replace('href="./steel.html"', 'href="./demo-decks/steel.html"')
        .replace('href="./pharma.html"', 'href="./demo-decks/pharma.html"'),
        encoding="utf-8",
    )
    print("wrote hubs")


if __name__ == "__main__":
    main()
