from app.llm import chat


def main() -> None:
    print("Contacting Qwen Cloud...\n")
    reply = chat(
        "In one sentence, what is a Hausa tatsuniya?",
        system="You are a concise assistant.",
    )
    print("Qwen replied:\n")
    print(reply)
    print("\nConnection works. Day 1 done.")


if __name__ == "__main__":
    main()
