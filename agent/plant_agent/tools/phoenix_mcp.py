from mcp import ClientSession
from mcp.client.stdio import (
    stdio_client,
    StdioServerParameters,
)
import json
async def get_recent_failures():

    server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@arizeai/phoenix-mcp@latest",
            "--baseUrl",
            "http://localhost:6006",
        ],
    )

    async with stdio_client(
        server_params
    ) as (read_stream, write_stream):

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize() 

            traces = await session.call_tool(
                "list-traces",
                {
                    "project_identifier": "gemini-hackathon-tk",
                    "limit": 20,
                },
            )

            metadata = []

            if hasattr(traces, "content"):
                items = traces.content
            else:
                items = []

            for item in items:

                item_str = str(item)

                metadata.append({
                    "trace_id": getattr(item, "trace_id", "unknown"),
                    "status": getattr(item, "status", "unknown"),
                    "has_error":
                        any(word in item_str.lower()
                            for word in [
                                "error",
                                "exception",
                                "failed",
                                "timeout",
                            ]),
                })

            total = len(metadata)

            evaluation_data = await get_recent_evaluations()
            total = evaluation_data["evaluation_span_count"]
            failed = len(
                evaluation_data["failed_evaluations"]
            )

            return {
                "total_traces": total,
                "failed_traces": failed,
                "failure_rate":
                    round((failed / total) * 100, 2)
                    if total else 0,
                "trace_metadata": metadata,
            }

async def get_recent_evaluations():
    server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@arizeai/phoenix-mcp@latest",
            "--baseUrl",
            "http://localhost:6006",
        ],
    )

    async with stdio_client(
        server_params
    ) as (read_stream, write_stream):

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            spans = await session.call_tool(
                "get-spans",
                {
                    "project_identifier":
                        "gemini-hackathon-tk"
                }
            )

            payload = json.loads(
                spans.content[0].text
            )

            all_spans = payload.get(
                "spans",
                []
            )
            evaluations = []
            failed_evals = []
            issues = []

            for span in all_spans:

                attrs = span.get("attributes", {})

                if "evaluation.passed" not in attrs:
                    continue
                
                ev = {
                    "passed": attrs.get("evaluation.passed"),
                    "issues": attrs.get("evaluation.issues"),
                    "question_type": attrs.get("evaluation.question_type"),
                    "disease": attrs.get("evaluation.disease"),
                }

                evaluations.append(ev)

                if not ev["passed"]:
                    failed_evals.append(ev)

                span_issues = attrs.get(
                    "evaluation.issues",
                    []
                )

                if span_issues:

                    if isinstance(span_issues, list):
                        issues.extend(span_issues)
                    else:
                        issues.append(str(span_issues))

            return {
                "evaluation_span_count": len(evaluations),
                "recent_issues": issues[-10:],
                "evaluations": evaluations[-20:],
                "failed_evaluations": failed_evals[-20:]
            }
                        