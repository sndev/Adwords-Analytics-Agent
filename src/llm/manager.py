"""Fit-for-purpose LLM routing.

Workload is small (thousands of tokens/day). Architecture:
  - ETL / number crunching: deterministic code (no LLM) => $0
  - cheap model: keyword/negative extraction, summaries
  - strong model: optimization decisions (rare, high-stakes)
  - per-run cost cap enforced here
"""
import os
import time
from typing import Any, Callable, Dict, Optional

from ..config_loader import settings

_SUPPORTED = ("none", "gemini-flash", "gemini-pro", "openai-gpt4o-mini", "claude-haiku", "claude-sonnet", "groq-llama")


def _tier(name: str) -> Dict[str, Any]:
    llm = settings().get("llm", {})
    return {"model": llm.get(name, "none"), "tier": name}


def route(task: str) -> str:
    """Return the configured model for a task type (etl/cheap/mid/strong)."""
    if task in ("etl", "format", "metrics"):
        return "none"
    if task in ("keywords", "negatives", "summary"):
        return _tier("cheap_model")["model"]
    if task in ("rsa", "adcopy"):
        return _tier("mid_model")["model"]
    if task in ("optimize", "bidding", "budget", "decision"):
        return _tier("strong_model")["model"]
    return _tier("cheap_model")["model"]


def cost_cap() -> float:
    return float(settings().get("llm", {}).get("per_run_cost_cap_usd", 0.05))


class BudgetTracker:
    def __init__(self) -> None:
        self.spent = 0.0
        self.calls = 0

    def check(self, est_cost: float) -> bool:
        return self.spent + est_cost <= cost_cap()

    def record(self, est_cost: float) -> None:
        self.spent += est_cost
        self.calls += 1


def generate(prompt: str, task: str, budget: Optional[BudgetTracker] = None) -> Optional[str]:
    """Run the chosen model for `task`, respecting the per-run cost cap.

    Providers are pluggable; returns None when model=none or cost cap exceeded.
    """
    model = route(task)
    if model == "none":
        return None
    tracker = budget or BudgetTracker()
    est = 0.0005  # rough cost estimate for a short prompt/response
    if not tracker.check(est):
        return None
    # Placeholder for provider SDK call — wire to Google Gemini / OpenAI / Anthropic keyed by model.
    # raise NotImplementedError(f"LLM provider not wired for model={model}")
    return None