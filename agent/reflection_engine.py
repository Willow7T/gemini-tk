import json
from pathlib import Path
from collections import Counter
from strategy_store import safe_load_json
import time

HISTORY_FILE = Path("data/evaluation_history.json")
STRATEGY_FILE = Path("data/strategy.json")


ISSUE_TO_RECOMMENDATION = {
    "MISSING_DISEASE_NAME":
        "Always mention the exact disease predicted by the classifier.",

    "QUESTION_NOT_FULLY_ANSWERED":
        "Directly answer every user question before additional explanation.",

    "MISSING_CONFIDENCE":
        "Always include model confidence and uncertainty.",

    "CONTRADICTS_PREDICTION":
        "Never mention diseases different from the classifier result.",

    "NO_DIRECT_ANSWER":
        "Provide a direct answer first.",

    "OVERCONFIDENT":
        "Never claim the diagnosis is certain.",

}


def generate_strategy(failure_summary=None, phoenix_report=None, last_prediction=None):

    if not HISTORY_FILE.exists():
        return {
            "version": 1,
            "total_failures": 0,
            "top_failure": None,
            "recommendations": []
        }

    history = safe_load_json(
        HISTORY_FILE,[]
    )

    issue_counter = Counter()
    question_type_counter = Counter()
    reasoning_counter = Counter()

    for item in history:
        if item.get("passed", True):
            continue

        issues = item.get("issues", [])
        if isinstance(issues, str):
            issues = [issues]

        for issue in issues:
            issue_counter[issue] += 1

            question_type = item.get("question_type", "general")
            issue_key = f"{issue}|{question_type}"
            question_type_counter[issue_key] += 1

        for reason in item.get("reasoning", []):
            reasoning_counter[reason] += 1

    recommendations = []

    for issue, count in issue_counter.items():

        priority = (
            "high" if count >= 5
            else "medium" if count >= 2
            else "low"
        )

        base_description = ISSUE_TO_RECOMMENDATION.get(
            issue,
            f"Reduce occurrences of {issue}."
        )

        recommendations.append({
            "issue": issue,
            "count": count,

            "recommendation": {
                "rule": issue,
                "description": base_description,
                "action": "prompt_injection_rule",
                "priority": priority
            },

            "activation": {
                "trigger_issue": issue,
                "question_types": ["general", "treatment", "spread", "prevention"],
                "min_confidence": 0.0
            },

            "effectiveness": {
                "usage_count": 0,
                "success_count": 0,
                "success_rate": 0.0
            }
        })

    # sort by importance
    recommendations.sort(key=lambda x: x["count"], reverse=True)
    recommendations = recommendations[:5]

    top_question_patterns = []

    for pattern, count in question_type_counter.most_common(5):
        issue, question_type = pattern.split("|", 1)

        top_question_patterns.append({
            "issue": issue,
            "question_type": question_type,
            "count": count
        })

    common_reasoning = []

    for reason, count in reasoning_counter.most_common(5):
        common_reasoning.append({
            "reason": reason,
            "count": count
        })

    if history:
       strategy_version = int(time.time())

    strategy = {
        "strategy_version": strategy_version,
        "total_failures": sum(issue_counter.values()),
        "top_failure": (
            recommendations[0]["issue"]
            if recommendations
            else None
        ),

        "recommendations": recommendations,
        "question_patterns": top_question_patterns,
        "common_reasoning": common_reasoning
    }

    flat_rules = []

    for item in recommendations:

        rec = item["recommendation"]

        flat_rules.append({
            "rule": rec["rule"],
            "description": rec["description"],
            "priority": rec["priority"],
        })

    strategy["flat_rules"] = flat_rules

    STRATEGY_FILE.parent.mkdir(exist_ok=True)

    with open(STRATEGY_FILE, "w") as f:
        json.dump(strategy, f, indent=2)

    return strategy