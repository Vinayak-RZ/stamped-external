import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

// Thin smoke — logic mirrored for CJS-free test without ts loader
function countByStatus(detections) {
  return {
    emitted: detections.filter((d) => d.status === "emitted").length,
    suppressed: detections.filter((d) => d.status === "suppressed").length,
    shadow_only: detections.filter((d) => d.status === "shadow_only").length,
  };
}

test("countByStatus tallies statuses", () => {
  const c = countByStatus([
    { status: "emitted" },
    { status: "suppressed" },
    { status: "shadow_only" },
    { status: "emitted" },
  ]);
  assert.equal(c.emitted, 2);
  assert.equal(c.suppressed, 1);
  assert.equal(c.shadow_only, 1);
});
