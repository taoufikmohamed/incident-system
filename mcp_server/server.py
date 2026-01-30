from fastapi import FastAPI
from shared.incident_schema import Incident
import requests

app = FastAPI()

TICKET_AGENT_URL = "http://localhost:9000/create_ticket"

@app.post("/tool/new_incident")
def new_incident(incident: Incident):
    """
    MCP Tool: new_incident
    """
    # Forward incident to ticket agent
    response = requests.post(TICKET_AGENT_URL, json=incident)
    return {"status": "forwarded", "ticket_agent": response.status_code}
