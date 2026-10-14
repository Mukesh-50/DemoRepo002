# HEALER: runs the test. If it fails, an agent fixes it.
# The agent has browser tools (to look at the real page) and a tool to save and run the test.

from langchain.agents import create_agent
from langchain_core.tools import tool

from config import MAX_HEAL_RUNS
from workflow.browser import browser_tools
from workflow.llm import llm
from workflow.state import TestState
from workflow.test_runner import run_test, save_test

HEALER_PROMPT = f"""
You are a QA engineer fixing a failing Playwright test (TypeScript).
1. Read the error. Use the browser tools to look at the real page if you need to.
2. Fix the test and call save_and_run_test with the FULL fixed code.
3. If it still fails, try again. You can run it at most {MAX_HEAL_RUNS} times.
Keep the test checking the same expected results. Never delete an assertion just to make it pass.
Never make a step optional with if statements, try/catch or .catch(). Every step must always run.
Use getByRole(), getByPlaceholder(), getByLabel() or getByText(). No CSS or XPath, no waitForTimeout().
When the test passes (or you have no runs left), reply with one sentence describing what you fixed.
"""


async def healer(state: TestState):
    print("🩹 Healer: running the test...")
    save_test(state["output_file"], state["test_code"])
    passed, output = run_test(state["output_file"])

    if passed:
        print("🩹 Healer: test PASSED, nothing to fix")
        return {"test_status": "passed", "run_output": output, "history": ["healer: ran the test, it passed"]}

    print("🩹 Healer: test FAILED, fixing it...")

    # The agent's own tool. It remembers the latest code and result in `latest`.
    latest = {"code": state["test_code"], "passed": False, "output": output, "runs": 0}

    @tool
    def save_and_run_test(code: str) -> str:
        """Save the full fixed test code and run it. Returns PASSED, or the error output."""
        if latest["runs"] >= MAX_HEAL_RUNS:
            return "No runs left. Stop and reply with a short summary."
        latest["runs"] += 1
        print(f"🩹 Healer: trying fix #{latest['runs']}...")
        save_test(state["output_file"], code)
        latest["code"] = code
        latest["passed"], latest["output"] = run_test(state["output_file"])
        return "PASSED" if latest["passed"] else latest["output"]

    async with browser_tools() as tools:
        agent = create_agent(llm, tools=tools + [save_and_run_test], system_prompt=HEALER_PROMPT)
        result = await agent.ainvoke(
            {"messages": [("user", f"Manual test case:\n{state['test_case']}\n\nTest code:\n{state['test_code']}\n\nError:\n{output}")]},
            {"recursion_limit": 50},
        )

    summary = result["messages"][-1].content
    print(f"🩹 Healer: test {'PASSED' if latest['passed'] else 'still FAILING'} after {latest['runs']} fix(es)")

    code_changed = latest["code"] != state["test_code"]
    return {
        "test_code": latest["code"],
        "test_status": "passed" if latest["passed"] else "failed",
        "run_output": latest["output"],
        "heal_runs": state["heal_runs"] + latest["runs"],
        # Changed code must be reviewed again
        "review_status": "not reviewed" if code_changed else state["review_status"],
        "history": [f"healer: test failed, tried {latest['runs']} fix(es), now {'passing' if latest['passed'] else 'still failing'}. {summary}"],
    }
