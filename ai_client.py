import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from fastmcp import Client
from fastmcp.exceptions import ToolError

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing from .env")

# Connect to Groq using its OpenAI-compatible API.
ai = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"

# Describe the MCP tools to the AI model.
ai_tools = [
    {
        "type": "function",
        "function": {
            "name": "find_student",
            "description": "Find a student by their student ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {"type": "integer"}
                },
                "required": ["student_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_attendance",
            "description": "Get a student's attendance percentage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {"type": "integer"}
                },
                "required": ["student_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exam_date",
            "description": "Get a student's exam date.",
            "parameters": {
                "type": "object",
                "properties": { "student_id": {"type": "integer"} },
                "required": ["student_id"],
                "additionalProperties": False,
            },
        },
    },
]


async def main():
    question = input("Ask Campus Agent: ")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful Campus Agent. "
                "Use the available tools for student information. "
                "Never invent student records or results."
            ),
        },
        {"role": "user", "content": question},
    ]

    async with Client(Path("server.py")) as mcp:
        while True:
            response = ai.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=ai_tools,
                tool_choice="auto",
            )

            message = response.choices[0].message

            # Save the model's reply, including any requested tool calls.
            messages.append(message.model_dump(exclude_none=True))

            # If the model doesn't request a tool, display its answer.
            if not message.tool_calls:
                print("\nCampus Agent:", message.content or "")
                break

            # Execute each requested tool using the MCP client.
            for call in message.tool_calls:
                tool_name = call.function.name
                arguments = json.loads(call.function.arguments)

                print(f"\nCalling MCP tool: {tool_name}")
                print("Input:", arguments)

                try:
                    result = await mcp.call_tool(tool_name, arguments)

                    data = result.structured_content
                    if data is None:
                        data = [
                            item.text
                            for item in result.content
                            if hasattr(item, "text")
                        ]

                except ToolError:
                    data = {
                        "error": (
                            "Invalid tool input. Student ID must be "
                            "a positive integer greater than or equal to 1."
                        )
                    }

                # Return the actual tool result to the model.
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(data, default=str),
                })


if __name__ == "__main__":
    asyncio.run(main())
