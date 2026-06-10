import asyncio
import nest_asyncio
import json
from plant_agent.tools.phoenix_mcp import (
    get_recent_evaluations
)

nest_asyncio.apply()

async def review_phoenix_traces():
    evaluation_spans = await get_recent_evaluations()

    return {
        "evaluation_span_count": evaluation_spans.get("evaluation_span_count", 0),
        "evaluations": evaluation_spans.get("evaluations", []),
        "recent_issues": evaluation_spans.get("recent_issues", []),
        "failed_evaluations": evaluation_spans.get("failed_evaluations", [])
    }