from __future__ import annotations

from typing import Any, Dict, List

__all__ = ["PrescriptiveEngine"]


class PrescriptiveEngine:
    """Rule-based prescriptive recommendations using KPI thresholds."""

    def __init__(self, revenue_target_growth: float = 0.05, margin_floor: float = 0.20):
        self.revenue_target_growth = revenue_target_growth
        self.margin_floor = margin_floor

    def recommend(self, diagnostics: Dict[str, Any], latest_kpis: Dict[str, Any]) -> Dict[str, Any]:
        recs: List[str] = []
        delta_rev = diagnostics.get("delta_revenue", 0.0)
        avg_discount = latest_kpis.get("avg_discount", 0.0)
        revenue_total = latest_kpis.get("revenue_total", 0.0)
        profit_total = latest_kpis.get("profit_total", 0.0)

        margin = profit_total / revenue_total if revenue_total else 0.0

        worst_regions = sorted(diagnostics.get("delta_by_Region", {}).items(), key=lambda x: x[1])[:2]
        worst_categories = sorted(diagnostics.get("delta_by_Product_Category", {}).items(), key=lambda x: x[1])[:2]

        if delta_rev < 0:
            if avg_discount < 0.10:
                recs.append("Run a targeted 5% promo in impacted regions/categories for 2 weeks.")
            else:
                recs.append("Use bundled offers instead of deeper discounts to protect margins.")
            if worst_regions:
                recs.append("Focus on regions: " + ", ".join([w[0] for w in worst_regions]) + ".")
            if worst_categories:
                recs.append("Focus on categories: " + ", ".join([w[0] for w in worst_categories]) + ".")

        if margin < self.margin_floor:
            recs.append("Reduce blanket discounting by 2–3% in low-elasticity categories.")

        recs.append(f"Set next-month revenue growth target to {int(self.revenue_target_growth * 100)}%.")

        return {"recommendations": recs, "context": {"delta_revenue": delta_rev, "margin": margin}}
