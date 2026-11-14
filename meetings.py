
import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
TIMEZONE = "Asia/Karachi"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
MEETINGS_FILE = os.path.join(BASE_DIR, "meetings.json")


def connect_calendar():
    credentials = None

    if os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE, SCOPES
        )

    if not credentials or not credentials.valid:
        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    "credentials.json not found in MY AI AGENT folder."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            credentials = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w", encoding="utf-8") as file:
            file.write(credentials.to_json())

    return build("calendar", "v3", credentials=credentials)


def arrange_meeting():
    print("\nAI Agent: Let's arrange your meeting!")

    person = input("Meeting with: ").strip()
    date = input("Date (YYYY-MM-DD): ").strip()
    time = input("Time (HH:MM): ").strip()
    purpose = input("Meeting purpose: ").strip()

    if not all([person, date, time, purpose]):
        print("AI Agent: All meeting details are required.")
        return

    try:
        start = datetime.strptime(
            f"{date} {time}", "%Y-%m-%d %H:%M"
        ).replace(tzinfo=ZoneInfo(TIMEZONE))

        if start <= datetime.now(ZoneInfo(TIMEZONE)):
            print("AI Agent: Please choose a future date and time.")
            return

    except ValueError:
        print("AI Agent: Invalid date or time.")
        return

    end = start + timedelta(hours=1)

    print("\n--- Meeting Details ---")
    print("Person:", person)
    print("Date:", date)
    print("Time:", time)
    print("Purpose:", purpose)
    print("Duration: 1 hour")
    print("Timezone:", TIMEZONE)

    confirm = input(
        "\nAdd this meeting to Google Calendar? (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        print("AI Agent: Meeting cancelled.")
        return

    event = {
        "summary": f"Meeting with {person}",
        "description": purpose,
        "start": {
            "dateTime": start.isoformat(),
            "timeZone": TIMEZONE
        },
        "end": {
            "dateTime": end.isoformat(),
            "timeZone": TIMEZONE
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 10}
            ]
        }
    }

    try:
        service = connect_calendar()

        created_event = service.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        meeting = {
            "person": person,
            "date": date,
            "time": time,
            "purpose": purpose,
            "calendar_event_id": created_event["id"]
        }

        with open(MEETINGS_FILE, "a", encoding="utf-8") as file:
            file.write(json.dumps(meeting) + "\n")

        print("\nAI Agent: Meeting created successfully!")
        print("Google Calendar:", created_event.get("htmlLink"))

    except Exception as error:
        print("\nAI Agent: Could not create meeting.")
        print("Error:", error)


def show_meetings():
    print("\nAI Agent: Your Saved Meetings")

    if not os.path.exists(MEETINGS_FILE):
        print("No meetings found.")
        return

    found = False

    with open(MEETINGS_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            try:
                meeting = json.loads(line)
            except json.JSONDecodeError:
                continue

            if not isinstance(meeting, dict):
                continue

            found = True

            print("--------------------")
            print("Person:", meeting.get("person", "Unknown"))
            print("Date:", meeting.get("date", "Unknown"))
            print("Time:", meeting.get("time", "Unknown"))
            print("Purpose:", meeting.get("purpose", "Unknown"))

    if not found:
        print("No meetings found.")


if __name__ == "__main__":
    arrange_meeting()


