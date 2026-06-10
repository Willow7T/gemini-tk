from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from plant_agent.prompt import (
    plant_agent_instruction
)

from plant_agent.tools.mcp_reflection import (
    review_phoenix_traces
)

from plant_agent.tools.load_strategy import (
    load_strategy
)

from plant_agent.tools.classifier import (
    predict_disease
)

from plant_agent.tools.reflection import (
    summarize_failures
)

root_agent = Agent(
    name="plant_pathologist",
    instruction=plant_agent_instruction,
    tools=[
        FunctionTool(
            func=review_phoenix_traces
        ),
        FunctionTool(
            func=load_strategy
        ),
        FunctionTool(
            func=predict_disease
        ),
        FunctionTool(
            func=summarize_failures
        ),
        
    ],
)