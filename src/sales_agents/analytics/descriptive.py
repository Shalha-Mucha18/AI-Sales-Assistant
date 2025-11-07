from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import pandas as pd

__all__ = ["AnalyticalEngine"]

class AnalyticalEngine:
    """Descriptive & Diagnostic analytics on a sales DataFrame."""
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df["Date"] = pd.to_datetime(self.df["Date"])
        self.df["Month"] = self.df["Date"].dt.to_period("M").dt.to_timestamp()

    def summary_kpis(self, date_from: Optional[str]=None, date_to: Optional[str]=None) -> Dict[str, Any]:
        dff = self._filter_dates(self.df, date_from, date_to)
        kpis = {
            "revenue_total": float(dff["Revenue"].sum()),
            "profit_total": float(dff["Profit"].sum()),
            "units_total": int(dff["Units_Sold"].sum()) if "Units_Sold" in dff else 0,
            "avg_discount": float(dff["Discount"].mean() or 0.0) if "Discount" in dff else 0.0,
            "orders": int(len(dff)),
        }
        top_cat = dff.groupby("Product_Category")["Revenue"].sum().sort_values(ascending=False).head(3)
        top_region = dff.groupby("Region")["Revenue"].sum().sort_values(ascending=False).head(3)
        by_channel = dff.groupby("Sales_Channel")["Revenue"].sum().sort_values(ascending=False) if "Sales_Channel" in dff else None
        kpis["top_categories"] = top_cat.to_dict()
        kpis["top_regions"] = top_region.to_dict()
        if by_channel is not None:
            kpis["by_channel"] = by_channel.to_dict()
        return kpis

    def trend(
        self,
        groupby: str = "Month",
        measure: str = "Revenue",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> pd.Series:
        dff = self._filter_dates(self.df, date_from, date_to)
        if groupby == "Month":
            g = dff.groupby("Month")[measure].sum().sort_index()
        else:
            g = dff.groupby(groupby)[measure].sum().sort_index()
        g.name = measure
        return g

    def drivers(
        self,
        period_a: str,
        period_b: str,
        dims: Tuple[str, ...] = ("Region", "Product_Category"),
    ) -> Dict[str, Any]:
        a = self.df[self.df["Month"] == pd.to_datetime(period_a)]
        b = self.df[self.df["Month"] == pd.to_datetime(period_b)]
        out = {
            "period_a": period_a,
            "period_b": period_b,
            "delta_revenue": float(b["Revenue"].sum() - a["Revenue"].sum()),
        }
        for dim in dims:
            a_dim = a.groupby(dim)["Revenue"].sum()
            b_dim = b.groupby(dim)["Revenue"].sum()
            delta = (b_dim - a_dim).sort_values(ascending=False).fillna(0.0)
            out[f"delta_by_{dim}"] = delta.to_dict()
        if "Discount" in a.columns:
            a_day = a.groupby("Date")[["Revenue", "Discount"]].mean()
            corr = float(a_day["Revenue"].corr(a_day["Discount"]) or 0.0)
            out["corr_discount_revenue_in_A"] = corr
        return out

    def _filter_dates(
        self,
        df: pd.DataFrame,
        date_from: Optional[str],
        date_to: Optional[str],
    ) -> pd.DataFrame:
        dff = df
        if date_from:
            dff = dff[dff["Date"] >= pd.to_datetime(date_from)]
        if date_to:
            dff = dff[dff["Date"] <= pd.to_datetime(date_to)]
        return dff
