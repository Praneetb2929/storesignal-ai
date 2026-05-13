# StoreSignal — Technical Document

## System architecture

Three layers:

1. **Data ingestion** — pulls product data from Shopify Admin API
   into a normalised ProductContext object
2. **AI simulation engine** — runs LLM calls simulating buyer personas,
   measures confidence, hallucination, and drift
3. **Scoring + generation** — weighted gap scoring, impact ranking,
   LLM-powered copy rewrites

## Components

### schema.py — shared data contracts
Single source of truth for all data shapes. Both ingestion and
simulation import from here. Prevents integration bugs.

Key types: ProductContext, SimulationResult, Gap, GapReport

### ingestion/shopify.py — Shopify data fetcher
Calls Shopify Admin GraphQL API. Pulls products, variants, policies,
FAQs, reviews. Normalises into ProductContext.
Mock version (mock_shopify.py) used for demo — identical interface.

### simulation/agent.py — AI simulation core
- simulate_one(): asks one buyer question, parses structured response
- simulate_all(): runs all 4 personas × 3 questions = 12 total
- measure_drift(): asks same question 5 ways, scores consistency
- run_drift_analysis(): runs drift across 3 question topics

Hallucination detection: AI evidence claim checked against source text.
If evidence not found in source — flagged as hallucination.

### scoring/scorer.py — gap scorer
Weighted scoring across 5 dimensions:
- Query coverage (35%) — % of questions answered confidently
- Hallucination risk (25%) — rate of unsupported claims
- Policy clarity (25%) — confidence on policy questions
- Answer consistency (15%) — inverse of drift score

Gaps sorted by severity. High severity = immediate action needed.

### generation/suggester.py — copy rewriter
Per-dimension prompts generate targeted rewrites.
Each prompt is tuned to the specific failure mode of that dimension.

### main.py — FastAPI server
4 endpoints:
- GET / — health check
- GET /products — list all product IDs
- GET /analyse/{id} — full simulation + scoring
- GET /fixes/{id} — full analysis + rewrite generation

CORS enabled for localhost:3000.

## Failure handling

| Failure | Behaviour |
|---------|-----------|
| LLM returns malformed response | Confidence defaults to 0.5, evidence to "none" |
| Confidence parse fails | Falls back to 0.5 |
| Drift consistency parse fails | Falls back to 0.5 (neutral) |
| Fix generation fails | Returns error string, doesn't crash report |
| Product not found | 404 HTTP response |
| Shopify API down | Falls back to mock data |

## AI vs deterministic boundary

- **Deterministic**: data fetching, response parsing, score calculation,
  gap severity classification, API routing
- **LLM**: buyer question answering, consistency scoring, copy rewriting

We drew this line deliberately. Scoring is deterministic so results
are reproducible and explainable. LLM is used only where
human-language understanding is genuinely needed.

## Known limitations

- Analysis takes ~45 seconds (12 simulation + 15 drift + generation calls)
- Hallucination detection is approximate (string matching, not semantic)
- Mock data doesn't reflect real merchant store diversity
- No caching — re-runs full analysis each time

## What we would improve with more time

- Semantic hallucination detection using embeddings
- Result caching (Redis) to avoid re-running unchanged products
- Real Shopify OAuth flow for one-click merchant onboarding
- Batch analysis across all products in a store
- Historical score tracking to show improvement over time