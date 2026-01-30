from fastapi import FastAPI
import requests
from shared.incident_schema import Incident

app = FastAPI()

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/XXX/YYY/ZZZ"

@app.post("/create_ticket")
def create_ticket(incident: Incident):
    message = {
        "text": (
            f"🚨 *New Incident Detected*\n\n"
            f"*Host:* {incident['host']}\n"
            f"*Source:* {incident['source']}\n"
            f"*Event ID:* {incident['event_id']}\n"
            f"*Level:* {incident['level']}\n"
            f"*Time:* {incident['timestamp']}\n\n"
            f"*Message:*\n{incident['message']}"
        )
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=message)

    return {"slack_status": response.status_code}
