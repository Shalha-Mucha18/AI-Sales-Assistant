# AI Sales Assistant

An **AI-powered sales intelligence prototype** that orchestrates multiple autonomous agents to analyze business data and generate **actionable insights** in real time.
The system ingests B2B or retail sales data, performs **Descriptive**, **Diagnostic**, **Predictive**, and **Prescriptive** analytics,  producing **executive-ready recommendations** through an interactive, conversational interface.
## Overview
This prototype demonstrates how **Agentic AI systems** can empower businesses with continuous intelligence. By connecting data analytics with autonomous reasoning agents, the assistant provides **real-time decision support**, enabling companies to:
- Understand **what happened** in sales performance  
- Diagnose **why it happened**  
- Predict **what will happen next**  
- Recommend **what actions should be taken**
  
This type of system can be integrated into existing ERP, CRM, or BI dashboards to deliver **AI-driven business insights** that traditionally require manual analyst intervention.
# 🎥 Video Demonstration
[![AI Sales Assistant Demo](https://img.shields.io/badge/Watch_Demo-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://drive.google.com/file/d/1nJ-RCQ5Y2O12Q1eZkkZ5pz-nUI0jneY9/view?usp=drive_link)
*Click the badge above to watch the full demonstration video*


## How It Works
Here, users upload their **sales data (CSV or Excel)** and ask natural-language queries such as:

> “Why did revenue drop last month?”  
> “Forecast next quarter by category.”  
> “Recommend strategies to improve margins.”
A team of specialized AI agents collaborates to analyze, reason, and respond intelligently.

You can use this dataset for testing purposes: https://drive.google.com/file/d/1Ee9kMYOjCWSf4pwg5HnqZi90JZcliR71/view?usp=sharing

## 👥 The Multi-Agent System
Each agent in the system has a **distinct role and responsibility**, coordinated through the CrewAI framework:
| Agent | Role | Responsibility |
|--------|------|----------------|
| **Analyst Agent** | Descriptive & Diagnostic Analytics | Summarizes KPIs, trends, and performance drivers |
| **Forecaster Agent** | Predictive Analytics | Uses statistical and ML-based forecasting for future performance |
| **Advisor Agent** | Prescriptive Analytics | Recommends strategic actions to improve revenue and margins |
| **Assistant Agent** | Conversational Orchestration | Interprets user queries, coordinates other agents, and generates final executive summaries |

Together, they form a **collaborative agent ecosystem**, where each agent’s reasoning contributes to a unified, context-aware business insight.
## 🚀 Key Features

- **Multi-Agent Collaboration** – Autonomous agents work together to analyze, forecast, and recommend actions.  
- **Four-Tier Analytics** – Delivers Descriptive, Diagnostic, Predictive, and Prescriptive insights.  
- **Conversational BI** – Users interact naturally with the system — no data expertise required.  
- **Real-Time Visualization** – Generates KPI summaries, charts, and trend insights instantly.  
- **Enterprise Value** – Helps companies detect sales anomalies, optimize pricing, forecast demand, and cut BI workload by up to 70%.  
## Project Layout
```
├── src/
│   └── sales_agents/
│       ├── __init__.py
│       ├── main.py
│       ├── crew.py
│       ├── analytics/
│       │   ├── descriptive.py
│       │   ├── predictive.py
│       │   └── prescriptive.py
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── data/
│       │   └── demo_sales.csv
│       ├── memory/
│       │   └── kb.py
│       ├── tools/
│       │   └── custom_tool.py
│       └── utils/
│           ├── intent.py
│           ├── schema.py
│           └── viz.py
├── pyproject. toml
├── README.md
└── uv.lock
```
## Getting Started
1. Install UV (if not already installed):
```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
      # Or using pip:
      # pip install uv
```
2. Clone and set up the project:
```bash 
    git clone https://github.com/Shalha-Mucha18/AI-Sales-Assistant.git
    cd AI-Sales-Assistant
```
3. Install dependencies:
```bash
    uv sync
```
4. Create and set up environment variables: via `.env`:
```env
  GROQ_API_KEY=your-key-here
```
5. Launch the Streamlit interface:
```bash
  uv run streamlit run src/sales_agents/main.py
```
## Configuration
- Adjust agent personas in `config/agents.yaml`.
- Modify task expectations in `config/tasks.yaml`.
- Swap in your own seed dataset by replacing `data/demo_sales.csv`.

## Extensibility

Implement additional utilities inside `src/my_project/tools/` and expose them through `tools/__init__.py`. Agents can call these helpers to augment reasoning or report generation.

---
Built with ❤️ for data-driven operators.
