import json
import sys
import time

from openai import OpenAI

from .config import MAX_ITERATIONS, MODEL, SYSTEM_PROMPT
from .tools import TOOLS, execute_tool


def agent_loop(client: OpenAI, user_prompt: str, verbose: bool = True) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    for _ in range(MAX_ITERATIONS):
        response = None
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=TOOLS,
                    temperature=0,
                )
                break
            except Exception as e:
                if "rate_limit_exceeded" in str(e) and attempt < 2:
                    print("Rate limited, retrying in 10s...", file=sys.stderr)
                    time.sleep(10)
                else:
                    raise

        if response is None or not response.choices:
            raise RuntimeError("no choices in response")

        message = response.choices[0].message

        if not message.tool_calls:
            return message.content

        messages.append(message)

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            if verbose:
                print(f"  tool: {name}({args})", file=sys.stderr)
            result = execute_tool(name, args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    raise RuntimeError(f"agent did not finish within {MAX_ITERATIONS} iterations")
