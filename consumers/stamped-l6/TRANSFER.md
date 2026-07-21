# Transfer manifest — stamped-l6 reference → consumer

Copy/adapt these paths into `Vinayak-RZ/stamped-l6` (do **not** permanently fork contracts; mount `external/`).

| Seed path | Consumer destination | Notes |
|-----------|----------------------|-------|
| `src/styles/tokens.css` | `packages/web/src/styles/tokens.css` | Prefer generating from `external/design/forge-industrial-v2.tokens.yaml` |
| `src/lib/types.ts` | `packages/web/src/lib/types.ts` | Align with OpenAPI when BFF exists |
| `src/lib/format.ts` | same | Keep claim vocabulary |
| `src/lib/analyst-context.ts` | same + BFF validation | Enforce `assertTenantMatch` server-side |
| `src/components/**` | `packages/web/src/components/**` | Replace fixture actions with BFF mutations |
| `src/app/**` | `packages/web/src/app/**` | Add auth layout + RBAC |
| `src/fixtures/demo.ts` | `packages/web/src/fixtures/` + Storybook | Keep for visual regression |
| `tests/**` | `packages/web/tests/` | Expand Playwright per UI charter §17 |

## Do not transfer

- This README’s “platform seed” framing as product docs
- Hard-coded `org_demo` / plant ids into production paths
- Inline `<style>` media queries long-term — move to CSS modules/Tailwind

## Parity checklist

- [ ] Today ≤7 signals
- [ ] More tools reveal persists per user
- [ ] Alarm ack posts Idempotency-Key to L5
- [ ] Rx defer requires reason
- [ ] Mode A chips removable + audited
- [ ] Dual claim badges (ops vs modeled vs reserved bill)
