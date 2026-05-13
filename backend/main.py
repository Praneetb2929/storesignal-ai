from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingestion.mock_shopify import fetch_product, fetch_all_product_ids
from simulation.agent import simulate_all, run_drift_analysis
from scoring.scorer import score_product
from schema import GapReport, ProductContext
from generation.suggester import generate_all_fixes

app = FastAPI(title="StoreSignal API")

# Allow React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ─────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "StoreSignal API is running"}


# ── Get all product IDs in the store ─────────────────────
@app.get("/products")
def get_products():
    ids = fetch_all_product_ids()
    return {"product_ids": ids}


# ── Run full analysis on one product ─────────────────────
@app.get("/analyse/{product_id}", response_model=GapReport)
def analyse_product(product_id: str):
    # Step 1: fetch product data
    product = fetch_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Step 2: run simulation (AI asks buyer questions)
    simulation_results = simulate_all(product)

    # Step 3: run drift detection
    drift_results = run_drift_analysis(product)

    # Step 4: score everything and return report
    report = score_product(product_id, simulation_results, drift_results)
    return report


# ── Get product basic info (for frontend display) ────────
@app.get("/product/{product_id}")
def get_product_info(product_id: str):
    product = fetch_product(product_id)
    return {
        "product_id": product.product_id,
        "title": product.title,
        "description": product.description,
        "variants": product.variants,
        "return_policy": product.return_policy,
        "shipping_policy": product.shipping_policy,
    }

# ── Generate copy fixes for a product ────────────────────
@app.get("/fixes/{product_id}")
def get_fixes(product_id: str):
    """
    Run full analysis then generate LLM-powered rewrites
    for every gap found.
    """
    # Fetch and analyse
    product = fetch_product(product_id)
    simulation_results = simulate_all(product)
    drift_results = run_drift_analysis(product)
    report = score_product(product_id, simulation_results, drift_results)

    # Generate fixes for each gap
    fixes = generate_all_fixes(product, report.gaps)

    return {
        "product_id": product_id,
        "product_title": product.title,
        "overall_score": report.overall_score,
        "fixes": [
            {
                "dimension": gap.dimension,
                "severity": gap.severity,
                "problem": gap.description,
                "original_content": _get_original(product, gap.dimension),
                "suggested_fix": fixes.get(gap.dimension, gap.suggested_fix),
            }
            for gap in report.gaps
        ]
    }


def _get_original(product: ProductContext, dimension: str) -> str:
    """Return the original content that needs fixing for each dimension."""
    mapping = {
        "query_coverage":     product.description,
        "policy_clarity":     f"Return: {product.return_policy}\nShipping: {product.shipping_policy}",
        "answer_consistency": f"Variants: {', '.join(product.variants)}\n{product.description}",
        "persona_coverage":   product.description,
        "hallucination_risk": product.description,
    }
    return mapping.get(dimension, product.description)