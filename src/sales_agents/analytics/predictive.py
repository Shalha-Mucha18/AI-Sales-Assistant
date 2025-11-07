from __future__ import annotations

from typing import Any, Dict

import pandas as pd
from sklearn.linear_model import LinearRegression

__all__ = ["PredictiveEngine"]

class PredictiveEngine:
    """Lightweight forecasting using linear regression on monthly totals."""
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df["Date"] = pd.to_datetime(self.df["Date"])
        self.df["Month"] = self.df["Date"].dt.to_period("M").dt.to_timestamp()

    def forecast_monthly(self, measure: str = "Revenue", horizon: int = 1) -> Dict[str, Any]:
        dff = self.df.groupby("Month")[measure].sum().reset_index()
        if len(dff) < 3:
            return {"measure": measure, "forecasts": {}}
        dff["t"] = (dff["Month"] - dff["Month"].min()).dt.days
        X, y = dff[["t"]].values, dff[measure].values
        model = LinearRegression()
        model.fit(X, y)
        last_t = dff["t"].iloc[-1]
        preds = {}
        for h in range(1, horizon + 1):
            t_future = last_t + 30 * h
            yhat = float(model.predict([[t_future]])[0])
            month_future = (dff["Month"].iloc[-1] + pd.offsets.MonthBegin(h)).strftime("%Y-%m")
            preds[month_future] = yhat
        return {"measure": measure, "forecasts": preds}

    def forecast_by_group(
        self,
        group_col: str = "Region",
        measure: str = "Revenue",
        horizon: int = 1,
    ) -> Dict[str, Any]:
        out = {}
        for grp, dfg in self.df.groupby(group_col):
            dff = (
                dfg.groupby(pd.Grouper(key="Date", freq="MS"))[measure]
                .sum()
                .reset_index()
                .rename(columns={"Date": "Month"})
            )
            if len(dff) < 3:
                continue
            dff["t"] = (dff["Month"] - dff["Month"].min()).dt.days
            X, y = dff[["t"]].values, dff[measure].values
            model = LinearRegression()
            model.fit(X, y)
            last_t = dff["t"].iloc[-1]
            preds = {}
            for h in range(1, horizon + 1):
                t_future = last_t + 30 * h
                yhat = float(model.predict([[t_future]])[0])
                month_future = (dff["Month"].iloc[-1] + pd.offsets.MonthBegin(h)).strftime("%Y-%m")
                preds[month_future] = yhat
            out[grp] = preds
        return {"group": group_col, "measure": measure, "forecasts": out}
