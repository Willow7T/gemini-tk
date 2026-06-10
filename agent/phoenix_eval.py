from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def detect_question_type(question: str):

    q = question.lower()

    if any(x in q for x in ["spread", "infect", "contagious"]):
        return "spread"

    if any(x in q for x in ["treat", "treatment", "cure", "fungicide"]):
        return "treatment"

    if any(x in q for x in ["prevent", "prevention", "avoid"]):
        return "prevention"

    if any(x in q for x in ["cause", "why"]):
        return "cause"

    if any(x in q for x in ["human", "people", "eat", "safe"]):
        return "human_risk"

    if any(x in q for x in ["symptom", "look like"]):
        return "symptoms"

    return "general"

def log_evaluation(
    response: str,
    passed: bool,
    issues: list,
    disease: str,
    question: str,
):

    with tracer.start_as_current_span(
        "phoenix_evaluation"
    ) as span:

        span.set_attribute(
            "evaluation.passed",
            passed
        )

        span.set_attribute(
            "evaluation.issue_count",
            len(issues)
        )

        span.set_attribute(
            "evaluation.issues",
            "; ".join(issues)
        )

        span.set_attribute(
            "evaluation.disease",
            disease
        )

        span.set_attribute(
            "evaluation.question",
            question
        )

        span.set_attribute(
            "evaluation.question_type",
            detect_question_type(question)
        )

        span.set_attribute(
            "evaluation.response",
            response
        )

        span.set_attribute(
            "evaluation.has_issues",
            len(issues) > 0
        )

        span.set_attribute(
            "evaluation.failure_types",
            ";".join(issues)
        )