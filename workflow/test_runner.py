# Saves a test file and runs it with Playwright

import glob
import os
import subprocess

from config import HEADLESS


def save_test(path: str, code: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as file:
        file.write(code)


def run_test(path: str):
    command = ["npx", "playwright", "test", path, "--reporter=list"]
    if not HEADLESS:
        command.append("--headed")  # opens a visible browser window
    result = subprocess.run(command, capture_output=True, text=True)

    output = result.stdout + result.stderr
    # On failure, Playwright saves a snapshot of the page in error-context.md. Add it to the output.
    for context_file in glob.glob("test-results/**/error-context.md", recursive=True):
        with open(context_file) as file:
            output += "\n\nPage at the moment of failure:\n" + file.read()

    passed = result.returncode == 0
    return passed, output
