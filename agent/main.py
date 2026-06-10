import asyncio
import os
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import InMemoryRunner
from google.genai import types

from instrumentation import setup_tracing
from plant_agent.agent import root_agent


async def run_turn(image_path: str, user_question: str = None) -> None:
    setup_tracing() 
    
    app_name = "plant_disease_hackathon"
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    user_id = "local_user"

    runner = InMemoryRunner(agent=root_agent, app_name=app_name)
    
    try:
        await runner.session_service.create_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
    except Exception as e:
        print(f"Session creation warning: {e}")
        pass

    if user_question:
        user_text = f"Please analyze this plant image: {image_path}\nUser Question: {user_question}"
    else:
        user_text = f"Please analyze this plant image: {image_path}"
    
    print(f"\n--- Processing Agent Session ---")
    print(f"Image Path: {image_path}")
    if user_question:
        print(f"User Text Query: {user_question}")
    print(f"-----------------------------------------\n")

    new_message = types.Content(role="user", parts=[types.Part(text=user_text)])

 
    all_events = []
    events = runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=new_message
    )

    for event in events:
        all_events.append(event)
        # Print tool calls immediately
        if hasattr(event, 'model_response') and event.model_response:
            if hasattr(event.model_response, 'candidates'):
                for candidate in event.model_response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        for part in candidate.content.parts:
                            if hasattr(part, 'function_call') and part.function_call:
                                print(f"  🔧 Calling {part.function_call.name}...")
    
    print("\n Chat Response to the Question: \n")
    
    session = await runner.session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    
    final_answer = None
    if session and session.events:
        for event in reversed(session.events):
            if event.author == "plant_pathologist" and event.content:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        final_answer = part.text
                        break
                if final_answer:
                    break
    
    if final_answer:
        print(final_answer)
    else:
        print("No final answer generated. The tool may have failed or the model didn't respond.")
    
    print("\n-----------------------------------------------------")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_image> [optional_question]")
        return
    
    image_path = sys.argv[1]
    user_question = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
    
    # Run the wrapper
    asyncio.run(run_turn(image_path, user_question))


if __name__ == "__main__":
    main()