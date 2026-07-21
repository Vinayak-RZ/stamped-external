import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { claimBadgeLabel, formatInr } from "../src/lib/format";
import {
  assertTenantMatch,
  visibleContextChips,
} from "../src/lib/analyst-context";
import type { AnalystContextEnvelope } from "../src/lib/types";

describe("formatInr", () => {
  it("uses en-IN grouping", () => {
    const s = formatInr(214000);
    assert.match(s, /2,14,000|214,000/);
  });
});

describe("claimBadgeLabel", () => {
  it("labels ops_confirmed distinctly", () => {
    assert.equal(claimBadgeLabel("ops_confirmed").label, "Ops-confirmed");
  });
  it("labels modeled with bill disclaimer", () => {
    assert.match(claimBadgeLabel("modeled").label, /not bill-verified/i);
  });
});

describe("analyst context", () => {
  const base: AnalystContextEnvelope = {
    orgId: "org_demo",
    plantId: "plant_a",
    userId: "u1",
    role: "supervisor",
    routeId: "alarms",
    screenTitle: "EMS alarm console",
    focusEntity: { type: "alarm", id: "alm_1" },
    visibleSummary: ["critical open"],
  };

  it("builds removable chips", () => {
    const chips = visibleContextChips(base);
    assert.ok(chips.some((c) => c.value === "EMS alarm console"));
    assert.ok(chips.some((c) => c.value === "alarm:alm_1"));
  });

  it("honours excludeKeys", () => {
    const chips = visibleContextChips({ ...base, excludeKeys: ["focus", "summary:0"] });
    assert.ok(!chips.some((c) => c.key === "focus"));
    assert.ok(!chips.some((c) => c.value === "critical open"));
  });

  it("rejects cross-tenant focus plant", () => {
    assert.equal(assertTenantMatch(base, "plant_other"), false);
    assert.equal(assertTenantMatch(base, "plant_a"), true);
  });
});
