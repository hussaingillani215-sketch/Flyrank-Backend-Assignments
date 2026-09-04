import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
from tools import get_tasks

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

tool_definitions = [
    {
        "name": "get_tasks",
        "description": "Get tasks from the task database, optionally filtered by status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "done"],
                    "description": "Filter tasks by status. Omit to get all tasks.",
                }
            },
        },
    }
]

def run_agent(user_message):
    messages = [{"role": "user", "content": user_message}]

    for _ in range(5):  # hard cap so a confused loop can't run forever
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            tools=tool_definitions,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            # Claude answered in plain text — we're done
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            return

        # Claude wants to call a tool
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                if block.name == "get_tasks":
                    status = block.input.get("status")
                    result = get_tasks(status)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })

        messages.append({"role": "user", "content": tool_results})

    print("Loop cap hit — stopping.")

if __name__ == "__main__":
    run_agent("What tasks do I still need to finish?")