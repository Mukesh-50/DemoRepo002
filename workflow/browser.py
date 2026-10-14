# Connects to the Playwright MCP server, which gives the agents browser tools
# (navigate, click, type, snapshot, ...)

from contextlib import asynccontextmanager

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from config import HEADLESS, SAFE_BROWSER_TOOLS

mcp_args = ["@playwright/mcp", "--isolated", "--browser", "chromium"]
if HEADLESS:
    mcp_args.append("--headless")

client = MultiServerMCPClient({
    "playwright": {
        "command": "npx",
        "args": mcp_args,
        "transport": "stdio",
    }
})


@asynccontextmanager
async def browser_tools():
    # One session = one browser that stays open for all tool calls,
    # so the agent stays logged in between steps.
    async with client.session("playwright") as session:
        tools = await load_mcp_tools(session)
        yield [tool for tool in tools if tool.name in SAFE_BROWSER_TOOLS]
