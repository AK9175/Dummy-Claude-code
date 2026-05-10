import argparse
import sys

from openai import OpenAI

from .agent import agent_loop
from .config import API_KEY, BASE_URL, MODEL


def interactive_mode(client: OpenAI) -> None:
    print(f"Dummy Claude Code  |  model: {MODEL}")
    print("Type 'exit' or press Ctrl+C to quit.\n")
    while True:
        try:
            prompt = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if not prompt:
            continue
        if prompt.lower() in ("exit", "quit"):
            print("Bye!")
            break

        try:
            result = agent_loop(client, prompt, verbose=True)
            print(f"\n{result}\n")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dummy-claude-code",
        description="AI coding agent powered by Mistral",
    )
    parser.add_argument("-p", metavar="PROMPT", help="Run a single prompt and exit")
    parser.add_argument("--model", default=MODEL, help="Model to use")
    parser.add_argument(
        "--no-verbose", action="store_true", help="Hide tool call logs"
    )
    args = parser.parse_args()

    if not API_KEY:
        sys.exit("Error: MISTRAL_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    verbose = not args.no_verbose

    if args.p:
        result = agent_loop(client, args.p, verbose=verbose)
        print(result)
    else:
        interactive_mode(client)


if __name__ == "__main__":
    main()
