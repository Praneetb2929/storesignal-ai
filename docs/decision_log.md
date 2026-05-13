# Decision Log

## Why LLM simulation over rule-based checking
Rule-based checkers can't measure what AI agents actually do.
We chose to run real LLM calls because the problem is about
AI agent behaviour — not a proxy for it.
Tradeoff: higher cost per analysis, slower response time.

## Why Groq + Llama over OpenAI
Free tier, generous limits, fast inference.
Good enough for simulation. Would switch to GPT-4 for production.

## Why we didn't build real-time monitoring
Out of scope for 10 days. Core value is the diagnostic,
not continuous monitoring. Noted as future work.

## Why drift detection matters
Same question phrased differently should get the same answer.
High drift = ambiguous store data. This is unmeasurable with
any rule-based system. It's our core technical differentiator.

## Mock data vs real Shopify
Used mock data to unblock development. Real Shopify ingestion
is identical in structure — swap mock_shopify.py for shopify.py.
The rest of the system doesn't change.