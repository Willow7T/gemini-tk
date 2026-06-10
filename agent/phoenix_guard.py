from plant_agent.tools.classifier import LAST_PREDICTION
from phoenix_judge import judge_response
import re


def normalize(text):
    text = text.lower()
    text = text.replace("_", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


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

    return "general"


def evaluate_response(
    response: str,
    user_question: str = "",
    conversation_mode: str = "INITIAL_DIAGNOSIS"
):
    issues = []

    label = LAST_PREDICTION.get("label", "")
    confidence = LAST_PREDICTION.get("confidence", 0)

    normalized_response = normalize(response)
    normalized_label = normalize(label)

    response_lower = response.lower()

    if conversation_mode == "FOLLOWUP":

        if "Prediction:" in response:
            issues.append("REPEATED_DIAGNOSIS_TEMPLATE")

        if "Explanation:" in response:
            issues.append("REPEATED_EXPLANATION_SECTION")

        if "Model Confidence" in response:
            issues.append("REPEATED_CONFIDENCE_SECTION")

    if user_question:

        first_200 = response_lower[:200]

        direct_answer_terms = [
            "yes",
            "no",
            "prediction",
            "identified as",
            "the disease is",
            "diagnosis",
        ]

        if not any(
            term in first_200
            for term in direct_answer_terms
        ):
            issues.append("NO_DIRECT_ANSWER")

    if normalized_label:

        label_words = set(normalized_label.split())
        response_words = set(normalized_response.split())

        overlap = len(label_words & response_words)

        required_overlap = max(
            1,
            int(len(label_words) * 0.6)
        )

        if overlap < required_overlap:
            issues.append("MISSING_DISEASE_NAME")


    confidence_terms = [
        "confidence",
        "certain",
        "uncertain",
        "likely",
        "probability",
        "%",
    ]

    if conversation_mode == "INITIAL_DIAGNOSIS":
        if not any(
            term in response_lower
            for term in confidence_terms
        ):
            issues.append("MISSING_CONFIDENCE")

        
    overconfident_terms = [
        "definitely",
        "certainly",
        "guaranteed",
        "100%",
        "absolutely",
        "without doubt",
    ]

    if (
        confidence < 0.80
        and any(
            term in response_lower
            for term in overconfident_terms
        )
    ):
        issues.append("OVERCONFIDENT")

    question_type = (
        detect_question_type(user_question)
        if user_question
        else "general"
    )

    if question_type == "treatment":

        treatment_terms = [
            "fungicide",
            "spray",
            "remove",
            "treatment",
            "manage",
        ]

        if not any(
            term in response_lower
            for term in treatment_terms
        ):
            issues.append(
                "QUESTION_NOT_FULLY_ANSWERED"
            )

    elif question_type == "prevention":

        prevention_terms = [
            "prevent",
            "avoid",
            "rotation",
            "spacing",
        ]

        if not any(
            term in response_lower
            for term in prevention_terms
        ):
            issues.append(
                "QUESTION_NOT_FULLY_ANSWERED"
            )

    elif question_type == "cause":

        cause_terms = [
            "cause",
            "caused",
            "because",
            "conditions",
            "environment",
            "fungus",
            "bacteria",
            "virus",
        ]

        if not any(
            term in response_lower
            for term in cause_terms
        ):
            issues.append(
                "QUESTION_NOT_FULLY_ANSWERED"
            )

    elif question_type == "human_risk":

        risk_terms = [
            "safe",
            "human",
            "people",
            "consume",
            "eat",
            "edible",
        ]

        if not any(
            term in response_lower
            for term in risk_terms
        ):
            issues.append(
                "QUESTION_NOT_FULLY_ANSWERED"
            )

    elif question_type == "spread":

        spread_terms = [
            "spread",
            "infect",
            "transmit",
            "spore",
            "nearby",
            "neighboring",
        ]

        if not any(
            term in response_lower
            for term in spread_terms
        ):
            issues.append(
                "QUESTION_NOT_FULLY_ANSWERED"
            )

    try:

        judge_result = judge_response(
            response=response,
            question=user_question,
            prediction=label,
        )

        issues.extend(
            judge_result.get("issues", [])
        )

    except Exception as e:

        print(
            f"Judge evaluation failed: {e}"
        )

    issues = list(dict.fromkeys(issues))

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "question_type": question_type,
    }