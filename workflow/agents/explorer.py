# EXPLORER: an agent with browser tools (Playwright MCP).
# It performs the test steps in a real browser and reports what it saw.

from langchain.agents import create_agent

from workflow.browser import browser_tools
from workflow.llm import llm
from workflow.state import TestState

EXPLORER_PROMPT = """
You are a QA explorer. You have browser tools.
Perform every step of the manual test case in the real browser, in order. Do not skip or stop early.
After each action, read the page snapshot to see what changed.
If a step's element is hidden (for example inside a menu), find how to reach it and report that.

When you are done, write a report for the test writer. For each step include:
- what you did
- the element you used: its role and accessible name (e.g. button "Sign in"),
  or its placeholder/label for text boxes. Never use [ref=...] ids.
- the page URL after the step
- what is visible on the page that proves the expected result

If a step cannot be done, say so clearly. Do not write test code.
"""


async def explorer(state: TestState):
    print("🔍 Explorer: performing the test steps in the browser...")

    async with browser_tools() as tools:
        agent = create_agent(llm, tools=tools, system_prompt=EXPLORER_PROMPT)
        result = await agent.ainvoke(
            {"messages": [("user", f"Manual test case:\n{state['test_case']}")]},
            {"recursion_limit": 50},
        )

    report = result["messages"][-1].content
    tool_calls = sum(1 for message in result["messages"] if message.type == "tool")
    print(f"🔍 Explorer: done ({tool_calls} browser actions)")
    return {
        "exploration": report,
        "history": [f"explorer: explored the test case in the browser ({tool_calls} browser actions)"],
    }
