# Human-in-the-loop: show the final test and ask before opening a pull request.
# Then: new branch -> commit -> push -> AI-written PR description -> gh pr create

import subprocess

from langgraph.types import interrupt

from config import BASE_BRANCH
from workflow.llm import llm
from workflow.state import TestState

PR_DESCRIPTION_PROMPT = """
Write a GitHub pull request description in Markdown for this AI-generated Playwright test.
Use these sections:
## Summary  (2-3 sentences: what the test checks)
## Test steps covered  (a short numbered list)
## How it was generated  (which agents worked on it, based on the log)
## How to run  (npx playwright test {output_file})
Keep it short and clear. Return only the Markdown.

Manual test case:
{test_case}

Test code:
{test_code}

Test status: {test_status}

Agent log:
{history}
"""


def ask_create_pr(state: TestState):
    # Note: when the graph resumes, this node runs again from the top.
    # So we don't print() here; everything to show goes inside the interrupt message.
    message = f"""
==================== FINAL TEST: {state['output_file']} ====================
{state['test_code']}
==========================================================================
Test: {state['test_status'].upper()}   Review: {state['review_status'].upper()}   Supervisor steps: {state['steps']}
"""
    if state["test_status"] != "passed":
        message += "WARNING: the test is not passing.\n"
    message += f"Create a pull request on branch '{state['branch']}'? (yes/no): "

    # interrupt() pauses the graph here and waits for your answer
    answer = interrupt(message)
    return {"create_pr": answer.strip().lower() in ("yes", "y")}


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True)


def create_pull_request(state: TestState):
    branch = state["branch"]
    files = [state["input_file"], state["output_file"]]
    print(f"🔀 Creating branch {branch}...")

    pr_url = ""
    try:
        git("checkout", "-b", branch)
        git("add", *files)
        commit = git("commit", "-m", f"Add Playwright test for {state['input_file']}", "--", *files)
        if commit.returncode != 0:
            print("Commit failed:\n" + commit.stdout + commit.stderr)
            return {"pr_url": ""}

        push = git("push", "-u", "origin", branch)
        if push.returncode != 0:
            print("Push failed:\n" + push.stderr)
            return {"pr_url": ""}

        print("✍️  Writing the pull request description with AI...")
        description = llm.invoke(PR_DESCRIPTION_PROMPT.format(
            output_file=state["output_file"],
            test_case=state["test_case"],
            test_code=state["test_code"],
            test_status=state["test_status"],
            history="\n".join(state["history"]),
        )).content

        pr = subprocess.run(
            ["gh", "pr", "create", "--base", BASE_BRANCH, "--head", branch,
             "--title", f"Add Playwright test for {state['input_file']}", "--body", description],
            capture_output=True, text=True,
        )
        if pr.returncode == 0:
            pr_url = pr.stdout.strip()
            print(f"✅ Pull request created: {pr_url}")
        else:
            print("Creating the pull request failed:\n" + pr.stderr)
    finally:
        # Always go back to the base branch for the next test case
        git("checkout", BASE_BRANCH)

    return {"pr_url": pr_url}
