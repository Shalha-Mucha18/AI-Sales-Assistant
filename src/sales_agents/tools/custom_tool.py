from __future__ import annotations

import pandas as pd


def revenue_growth_summary(df: pd.DataFrame) -> str:
    """Return a short natural-language summary of month-over-month revenue growth."""
    df_local = df.copy()
    df_local["Date"] = pd.to_datetime(df_local["Date"])
    monthly = df_local.groupby(pd.Grouper(key="Date", freq="MS"))["Revenue"].sum().sort_index()
    if len(monthly) < 2:
        return "Not enough history to compute revenue growth."

    last_period, prev_period = monthly.iloc[-1], monthly.iloc[-2]
    pct_change = ((last_period - prev_period) / prev_period) * 100 if prev_period else 0.0
    trend = "increased" if pct_change >= 0 else "decreased"
    return (
        f"Revenue {trend} by {abs(pct_change):.1f}% from {monthly.index[-2].strftime('%Y-%m')} "
        f"to {monthly.index[-1].strftime('%Y-%m')}."
    )


__all__ = ["revenue_growth_summary"]
