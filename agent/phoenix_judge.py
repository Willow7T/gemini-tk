import json
from google import genai
import os

VALID_ISSUES = {
    "QUESTION_NOT_FULLY_ANSWERED",
    # "MISSING_TREATMENT",
    # "MISSING_PREVENTION",
    "MISSING_CONFIDENCE",
    "CONTRADICTS_PREDICTION",
    "NO_DIRECT_ANSWER",
    "OVERCONFIDENT",
}

_client = None

def get_client():
    global _client
    if _client is None:
        _client = genai.Client(
            vertexai=True,
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION"),
        )
    return _client

def judge_response(response: str, question: str, prediction: str):

    prompt = f"""
You are an agricultural response evaluator.

Classifier prediction:
{prediction}

User question:
{question}

Assistant response:
{response}

Return ONLY JSON:
{{
  "passed": false,
  "issues": [],
  "reasoning": []
}}

Allowed issues:
{", ".join(VALID_ISSUES)}
"""

    result = get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = getattr(result, "text", None)
    if not text:
        text = result.candidates[0].content.parts[0].text

    text = text.strip()

    if text.startswith("`"):
        text = "\n".join(text.splitlines()[1:-1]).strip()

    parsed = json.loads(text)

    issues = [i for i in parsed.get("issues", []) if i in VALID_ISSUES]

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "reasoning": parsed.get("reasoning", [])
    }