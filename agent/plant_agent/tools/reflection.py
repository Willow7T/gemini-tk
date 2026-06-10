import json
from pathlib import Path

HISTORY_FILE = Path("data/evaluation_history.json")


def store_evaluation_result(
    passed: bool,
    issues: list,
):
    """
    Persist evaluation results so recurring failures can be analyzed.
    """

    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    history = []

    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append({
        "passed": passed,
        "issues": issues
    })

    history = history[-500:]

    with open(HISTORY_FILE, "w") as f:
        json.dump(
            history,
            f,
            indent=2
        )


def summarize_failures() -> str:

    if not HISTORY_FILE.exists():
        return "No historical failures detected."

    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)

    except Exception:
        return "Unable to load evaluation history."

    failures = [
        item
        for item in history
        if not item.get("passed", True)
    ]

    if not failures:
        return "No historical failures detected."

    issue_counts = {}

    for failure in failures:

        for issue in failure.get("issues", []):

            issue_counts[issue] = (
                issue_counts.get(issue, 0) + 1
            )

    report = []

    for issue, count in sorted(
        issue_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        report.append(
            f"{issue}: {count} failures"
        )

    return "\n".join(report)