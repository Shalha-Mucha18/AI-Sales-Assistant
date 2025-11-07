from __future__ import annotations
import pandas as pd
from typing import Dict, Tuple, List

REQUIRED_COLUMNS = {
    "date": ["date", "order_date", "txn_date", "timestamp"],
    "region": ["region", "area", "territory"],
    "product_category": ["product_category", "category", "productgroup", "product_group"],
    "revenue": ["revenue", "sales_amount", "net_sales", "salesvalue"],
    "profit": ["profit", "gross_profit", "margin_amount"],
}

OPTIONAL_COLUMNS = {
    "customer_segment": ["customer_segment", "segment", "customer_type"],
    "sales_channel": ["sales_channel", "channel"],
    "units_sold": ["units_sold", "qty", "quantity", "units"],
    "discount": ["discount", "discount_rate", "disc"],
}


def normalize_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str], List[str]]:
    original_cols = list(df.columns)
    df = df.copy()
    df.columns = [c.lower().strip().replace(" ", "_") for c in original_cols]

    def match(cands):
        for c in cands:
            if c in df.columns:
                return c
        return None

    column_map = {}
    missing = []

    for canonical, aliases in REQUIRED_COLUMNS.items():
        m = match(aliases)
        if m is None:
            missing.append(canonical)
        else:
            column_map[canonical] = m

    for canonical, aliases in OPTIONAL_COLUMNS.items():
        m = match(aliases)
        if m is not None:
            column_map[canonical] = m

    # rename in place
    for canonical, found in column_map.items():
        if canonical != found:
            df.rename(columns={found: canonical}, inplace=True)

    return df, column_map, missing


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df[df["date"].notna()]
    for col in ["revenue", "profit", "units_sold", "discount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "units_sold" in df.columns:
        df["units_sold"] = df["units_sold"].fillna(0).astype(int)
    if "discount" in df.columns:
        df["discount"] = df["discount"].clip(lower=0, upper=1).fillna(0.0)
    return df


def ensure_full_schema(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["customer_segment", "sales_channel", "units_sold", "discount"]:
        if col not in df.columns:
            if col == "units_sold":
                df[col] = 0
            elif col == "discount":
                df[col] = 0.0
            else:
                df[col] = "Unknown"
    rename_map = {
        "date": "Date",
        "region": "Region",
        "customer_segment": "Customer_Segment",
        "sales_channel": "Sales_Channel",
        "product_category": "Product_Category",
        "units_sold": "Units_Sold",
        "revenue": "Revenue",
        "discount": "Discount",
        "profit": "Profit",
    }
    df = df.rename(columns=rename_map)
    return df.sort_values("Date").reset_index(drop=True)
