from schema import SimulationResult, Gap, GapReport


def score_product(
    product_id: str,
    simulation_results: list[SimulationResult],
    drift_results: list[dict]
) -> GapReport:
    """
    Takes simulation results + drift results and produces
    a scored GapReport with specific gaps and fixes.
    """
    gaps = []

    # ── 1. Query coverage score ──────────────────────────
    # How many questions could the AI answer confidently?
    confident = [r for r in simulation_results if r.confidence >= 0.5]
    query_coverage = len(confident) / len(simulation_results) if simulation_results else 0

    if query_coverage < 0.7:
        gaps.append(Gap(
            dimension="query_coverage",
            description=f"AI agents could only confidently answer "
                        f"{int(query_coverage * 100)}% of buyer questions. "
                        f"Missing info is causing agents to skip or guess.",
            severity="high" if query_coverage < 0.5 else "medium",
            suggested_fix="Add detailed product descriptions covering: "
                          "materials, sizing, use cases, and compatibility."
        ))

    # ── 2. Hallucination score ───────────────────────────
    hallucinations = [r for r in simulation_results if r.is_hallucination]
    hallucination_rate = len(hallucinations) / len(simulation_results) if simulation_results else 0

    if hallucination_rate > 0.1:
        gaps.append(Gap(
            dimension="hallucination_risk",
            description=f"AI agents invented information in "
                        f"{int(hallucination_rate * 100)}% of responses. "
                        f"This means buyers may receive wrong information about your store.",
            severity="high" if hallucination_rate > 0.2 else "medium",
            suggested_fix="Explicitly state key facts in your product description "
                          "rather than leaving them implied. Be specific about "
                          "materials, dimensions, and policies."
        ))

    # ── 3. Policy clarity score ──────────────────────────
    policy_questions = [r for r in simulation_results
                        if "return" in r.question.lower()
                        or "ship" in r.question.lower()
                        or "deliver" in r.question.lower()]

    policy_confident = [r for r in policy_questions if r.confidence >= 0.5]
    policy_score = len(policy_confident) / len(policy_questions) if policy_questions else 1.0

    if policy_score < 0.8:
        gaps.append(Gap(
            dimension="policy_clarity",
            description=f"Your return and shipping policies are unclear to AI agents. "
                        f"Only {int(policy_score * 100)}% of policy questions were "
                        f"answered confidently. AI shopping agents deprioritise "
                        f"products with unclear policies.",
            severity="high",
            suggested_fix="Write a clear, plain-English return policy. Include: "
                          "how many days, what condition, who pays return shipping, "
                          "and how refunds are issued."
        ))

    # ── 4. Drift score ───────────────────────────────────
    high_drift = [d for d in drift_results if d["drift_score"] > 0.5]

    if high_drift:
        topics = [d["question_topic"][:40] for d in high_drift]
        gaps.append(Gap(
            dimension="answer_consistency",
            description=f"AI agents give inconsistent answers about: "
                        f"{', '.join(topics)}. "
                        f"This means buyers get different information depending "
                        f"on how they phrase their question.",
            severity="medium",
            suggested_fix="Rewrite these sections to be unambiguous. "
                          "Use direct, factual language with no room for interpretation."
        ))

    # ── 5. Persona coverage ──────────────────────────────
    personas = set(r.persona for r in simulation_results)
    persona_scores = {}
    for persona in personas:
        persona_results = [r for r in simulation_results if r.persona == persona]
        persona_confident = [r for r in persona_results if r.confidence >= 0.5]
        persona_scores[persona] = len(persona_confident) / len(persona_results)

    worst_persona = min(persona_scores, key=persona_scores.get)
    if persona_scores[worst_persona] < 0.5:
        gaps.append(Gap(
            dimension="persona_coverage",
            description=f"Your store performs very poorly for '{worst_persona}' buyers "
                        f"(score: {int(persona_scores[worst_persona]*100)}%). "
                        f"This buyer type cannot get answers to their key questions.",
            severity="medium",
            suggested_fix=f"Add content specifically addressing "
                          f"'{worst_persona}' concerns in your product description or FAQ."
        ))

    # ── Final score calculation ──────────────────────────
    # Weighted average of all dimension scores
    overall_score = round((
        query_coverage * 35 +
        (1 - hallucination_rate) * 25 +
        policy_score * 25 +
        (1 - (len(high_drift) / max(len(drift_results), 1))) * 15
    ), 1)

    # Sort gaps by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    gaps.sort(key=lambda g: severity_order[g.severity])

    return GapReport(
        product_id=product_id,
        overall_score=overall_score,
        gaps=gaps,
        simulation_results=simulation_results
    )