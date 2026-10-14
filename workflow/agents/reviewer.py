# REVIEWER: checks the test code against a quality checklist.
# Approves it, or requests changes that the generator must make.

from pydantic import BaseModel, Field

from workflow.llm import llm
from workflow.state import TestState


# The reviewer must answer in exactly this shape
class Review(BaseModel):
    approved: bool
    feedback: str = Field(description="If not approved: a numbered list of what must change. If approved: one short sentence.")


REVIEWER_PROMPT = """
You are a senior QA reviewer. Review this Playwright test against the checklist.

Checklist:
1. Every step of the manual test case is covered, in order.
2. Every expected result has an await expect().
3. Locators use getByRole(), getByPlaceholder(), getByLabel() or getByText(). No CSS or XPath.
4. No waitForTimeout() or fixed sleeps.
5. The assertions really check the expected result (not something always true).
6. The test name contains the test case ID.
7. No if statements, try/catch or .catch() that make a step optional. Every step must always run.

Approve if all checklist items pass. Do not reject for small style preferences.

Manual test case:
{test_case}

Test code:
{test_code}
"""


def reviewer(state: TestState):
    print("🧐 Reviewer: reviewing the test code...")

    prompt = REVIEWER_PROMPT.format(test_case=state["test_case"], test_code=state["test_code"])
    review = llm.with_structured_output(Review).invoke(prompt)

    if review.approved:
        print(f"🧐 Reviewer: APPROVED - {review.feedback}")
    else:
        print(f"🧐 Reviewer: CHANGES REQUESTED\n{review.feedback}")

    return {
        "review_status": "approved" if review.approved else "changes requested",
        "review_feedback": "" if review.approved else review.feedback,
        "history": ["reviewer: " + ("approved the test" if review.approved else "requested changes")],
    }
