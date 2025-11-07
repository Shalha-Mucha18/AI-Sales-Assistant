from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import yaml
from crewai import Agent, Crew, Process, Task, LLM
from dotenv import load_dotenv

from sales_agents.analytics.descriptive import AnalyticalEngine
from sales_agents.analytics.predictive import PredictiveEngine
from sales_agents.analytics.prescriptive import PrescriptiveEngine
from sales_agents.memory.kb import SimpleMemory
from sales_agents.utils.intent import detect_intents
from sales_agents.utils.viz import plot_series

load_dotenv()

PACKAGE_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = PACKAGE_ROOT / "config"
DATA_PATH = PACKAGE_ROOT / "data" 



def _load_yaml_config(path: Path) -> Dict[str, Dict[str, str]]:
    """Read YAML configuration or return the provided fallback dictionary."""
    if not path.exists():
        return fallback

    with path.open("r", encoding="utf-8") as handle:
        parsed: Optional[Dict[str, Dict[str, str]]] = yaml.safe_load(handle)
        if not parsed:
            return fallback
    return parsed


class SalesCrewApp:
    """High-level façade wiring together analytical agents and the CrewAI workflow."""

    def __init__(
        self,
        df_override: Optional[pd.DataFrame] = None,
        *,
        data_path: Optional[Path] = None,
        config_dir: Optional[Path] = None,
        llm_temperature: float = 0.7,
        memory_limit: int = 10,
    ) -> None:
        self.data_path = Path(data_path) if data_path  else DATA_PATH
        self.config_dir = Path(config_dir) if config_dir else CONFIG_DIR

        self.agent_blueprints = _load_yaml_config(self.config_dir / "agents.yaml")
        self.task_blueprints = _load_yaml_config(self.config_dir / "tasks.yaml")

        self.df = self._load_dataframe(df_override)
        self.memory = SimpleMemory(max_entries=memory_limit)
        self.llm = LLM(
            model="groq/llama-3.3-70b-versatile",
            temperature=llm_temperature,
            api_key=os.getenv("GROQ_API_KEY"),
        )

        # Core analytical engines
        self.analytical = AnalyticalEngine(self.df)
        self.predictive = PredictiveEngine(self.df)
        self.prescriptive = PrescriptiveEngine()

        # Agents wired with shared memory and config-driven personas
        self.assistant = self._build_agent("assistant")
        self.analyst = self._build_agent("analyst")
        self.forecaster = self._build_agent("forecaster")
        self.advisor = self._build_agent("advisor")

    def _load_dataframe(self, df_override: Optional[pd.DataFrame]) -> pd.DataFrame:
        if df_override is not None:
            return df_override.copy()
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Default data file not found at {self.data_path}. "
                "Provide a dataset via Streamlit upload or place a CSV at that location."
            )
        return pd.read_csv(self.data_path)

    def _build_agent(self, key: str) -> Agent:
        blueprint = self.agent_blueprints.get(key)
        if not blueprint:
            raise KeyError(f"Agent config '{key}' is not defined.")
        return Agent(
            role=blueprint["role"],
            goal=blueprint["goal"],
            backstory=blueprint.get("backstory", ""),
            llm=self.llm,
            memory=self.memory,
        )

    def _build_task(self, key: str, agent: Agent) -> Optional[Task]:
        blueprint = self.task_blueprints.get(key)
        if not blueprint:
            return None
        return Task(
            description=blueprint["description"],
            expected_output=blueprint["expected_output"],
            agent=agent,
        )

    def run_query(self, user_query: str) -> Dict[str, Any]:
        """Execute the end-to-end multi-agent workflow for a given prompt."""
        intents = detect_intents(user_query)
        descriptive = diagnostic = predictive = prescriptive = None
        chart = None

        if "descriptive" in intents or "diagnostic" in intents:
            descriptive = self.analytical.summary_kpis()
            if any(token in user_query.lower() for token in {"trend", "chart", "visualize", "graph", "plot"}):
                trend_series = self.analytical.trend()
                chart = plot_series(trend_series, "Monthly Revenue Trend")

            months = sorted(set(self.analytical.df["Month"]))
            if len(months) >= 2:
                period_a = months[-2].strftime("%Y-%m")
                period_b = months[-1].strftime("%Y-%m")
                diagnostic = self.analytical.drivers(period_a, period_b)
            else:
                diagnostic = {"note": "Not enough data for month-over-month comparison."}

        if "predictive" in intents:
            overall = self.predictive.forecast_monthly(horizon=2)
            by_region = self.predictive.forecast_by_group(group_col="Region", horizon=1)
            predictive = {"overall": overall, "by_region": by_region}

        if "prescriptive" in intents:
            diagnostic_ctx = diagnostic
            descriptive_ctx = descriptive
            if diagnostic_ctx is None or descriptive_ctx is None:
                descriptive_ctx = self.analytical.summary_kpis()
                months = sorted(set(self.analytical.df["Month"]))
                if len(months) >= 2:
                    period_a = months[-2].strftime("%Y-%m")
                    period_b = months[-1].strftime("%Y-%m")
                    diagnostic_ctx = self.analytical.drivers(period_a, period_b)
                else:
                    diagnostic_ctx = {"delta_revenue": 0.0}
            prescriptive = self.prescriptive.recommend(diagnostic_ctx, descriptive_ctx)

        tasks: list[Task] = []
        if descriptive or diagnostic:
            task = self._build_task("descriptive", self.analyst)
            if task:
                tasks.append(task)
        if predictive:
            task = self._build_task("predictive", self.forecaster)
            if task:
                tasks.append(task)
        if prescriptive:
            task = self._build_task("prescriptive", self.advisor)
            if task:
                tasks.append(task)

        crew = Crew(
            agents=[self.assistant, self.analyst, self.forecaster, self.advisor],
            tasks=tasks,
            process=Process.sequential,
            verbose=False,
        )

        context = {
            "user_query": user_query,
            "descriptive": descriptive,
            "diagnostic": diagnostic,
            "predictive": predictive,
            "prescriptive": prescriptive,
        }

        crew_result = crew.kickoff(inputs=context)
        crew_output_text = getattr(crew_result, "output", str(crew_result))
        prompt = f"""
You are an AI Business Intelligence Assistant preparing an executive insight summary.
Multiple analytical agents (Analyst, Forecaster, Advisor) have collaborated to analyze the data below.

User Question:
{user_query}

Your task:
Write a concise, professional 4–6 sentence executive summary that answers the question directly.

Guidelines:
• Begin with a clear statement of overall business performance or trend.
• Present key KPIs (revenue, profit, units sold, average discount) in business context — avoid raw JSON or tables.
• Explain 1–2 key drivers of change (regions, categories, or discounts) that influenced performance.
• If predictive data exists, include 1 short forecast highlight (expected direction or growth rate).
• Provide 2–3 prescriptive, actionable recommendations for management decisions.
• Keep tone factual, confident, and C-suite appropriate — avoid speculation or verbose explanations.

Structured Analytical Context:
DESCRIPTIVE = {descriptive}
DIAGNOSTIC = {diagnostic}
PREDICTIVE = {predictive}
PRESCRIPTIVE = {prescriptive}

Collaborative Agent Summary:
{crew_output_text}

Output format:
A short, well-structured executive paragraph (no bullet points or lists unless explicitly needed).
Avoid repeating field names or raw numbers; focus on insight and implication.
"""


        try:
            answer = self.llm.call(prompt)
        except AttributeError:
            answer = self.llm.run(prompt)

        self.memory.add("user", user_query)
        self.memory.add("assistant", answer)

        return {
            "answer": answer,
            "intents": intents,
            "descriptive": descriptive,
            "diagnostic": diagnostic,
            "predictive": predictive,
            "prescriptive": prescriptive,
            "chart_b64": chart,
            "multiagent_result": crew_output_text,
            "memory_context": self.memory.get_context(),
        }
