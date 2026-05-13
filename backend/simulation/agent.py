import os
from groq import Groq
from dotenv import load_dotenv
from schema import ProductContext, SimulationResult

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PERSONAS = {
    "budget_shopper": [
        "Is there a cheaper version of this?",
        "Are there any discounts or coupons?",
        "What is the total price including shipping?",
    ],
    "gift_buyer": [
        "Is this suitable as a gift?",
        "Do you offer gift wrapping?",
        "Can I include a personal message?",
    ],
    "first_time_buyer": [
        "How do I know what size to pick?",
        "What if it doesn't fit — can I return it?",
        "How long will delivery take?",
    ],
    "researcher": [
        "What materials is this made from?",
        "How does this compare to similar products?",
        "What do other customers say about quality?",
    ],
}

DRIFT_QUESTION_SETS = [
    [
        "Can I return this product?",
        "What happens if I want to send this back?",
        "Is there a return policy?",
        "What if I change my mind after buying?",
        "Do you accept returns?",
    ],
    [
        "How long does shipping take?",
        "When will I receive this?",
        "What is the delivery time?",
        "How many days until it arrives?",
        "What's the estimated arrival date?",
    ],
    [
        "What sizes are available?",
        "Do you have this in large?",
        "Can I get this in a different size?",
        "What size options do I have?",
        "Is size M available?",
    ],
]


def simulate_one(product: ProductContext, persona: str, question: str) -> SimulationResult:
    """Ask the AI one question about a product and measure the answer quality."""

    prompt = f"""You are an AI shopping assistant. A customer is asking about a product.
Answer ONLY using the product information provided below.
If you cannot answer confidently from the information given, say "I don't have enough information to answer this."

PRODUCT INFORMATION:
Title: {product.title}
Description: {product.description}
Available variants: {', '.join(product.variants)}
Return policy: {product.return_policy}
Shipping policy: {product.shipping_policy}
FAQs: {chr(10).join(product.faqs)}
Customer reviews summary: {product.reviews_summary}

CUSTOMER QUESTION: {question}

Respond in this exact format:
ANSWER: [your answer]
CONFIDENCE: [a number from 0.0 to 1.0]
EVIDENCE: [copy the exact text from product info that supports your answer, or "none" if you had no basis]
"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    raw = response.choices[0].message.content

    # Parse the structured response
    lines = {line.split(":")[0].strip(): ":".join(line.split(":")[1:]).strip()
             for line in raw.strip().split("\n") if ":" in line}

    answer     = lines.get("ANSWER", raw)
    confidence = float(lines.get("CONFIDENCE", "0.5"))
    evidence   = lines.get("EVIDENCE", "none")

    # Hallucination check
    source_text = (
        product.description.lower() +
        product.return_policy.lower() +
        product.shipping_policy.lower() +
        " ".join(product.faqs).lower() +
        product.reviews_summary.lower()
    )

    is_hallucination = (
        evidence.lower() != "none" and
        evidence.lower() not in source_text
    )

    return SimulationResult(
        persona=persona,
        question=question,
        answer=answer,
        confidence=confidence,
        is_hallucination=is_hallucination,
        evidence=evidence,
    )


def simulate_all(product: ProductContext) -> list[SimulationResult]:
    """Run all personas and all questions against a product."""
    results = []
    for persona, questions in PERSONAS.items():
        for question in questions:
            result = simulate_one(product, persona, question)
            results.append(result)
    return results


def measure_drift(product: ProductContext, question_set: list[str]) -> dict:
    """
    Ask the same question 5 ways. Measure how consistent the answers are.
    Returns drift score: 0.0 = perfectly consistent, 1.0 = completely inconsistent.
    """
    answers = []
    confidences = []

    for question in question_set:
        result = simulate_one(product, "researcher", question)
        answers.append(result.answer)
        confidences.append(result.confidence)

    comparison_prompt = f"""You are evaluating how consistent an AI shopping assistant is.

Below are {len(answers)} answers to the same question phrased differently.
Score their consistency from 0.0 (all say completely different things) to 1.0 (all say exactly the same thing).
Reply with ONLY a number between 0.0 and 1.0. Nothing else. No explanation.

Answers:
""" + "\n---\n".join(answers)

    consistency_response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": comparison_prompt}],
        max_tokens=10
    )

    try:
        consistency = float(
            consistency_response.choices[0].message.content.strip()
        )
        consistency = max(0.0, min(1.0, consistency))
    except ValueError:
        consistency = 0.5

    drift_score = round(1.0 - consistency, 2)

    return {
        "question_topic": question_set[0],
        "drift_score": drift_score,
        "avg_confidence": round(sum(confidences) / len(confidences), 2),
        "answers": answers,
    }


def run_drift_analysis(product: ProductContext) -> list[dict]:
    """Run drift detection across all question sets for a product."""
    results = []
    for question_set in DRIFT_QUESTION_SETS:
        result = measure_drift(product, question_set)
        results.append(result)
    return results