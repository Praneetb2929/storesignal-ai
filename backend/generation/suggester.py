from groq import Groq
import os
from dotenv import load_dotenv
from schema import ProductContext, Gap

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_fix(product: ProductContext, gap: Gap) -> str:
    """
    Given a product and a specific gap, generate improved copy
    that would fix that gap and score higher with AI agents.
    """

    prompts = {
        "query_coverage": f"""You are an expert ecommerce copywriter.
The following product description is too vague — AI shopping agents cannot answer basic buyer questions from it.

CURRENT DESCRIPTION:
{product.description}

PRODUCT TITLE: {product.title}
VARIANTS: {', '.join(product.variants)}

Rewrite the product description so it clearly answers:
- What is this product made of?
- Who is it for?
- What problem does it solve?
- How does sizing work?
- What makes it better than alternatives?

Write ONLY the new description. 3-5 sentences. Be specific and factual.""",

        "policy_clarity": f"""You are an ecommerce policy writer.
This store has an unclear or missing return/shipping policy that confuses AI shopping agents.

CURRENT RETURN POLICY: {product.return_policy or "Not set"}
CURRENT SHIPPING POLICY: {product.shipping_policy or "Not set"}

Write a clear, plain-English return and shipping policy that covers:
- How many days to return
- What condition items must be in
- Who pays return shipping
- How long refunds take
- Shipping timeframes

Write ONLY the policy text. Be direct and specific.""",

        "answer_consistency": f"""You are an ecommerce content specialist.
AI agents give inconsistent answers about this product because the information is ambiguous.

CURRENT DESCRIPTION: {product.description}
VARIANTS: {', '.join(product.variants)}

Rewrite the variant and sizing information so it is completely unambiguous.
Use clear, direct language. State facts explicitly — never leave anything to interpretation.
Write ONLY the improved content.""",

        "persona_coverage": f"""You are an ecommerce copywriter.
This product listing fails to address gift buyers, budget shoppers, and first-time buyers.

CURRENT DESCRIPTION: {product.description}
TITLE: {product.title}

Add a short FAQ section (4-5 questions) that addresses:
- Is this suitable as a gift?
- What is the price range / value for money?
- What if it doesn't fit or I don't like it?
- How long does delivery take?
- Is this good for first-time buyers?

Write ONLY the FAQ section in Q&A format.""",

        "hallucination_risk": f"""You are an ecommerce content specialist.
AI agents are making up information about this product because key facts are missing.

CURRENT DESCRIPTION: {product.description}
TITLE: {product.title}
VARIANTS: {', '.join(product.variants)}

Rewrite the description to explicitly state all key facts.
Never leave anything implied. If something is true, state it directly.
Write ONLY the improved description.""",
    }

    prompt = prompts.get(gap.dimension, prompts["query_coverage"])

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )

    return response.choices[0].message.content.strip()


def generate_all_fixes(product: ProductContext, gaps: list[Gap]) -> dict[str, str]:
    """Generate fixes for all gaps found in a product."""
    fixes = {}
    for gap in gaps:
        try:
            fixes[gap.dimension] = generate_fix(product, gap)
        except Exception as e:
            fixes[gap.dimension] = f"Could not generate fix: {str(e)}"
    return fixes