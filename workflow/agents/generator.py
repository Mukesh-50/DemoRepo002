# GENERATOR: writes the Playwright test from the explorer's report.
# If the reviewer requested changes, it rewrites the test to fix them.

from workflow.llm import llm
from workflow.state import TestState

GENERATOR_PROMPT = """
You are a QA automation engineer. Write a Playwright test in TypeScript for the manual test case.
Use ONLY the elements described in the explorer's report. They come from the real pages.

Rules:
- import {{ test, expect }} from '@playwright/test';
- One test(). Name it with the test case ID and title.
- Use getByRole(), getByPlaceholder(), getByLabel() or getByText(). No CSS or XPath selectors.
- Never use waitForTimeout().
- No if statements, try/catch or .catch(). Every step must always run.
- Add a comment for each step, and an await expect() for each expected result.
- Return ONLY TypeScript code. No explanation, no markdown.

Manual test case:
{test_case}

Explorer's report (real page elements):
{exploration}
{previous}
"""


def clean_code(text: str):
    # Remove ``` markdown fences if the AI added them
    for fence in ["```typescript", "```ts", "```"]:
        text = text.replace(fence, "")
    return text.strip()


def generator(state: TestState):
    rewriting = state["review_status"] == "changes requested"
    print("✍️  Generator: " + ("rewriting the test with the reviewer's feedback..." if rewriting else "writing the test..."))

    previous = ""
    if rewriting:
        previous = f"""
Your previous version:
{state['test_code']}

The reviewer requested these changes. Fix all of them:
{state['review_feedback']}
"""

    prompt = GENERATOR_PROMPT.format(
        test_case=state["test_case"],
        exploration=state["exploration"],
        previous=previous,
    )
    code = clean_code(llm.invoke(prompt).content)

    # New code: it has not been reviewed or run yet
    return {
        "test_code": code,
        "review_status": "not reviewed",
        "test_status": "not run",
        "history": ["generator: " + ("rewrote the test with the reviewer's feedback" if rewriting else "wrote the test")],
    }
