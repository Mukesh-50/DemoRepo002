# All settings for the multi-agent test generator in one place

import os

from dotenv import load_dotenv

# Load OPENAI_API_KEY (and optional OPENAI_MODEL) from the .env file
load_dotenv()

# AI model used by every agent. Set OPENAI_MODEL in .env to change it.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

# Safety limits, so the agents can never loop forever
MAX_SUPERVISOR_STEPS = 12   # how many times the supervisor may pick an agent
MAX_HEAL_RUNS = 3           # how many fixed versions the healer may try

# Show the browser while the agents work (set HEADLESS=true in .env to hide it)
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

# Where the manual test cases are, and where generated tests are saved
TEST_CASES_DIR = "test_cases"
TESTS_DIR = "tests"

# Pull requests are opened against this branch
BASE_BRANCH = "main"

# Only these Playwright MCP tools are given to the agents.
# Tools that run custom code or read local files (browser_run_code_unsafe,
# browser_evaluate, browser_file_upload, ...) are left out on purpose.
SAFE_BROWSER_TOOLS = [
    "browser_navigate",
    "browser_navigate_back",
    "browser_snapshot",
    "browser_click",
    "browser_type",
    "browser_fill_form",
    "browser_press_key",
    "browser_select_option",
    "browser_hover",
    "browser_wait_for",
]
