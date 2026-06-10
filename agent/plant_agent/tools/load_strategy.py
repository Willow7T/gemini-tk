import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" 

STRATEGY_FILE = DATA_DIR / "strategy.json"


def load_strategy():

    if not STRATEGY_FILE.exists():
        return "No learned strategy yet."

    try:
        with open(STRATEGY_FILE, "r") as f:
            strategies = json.load(f)

        if not strategies:
            return "No strategies available."

        lines = []

        for item in strategies:
            lines.append(
                f"- {item.get('rule')} "
                f"(success={item.get('success_count',0)}, "
                f"fail={item.get('fail_count',0)})"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"Unable to load strategy: {e}"