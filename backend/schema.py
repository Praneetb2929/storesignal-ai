from pydantic import BaseModel
from typing import Optional

# ── What we pull from Shopify ──────────────────────────────
class ProductContext(BaseModel):
    product_id: str
    title: str
    description: str
    variants: list[str]        # e.g. ["Size: S", "Size: M", "Color: Blue"]
    return_policy: str
    shipping_policy: str
    faqs: list[str]
    reviews_summary: str

# ── What the AI simulator produces per question ────────────
class SimulationResult(BaseModel):
    persona: str               # "budget_shopper" / "gift_buyer" / etc.
    question: str
    answer: str
    confidence: float          # 0.0 to 1.0
    is_hallucination: bool
    evidence: str              # exact text from store that supports answer

# ── One gap found in the store ─────────────────────────────
class Gap(BaseModel):
    dimension: str             # "policy_clarity" / "query_coverage" / etc.
    description: str           # human-readable explanation of the gap
    severity: str              # "high" / "medium" / "low"
    suggested_fix: str         # LLM-generated rewrite

# ── Final report for one product ──────────────────────────
class GapReport(BaseModel):
    product_id: str
    overall_score: float       # 0 to 100
    gaps: list[Gap]
    simulation_results: list[SimulationResult]