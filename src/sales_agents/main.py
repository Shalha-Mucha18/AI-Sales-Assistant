from __future__ import annotations

from datetime import datetime
from typing import Optional

import pandas as pd
import streamlit as st

if __package__ is None or __package__ == "":  
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[1]))

from sales_agents.crew import SalesCrewApp
from sales_agents.utils.schema import coerce_types, ensure_full_schema, normalize_columns


def configure_page() -> None:
    """Apply Streamlit-level configuration and shared header elements."""
    st.set_page_config(page_title="AI Sales Assistant", layout="wide", page_icon="🧠")
    st.markdown("<h1 style='text-align:center;'>AI Sales Assistant</h1>", unsafe_allow_html=True)
    st.caption("Empowering business intelligence with autonomous multi-agent collaboration")
    st.divider()


def render_sidebar() -> None:
    """Render upload workflow and initialize the application state."""
    with st.sidebar:
        st.header("⚙️ Upload & Initialize")
        st.info("Upload sales data (.csv or .xlsx). Required columns: Date, Region, Product_Category, Revenue, Profit.")
        uploaded = st.file_uploader("📂 Upload your sales data", type=["csv", "xlsx", "xls"])

        if uploaded is not None:
            df_raw = _read_uploaded_file(uploaded)
            if df_raw is not None:
                st.success(f"File '{uploaded.name}' loaded successfully.")
                st.dataframe(df_raw.head(5), use_container_width=True)
                _clean_and_store_dataframe(df_raw)

        st.markdown("---")
        init_clicked = st.button("Activate AI Agents", use_container_width=True, type="primary")

    if init_clicked:
        _initialize_app()


def _read_uploaded_file(uploaded) -> Optional[pd.DataFrame]:
    try:
        if uploaded.name.lower().endswith(".csv"):
            return pd.read_csv(uploaded)
        return pd.read_excel(uploaded)
    except Exception as exc:  
        st.error(f"Failed to read file: {exc}")
        return None


def _clean_and_store_dataframe(df_raw: pd.DataFrame) -> None:
    df_norm, _, missing = normalize_columns(df_raw)
    if missing:
        st.error(f"Missing required logical columns: {missing}")
        return

    df_typed = coerce_types(df_norm)
    df_final = ensure_full_schema(df_typed)

    issues = []
    if df_final["Date"].nunique() < 30:
        issues.append("Less than 30 unique dates — forecasting accuracy may be limited.")
    if (df_final["Revenue"] <= 0).mean() > 0.2:
        issues.append("Over 20% of rows have non-positive revenue — check data quality.")

    if issues:
        st.warning("\n".join(["⚠️ " + msg for msg in issues]))
    else:
        st.success("Data normalized and validated successfully.")

    st.session_state.df_uploaded = df_final


def _initialize_app() -> None:
    dataset = st.session_state.get("df_uploaded")
    st.session_state.app = SalesCrewApp(df_override=dataset) if dataset is not None else SalesCrewApp()
    if dataset is not None:
        st.success("Agents activated — ready to analyze your business.")
    else:
        st.info("Initialized with the bundled demo dataset.")


def render_main_panel() -> None:
    """Render the core analytical workflow once an app instance is available."""
    if "app" not in st.session_state:
        st.warning("⬅Upload a dataset and click **Activate AI Agents** to begin.")
        return
    user_query = st.text_input(
        "Ask a question about your business:",
        placeholder="e.g. Why did revenue drop last month and what should we do?",
    ).strip()

    if st.button("Run Analysis", use_container_width=True, type="primary"):
        if not user_query:
            st.error("Please enter a question for the agents to analyze.")
            return
        _run_analysis(user_query)


def _run_analysis(user_query: str) -> None:
    with st.spinner("Agents analyzing your request..."):
        progress = st.progress(0)
        status_text = st.empty()

        status_text.text("Analyst Agent exploring sales data...")
        progress.progress(25)

        result = st.session_state.app.run_query(user_query)

        status_text.text("Forecaster Agent predicting future trends...")
        progress.progress(50)
        status_text.text("Advisor Agent generating strategic recommendations...")
        progress.progress(75)
        status_text.text("Assistant compiling final report...")
        progress.progress(100)

    st.markdown("Executive Summary")
    st.success(result["answer"])
    st.divider()

    if result.get("descriptive"):
        _render_kpis(result["descriptive"])

    if result.get("chart_b64"):
        st.markdown("Monthly Revenue Trend")
        st.image(result["chart_b64"], caption="Revenue Over Time", use_container_width=True)

    st.markdown("Behind the Scenes: AI Agent Collaboration")
    with st.expander(" Multi-Agent Reasoning Log", expanded=False):
        st.markdown(result.get("multiagent_result", "_No collaboration log available._"))

    st.markdown(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def _render_kpis(kpi: dict) -> None:
    st.markdown("Key Business Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"${kpi['revenue_total'] / 1e6:.2f}M")
    c2.metric("Total Profit", f"${kpi['profit_total'] / 1e6:.2f}M")
    c3.metric("Units Sold", f"{int(kpi['units_total']):,}")
    c4.metric("Avg. Discount", f"{kpi['avg_discount'] * 100:.1f}%")

    st.markdown("**Top Categories:** " + ", ".join(kpi.get("top_categories", {}).keys()))
    st.markdown("**Top Regions:** " + ", ".join(kpi.get("top_regions", {}).keys()))
    st.divider()


def main() -> None:
    configure_page()
    render_sidebar()
    render_main_panel()


if __name__ == "__main__":
    main()
