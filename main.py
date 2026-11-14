
import requests
from meetings import arrange_meeting, show_meetings

MODEL = "llama3.2:1b"
OLLAMA_URL = "http://localhost:11434/api/chat"


def ask_ai(message):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful AI assistant. "
                            "Answer clearly and briefly."
                        )
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()
        return response.json()["message"]["content"]

    except requests.RequestException as error:
        return (
            "Cannot connect to Ollama. "
            "Make sure Ollama is running and the model is installed. "
            f"Details: {error}"
        )
    except (KeyError, ValueError) as error:
        return f"Unexpected AI response: {error}"


def main():
    print("=" * 45)
    print("             MY AI AGENT")
    print("=" * 45)

    print("\nWelcome! Your AI Agent is ready.")
    print("\nAvailable commands:")
    print("1. Schedule a meeting")
    print("2. Show meetings")
    print("3. Ask any question")
    print("4. Exit")

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        command = user_input.lower()

        if command in ["exit", "quit", "bye"]:
            print("\nAI Agent: Goodbye!")
            break

        elif (
            "show meeting" in command
            or "list meeting" in command
            or "my meeting" in command
        ):
            show_meetings()

        elif (
            "meeting" in command
            or "schedule" in command
            or "appointment" in command
        ):
            arrange_meeting()

        else:
            answer = ask_ai(user_input)
            print("\nAI Agent:", answer)


if __name__ == "__main__":
    main()




