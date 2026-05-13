# StoreSignal — Product Document

## Problem

Shopping is shifting from search-and-browse to ask-and-decide.
ChatGPT, Google AI Mode, and Shopify's own Agentic Plan now recommend
products directly inside conversations. Merchants are getting traffic
from these AI channels — but have zero visibility into how AI agents
perceive their store, or why they get skipped in favour of competitors.

The current merchant experience: no dashboard, no diagnostic, no feedback.
A merchant can spend hours perfecting their Shopify listing and still be
invisible to AI shopping agents — because the description is ambiguous,
the return policy is vague, or the product answers 3 out of 12 buyer
questions.

## Who is this for

Primary user: Shopify merchants who sell across AI shopping channels
and want to understand and improve their AI representation.

Secondary user: Shopify agency owners managing multiple stores who want
to audit AI readiness across their portfolio.

## What we built

StoreSignal is an AI readiness diagnostic tool. It simulates how AI
shopping agents parse a merchant's store, measures where they fail,
and generates optimised content rewrites.

### Core user journey
1. Merchant connects their Shopify store
2. Selects a product to analyse
3. StoreSignal runs 12 AI-simulated buyer questions across 4 personas
4. Receives a scored report across 5 readiness dimensions
5. Views specific gaps with severity ratings
6. Gets AI-generated rewrites for every gap — ready to copy into Shopify

## Key product decisions

### Decision 1 — Simulate real AI behaviour, not rules
We chose to run actual LLM calls against store data rather than a
rule-based checker. This measures the real problem: what AI agents
actually do, not a proxy for it.

### Decision 2 — Four buyer personas, not one generic user
Budget shopper, gift buyer, first-time buyer, researcher. Each has
different questions. A store might score 90% for researchers but 40%
for gift buyers. Stratified scoring surfaces this gap.

### Decision 3 — Drift detection
We ask the same question five different ways and measure consistency.
High drift means ambiguous store data — a problem no rule-based system
can detect.

### Decision 4 — Generate fixes, not just flags
We don't just tell merchants what's wrong. We generate an AI-optimised
rewrite for every gap, ready to paste directly into Shopify.

## What we chose NOT to build

- Real-time monitoring (continuous re-analysis) — out of scope, core
  value is the diagnostic not surveillance
- Multi-store portfolio view — useful but not core for v1
- Competitor benchmarking — would require scraping, legal complexity
- Browser extension — distribution complexity for a hackathon

## Tradeoffs

- Mock data vs real Shopify API — used mock data to unblock development.
  Real ingestion is identical in structure, swap one file.
- Groq/Llama vs GPT-4 — chose Groq for free tier. Would use GPT-4
  in production for higher answer quality.
- Speed vs depth — analysis takes ~45 seconds. Acceptable for a
  diagnostic tool used occasionally, not in real time.