# The State: the shared notebook every agent reads from and writes to

import operator
from typing import Annotated, TypedDict


class TestState(TypedDict):
    # Files
    input_file: str       # manual test case, e.g. test_cases/TC001.txt
    output_file: str      # generated test, e.g. tests/tc001.spec.ts
    branch: str           # git branch for the pull request, e.g. test/tc001
    test_case: str        # text of the manual test case

    # Work done by the agents
    exploration: str      # Explorer: what it saw in the real browser
    test_code: str        # Generator / Healer: the Playwright test
    review_status: str    # Reviewer: "not reviewed", "approved" or "changes requested"
    review_feedback: str  # Reviewer: what must be fixed
    test_status: str      # Healer: "not run", "passed" or "failed"
    run_output: str       # Healer: output of the last test run
    heal_runs: int        # Healer: how many fixes it has tried

    # Supervisor
    next_agent: str       # who works next
    steps: int            # how many decisions the supervisor has made
    history: Annotated[list[str], operator.add]  # log of what each agent did (new lines are added, not replaced)

    # Pull request
    create_pr: bool       # did you approve the pull request?
    pr_url: str           # link to the pull request
