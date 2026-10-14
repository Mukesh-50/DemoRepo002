# Decision functions: each one picks the next step for a conditional edge

import os
import subprocess

from workflow.state import TestState


def check_test_exists(state: TestState):
    # Skip if the test is already on disk, or already waiting in a pull request branch
    if os.path.exists(state["output_file"]):
        print(f"{state['output_file']} already exists, skipping")
        return "skip"

    remote_branch = subprocess.run(
        ["git", "ls-remote", "--heads", "origin", state["branch"]],
        capture_output=True, text=True,
    )
    if remote_branch.stdout.strip():
        print(f"Branch {state['branch']} already exists on GitHub (open pull request?), skipping")
        return "skip"

    return "new"


def route_to_agent(state: TestState):
    # The supervisor already decided; just follow its choice
    return state["next_agent"]


def check_create_pr(state: TestState):
    if state["create_pr"]:
        return "create"
    print("Not creating a pull request")
    return "skip"
