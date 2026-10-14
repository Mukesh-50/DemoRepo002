# SUPERVISOR: an AI that reads the progress and decides which agent works next

from typing import Literal

from pydantic import BaseModel, Field

from config import MAX_SUPERVISOR_STEPS
from workflow.llm import llm
from workflow.state import TestState


# The supervisor must answer in exactly this shape
class Decision(BaseModel):
    next_agent: Literal["explorer", "generator", "reviewer", "healer", "finish"]
    reason: str = Field(description="One short sentence explaining the choice")


SUPERVISOR_PROMPT = """
You are the supervisor of a QA automation team. Your team turns a manual test case
into a working Playwright test. Decide which team member works next.

Team:
- explorer: performs the test steps in a real browser and reports the real page elements. Needed before any code is written.
- generator: writes the Playwright test from the explorer's report. Also rewrites it when the reviewer requests changes.
- reviewer: reviews the test code for quality. Approves it or requests changes.
- healer: runs the test. If it fails, it fixes the test using the browser.
- finish: the work is done (test passed AND code approved), or the team is stuck.

Current progress:
- Exploration done: {explored}
- Test code written: {has_code}
- Review status: {review_status}
- Reviewer feedback: {review_feedback}
- Test status: {test_status}
- Healer fixes tried: {heal_runs}

What each agent did so far (oldest first):
{history}
"""


def supervisor(state: TestState):
    steps = state["steps"] + 1

    # Safety limit: stop if the team has taken too many steps
    if steps > MAX_SUPERVISOR_STEPS:
        print(f"\n🧭 Supervisor: step limit ({MAX_SUPERVISOR_STEPS}) reached -> finish")
        return {"next_agent": "finish", "steps": steps}

    prompt = SUPERVISOR_PROMPT.format(
        explored="yes" if state["exploration"] else "no",
        has_code="yes" if state["test_code"] else "no",
        review_status=state["review_status"],
        review_feedback=state["review_feedback"] or "none",
        test_status=state["test_status"],
        heal_runs=state["heal_runs"],
        history="\n".join(state["history"]) or "nothing yet",
    )
    decision = llm.with_structured_output(Decision).invoke(prompt)

    print(f"\n🧭 Supervisor (step {steps}): {decision.next_agent} - {decision.reason}")
    return {"next_agent": decision.next_agent, "steps": steps}
