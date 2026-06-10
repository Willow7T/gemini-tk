import json
from pathlib import Path
from datetime import datetime
import time

STRATEGY_FILE = Path("data/strategy.json")

def normalize_rule(rule):

    if isinstance(rule, dict):
        rule = rule.get("rule", "")
    return str(rule).strip().lower()

def safe_load_json(path: Path, default):
    try:
        if not path.exists():
            return default

        content = path.read_text().strip()

        if not content:
            return default

        return json.loads(content)

    except Exception as e:
        print(f"[Warning] Failed to load {path}: {e}")
        return default

def load_strategies():

    data = safe_load_json(
        STRATEGY_FILE,
        []
    )

    cleaned = []

    for s in data:

        if isinstance(s, str):
            cleaned.append({
                "rule": s,
                "usage_count": 0,
                "success_count": 0,
                "fail_count": 0,
                "rewards": [],
                "last_used": time.time()
            })
        else:
            cleaned.append(s)

    return cleaned

def strategy_exists(rule):
    target = normalize_rule(rule)

    data = load_strategies()

    return any(
        normalize_rule(s) == target
        for s in data
    )
def save_strategy(strategy):

    if isinstance(strategy, str):
        strategy = {
            "rule" : strategy
        }
    data = load_strategies()

    if strategy_exists(strategy["rule"]):
        return

    strategy["timestamp"] = datetime.utcnow().isoformat()
    strategy["usage_count"] = 0
    strategy["success_count"] = 0
    strategy["fail_count"] = 0
    strategy["last_used"] = time.time()
    strategy["rewards"] = []

    data.append(strategy)
    STRATEGY_FILE.write_text(json.dumps(data, indent=2))

def update_strategy_result(strategy_text, reward):
    data = load_strategies()

    found = False

    for i, s in enumerate(data):

        if isinstance(s, str):
            s = {
                "rule": s,
                "usage_count": 0,
                "success_count": 0,
                "fail_count": 0,
                "rewards": []
            }
            data[i] = s

        if normalize_rule(s) == normalize_rule(strategy_text):
            found = True

            s.setdefault("usage_count", 0)
            s.setdefault("success_count", 0)
            s.setdefault("fail_count", 0)
            s.setdefault("last_used", time.time())

            s["usage_count"] += 1
            s["last_used"] = time.time()

            if reward > 0:
                s["success_count"] += 1
            else:
                s["fail_count"] += 1

            s.setdefault("rewards", [])
            s["rewards"].append(reward)

            break

    if not found:
        data.append({
            "rule": strategy_text,
            "usage_count": 1,
            "success_count": 1 if reward > 0 else 0,
            "fail_count": 0 if reward > 0 else 1,
            "last_used": time.time(),
            "rewards": [reward]
        })

    STRATEGY_FILE.write_text(json.dumps(data, indent=2))


def get_best_strategies(limit=5):

    data = load_strategies()

    normalized = []

    for s in data:

        if isinstance(s, str):
            s = {
                "rule": s,
                "success_count": 0,
                "fail_count": 0,
                "usage_count": 0,
                "last_used": time.time(),
                "rewards": []
            }

        normalized.append(s)

    data = normalized

    for s in data:

        success = s.get("success_count", 0)
        fail = s.get("fail_count", 0)

        total = success + fail

        success_rate = (
            success / total
            if total > 0 else 0.5
        )

        rewards = s.get("rewards", [])

        avg_reward = (
            sum(rewards) / len(rewards)
            if rewards else 0
        )

        age_days = (
            time.time()
            - s.get("last_used", time.time())
        ) / 86400

        decay = 0.98 ** age_days

        s["score"] = (
            success_rate * 0.7
            + avg_reward * 0.3
        ) * decay

    return sorted(
        data,
        key=lambda x: x["score"],
        reverse=True
    )[:limit]
