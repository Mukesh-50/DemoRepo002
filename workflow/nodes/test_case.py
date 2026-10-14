# Node: read the manual test case and fill the notebook with starting values

from workflow.state import TestState


def read_test_case(state: TestState):
    print(f"📄 Reading test case from {state['input_file']}")
    with open(state["input_file"], "r") as file:
        test_case = file.read()

    return {
        "test_case": test_case,
        "exploration": "",
        "test_code": "",
        "review_status": "not reviewed",
        "review_feedback": "",
        "test_status": "not run",
        "run_output": "",
        "heal_runs": 0,
        "steps": 0,
        "create_pr": False,
        "pr_url": "",
    }
