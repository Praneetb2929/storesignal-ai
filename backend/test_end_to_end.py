import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ingestion.mock_shopify import fetch_all_product_ids, fetch_product
from backend.simulation.agent import simulate_all, run_drift_analysis
from backend.scoring.scorer import score_product

# ── Test with product 001 (blank return policy — worst case) ──
product = fetch_product("001")
print(f"\nTesting product: {product.title}")
print("=" * 50)

# Run simulation
results = simulate_all(product)
print(f"Total questions asked: {len(results)}")

low_confidence = [r for r in results if r.confidence < 0.5]
print(f"Low confidence answers: {len(low_confidence)}")

hallucinations = [r for r in results if r.is_hallucination]
print(f"Hallucinations detected: {len(hallucinations)}")

print("\n--- Sample low confidence answers ---")
for r in low_confidence[:3]:
    print(f"\nPersona : {r.persona}")
    print(f"Question: {r.question}")
    print(f"Answer  : {r.answer[:150]}")
    print(f"Confidence: {r.confidence}")

# Run drift analysis
print("\n--- Drift Analysis ---")
drift_results = run_drift_analysis(product)
for d in drift_results:
    status = "🔴 HIGH DRIFT" if d["drift_score"] > 0.5 else "🟢 LOW DRIFT"
    print(f"{status} | {d['question_topic'][:50]} | score: {d['drift_score']}")

# Run scorer
print("\n--- Final Score ---")
report = score_product("001", results, drift_results)
print(f"OVERALL SCORE: {report.overall_score} / 100")
print(f"Gaps found: {len(report.gaps)}")
for gap in report.gaps:
    print(f"\n[{gap.severity.upper()}] {gap.dimension}")
    print(f"  Problem : {gap.description[:120]}")
    print(f"  Fix     : {gap.suggested_fix[:120]}")