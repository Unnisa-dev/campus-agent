import asyncio
from pathlib import Path
from fastmcp import Client


async def main():
    # Connect to the MCP server
    async with Client((Path("server.py"))) as client:

        # Discover the available tools
        tools = await client.list_tools()

        print("Available tools:")
        for tool in tools:
            print("-", tool.name)

        # Call the attendance tool
        result = await client.call_tool(
            "get_attendance",
            {"student_id": 101}
        )

        print("\nAttendance result:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
