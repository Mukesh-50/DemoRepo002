# Start here: a multi-agent team turns every manual test case in test_cases/
# into a Playwright test, and opens a pull request for it.
#
# Run:  python main.py

import asyncio
import glob
import os

from langgraph.types import Command

from config import TEST_CASES_DIR, TESTS_DIR
from workflow.graph import app


async def run_workflow(input_file: str):
    name = os.path.basename(input_file).replace(".txt", "").lower()  # test_cases/TC001.txt -> tc001

    # Each file gets its own thread_id so its pause/resume is tracked separately.
    # recursion_limit: the supervisor loop takes many graph steps, so allow more than the default 25.
    config = {"configurable": {"thread_id": input_file}, "recursion_limit": 100}

    output = await app.ainvoke({
        "input_file": input_file,
        "output_file": f"{TESTS_DIR}/{name}.spec.ts",
        "branch": f"test/{name}",
        "history": [],
    }, config)

    # When the graph pauses (interrupt), ask the question and resume with the answer
    while "__interrupt__" in output:
        question = output["__interrupt__"][0].value
        answer = input(question)
        output = await app.ainvoke(Command(resume=answer), config)

    return output


def print_summary(results: dict):
    print("\n===== Summary =====")
    for input_file, output in results.items():
        if "test_status" not in output:
            print(f"{input_file}: SKIPPED")
        else:
            pr = output["pr_url"] or "no pull request"
            print(f"{input_file} -> {output['output_file']}: test {output['test_status'].upper()}, "
                  f"review {output['review_status'].upper()}, {output['steps']} supervisor steps, {pr}")


async def main():
    # Print the graph as an ASCII diagram (needs: pip install grandalf)
    app.get_graph().print_ascii()

    results = {}
    for input_file in sorted(glob.glob(f"{TEST_CASES_DIR}/TC*.txt")):
        print(f"\n########## {input_file} ##########")
        results[input_file] = await run_workflow(input_file)

    print_summary(results)


asyncio.run(main())
