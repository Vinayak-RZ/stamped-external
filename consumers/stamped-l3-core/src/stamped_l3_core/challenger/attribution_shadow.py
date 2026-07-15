"""Attribution shadow challengers — Lab-only (ADR-016).

Ranking ablations + STUMPY motif stub. Never stages to L4 outbox.
ponytail: no stumpy dependency required; motif uses plain correlation of series tails.
"""

from __future__ import annotations

from typing import Any


def _rank_by(
    candidates: list[dict[str, Any]],
    *,
    key_fn,
) -> list[dict[str, Any]]:
    return sorted(candidates, key=key_fn, reverse=True)


def ranking_ablations(
    candidates: list[dict[str, Any]],
    *,
    primary_asset: str | None,
) -> list[dict[str, Any]]:
    """Return shadow detection kwargs for LabLog.add_detection."""
    if not candidates:
        return []
    out: list[dict[str, Any]] = []

    def _emit(method: str, ranked: list[dict[str, Any]]) -> None:
        top = ranked[0]
        agree = primary_asset is None or top.get("asset") == primary_asset
        out.append(
            {
                "detection_id": f"shadow-{method}-{top.get('asset', 'x')}",
                "detector_kind": "ml_shadow",
                "rule_or_model_ref": f"shadow://attribution/{method}",
                "category": "md_overlap",
                "status": "shadow_only",
                "scores": {
                    "shadow_method": method,
                    "agree_with_primary": agree,
                    "primary_rank_ref": primary_asset,
                    "rank": 1,
                    "asset": top.get("asset"),
                    "score": top.get("score"),
                    "corr_abs": top.get("corr_abs"),
                },
                "logs": [f"ADR-016 ablation {method}; agree={agree}"],
            }
        )

    # corr-primary: sort by correlation then score
    _emit(
        "rank_ablation_corr_primary",
        _rank_by(candidates, key_fn=lambda c: (c.get("corr_abs") or 0, c.get("score") or 0)),
    )
    # flat proximity: score = ramp_kw only
    flat = [{**c, "score": c.get("ramp_kw") or 0} for c in candidates]
    _emit("rank_ablation_flat_proximity", _rank_by(flat, key_fn=lambda c: c.get("score") or 0))
    # wider window flag — candidates already filtered; re-rank by score (placeholder mark)
    _emit(
        "rank_ablation_wider_window",
        _rank_by(candidates, key_fn=lambda c: c.get("score") or 0),
    )
    return out


def stumpy_motif_shadow(
    candidates: list[dict[str, Any]],
    *,
    primary_asset: str | None,
    series: list[float] | None = None,
    motif: list[float] | None = None,
) -> dict[str, Any] | None:
    """Shape concordance stub — abs-corr of series tail vs motif when both provided.

    Without series/motif, emits informational shadow with agree=None-like False.
    """
    if not candidates:
        return None
    agree = False
    corr = None
    if series and motif and len(series) >= len(motif) >= 2:
        # pep: minimal cosine/pearson-ish via centered corr
        n = len(motif)
        a = series[-n:]
        mean_a = sum(a) / n
        mean_b = sum(motif) / n
        num = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, motif))
        den_a = sum((x - mean_a) ** 2 for x in a) ** 0.5
        den_b = sum((y - mean_b) ** 2 for y in motif) ** 0.5
        corr = (num / (den_a * den_b)) if den_a and den_b else 0.0
        # high motif match on primary's expected shape → agree if primary still top by score
        top = max(candidates, key=lambda c: c.get("score") or 0)
        agree = bool(corr >= 0.8 and top.get("asset") == primary_asset)
    else:
        top = max(candidates, key=lambda c: c.get("score") or 0)
        agree = top.get("asset") == primary_asset
    return {
        "detection_id": f"shadow-stumpy_motif-{primary_asset or 'x'}",
        "detector_kind": "ml_shadow",
        "rule_or_model_ref": "shadow://attribution/stumpy_motif",
        "category": "md_overlap",
        "status": "shadow_only",
        "scores": {
            "shadow_method": "stumpy_motif",
            "agree_with_primary": agree,
            "primary_rank_ref": primary_asset,
            "motif_corr": corr,
        },
        "logs": ["ADR-016 STUMPY motif stub (no stumpy dep); Lab-only"],
    }


def emit_attribution_shadows(
    candidates: list[dict[str, Any]],
    *,
    series: list[float] | None = None,
    motif: list[float] | None = None,
) -> list[dict[str, Any]]:
    if not candidates:
        return []
    primary = max(candidates, key=lambda c: c.get("score") or 0).get("asset")
    rows = ranking_ablations(candidates, primary_asset=primary)
    motif_row = stumpy_motif_shadow(
        candidates, primary_asset=primary, series=series, motif=motif
    )
    if motif_row:
        rows.append(motif_row)
    return rows
