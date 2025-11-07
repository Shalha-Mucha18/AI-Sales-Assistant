import re

INTENT_KEYWORDS = {
    "descriptive": [
        "what happened", "summary", "summarize", "describe", "overview",
        "kpi", "trend", "totals", "top", "bottom", "compare", "by region",
        "by category", "by segment", "share", "contribution"
    ],
    "diagnostic": [
        "why", "reason", "cause", "root cause", "driver", "impact", "effect",
        "correlat", "variance", "decline", "drop", "increase", "spike", "anomaly"
    ],
    "predictive": [
        "forecast", "predict", "projection", "likely", "next month", "next quarter",
        "future", "expected"
    ],
    "prescriptive": [
        "what should", "recommend", "action", "optimize", "improve", "strategy",
        "promotion", "pricing", "stock", "inventory", "campaign"
    ]
}

def detect_intents(user_query: str):
    q = user_query.lower()
    hits = []
    for intent, kws in INTENT_KEYWORDS.items():
        for kw in kws:
            if kw in q:
                hits.append(intent)
                break
    return list(set(hits)) or ["descriptive"]
