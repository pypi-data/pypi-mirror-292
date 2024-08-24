import os
import sys
import logging
import httpx
from gpt_cli.config import get_api_key
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('httpx').setLevel(logging.WARNING)

RESET = '\033[0m'
BOLD = '\033[1m'
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'

def print_help():
    help_text = """
    Usage: gpt [OPTIONS]

    Options:
      -m, --model TEXT         Specify the GPT model to use (default: gpt-4o)
      -t, --tokens INTEGER     Specify the maximum number of tokens for the response (default: 1000)
      -T, --temperature FLOAT  Specify the temperature for the response (default: 0.6)
      -h, --help               Show this message and exit
    """
    print(help_text)

def main():
    api_key = get_api_key()
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set. Please set it using the following command:")
        print("\nexport OPENAI_API_KEY='your_openai_api_key'\n")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    model = "gpt-4o"
    max_tokens = 1000
    temperature = 0.6

    args = iter(sys.argv[1:])
    for arg in args:
        if arg in ("-m", "--model"):
            model = next(args, model)
        elif arg in ("-t", "--tokens"):
            max_tokens = int(next(args, max_tokens))
        elif arg in ("-T", "--temperature"):
            temperature = float(next(args, temperature))
        elif arg in ("-h", "--help"):
            print_help()
            sys.exit(0)

    conversation_history = [
        {
            "role": "system",
            "content": (
                "The following is a conversation with an AI assistant in Terminal (shell). "
                "The assistant is helpful, creative, clever, and very friendly."
            ),
        }
    ]

    print("Enter your questions below. Type 'exit' to end the session.\n")

    while True:
        try:
            user_input = input(f"{CYAN}{BOLD}You: {RESET}")
            if user_input.lower() in ["exit", "quit"]:
                print(f"{BOLD}Ending the session. Goodbye!{RESET}")
                break

            conversation_history.append({"role": "user", "content": user_input})

            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=conversation_history,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                response = completion.choices[0].message.content
                print(f"{GREEN}{BOLD}AI: {RESET}{YELLOW}{response} {RESET}")

                conversation_history.append({"role": "assistant", "content": response})
            except Exception as e:
                logger.error(f"An error occurred: {e}")
                break

        except KeyboardInterrupt:
            print(f"\n{BOLD}Session interrupted. Goodbye!{RESET}")
            sys.exit(0)

if __name__ == "__main__":
    main()
