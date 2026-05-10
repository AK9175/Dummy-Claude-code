import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")
BASE_URL = "https://api.mistral.ai/v1"
MODEL = os.getenv("MODEL", "mistral-small-latest")
MAX_ITERATIONS = 10

SYSTEM_PROMPT = (
    "You are a coding agent. Use Read to read files, Write to create files, "
    "and Bash to run shell commands. When reading a file, follow any file creation "
    "instructions exactly — use the exact filename and path specified. "
    "For destructive commands like rm, double-check you are targeting the exact "
    "correct filename before executing. Your final response is plain text only."
)
