import sys
from pathlib import Path
import win32evtlog
import socket
import requests
from datetime import datetime

# Add parent directory to path to enable imports from sibling packages
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.incident_schema import Incident


MCP_SERVER_URL = "http://localhost:8000/tool/new_incident"

def read_system_errors():
    server = "localhost"
    logtype = "System"
    hand = win32evtlog.OpenEventLog(server, logtype)

    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    events = win32evtlog.ReadEventLog(hand, flags, 0)

    incidents = []

    for event in events:
        if event.EventType == win32evtlog.EVENTLOG_ERROR_TYPE:
            incidents.append(Incident(
                host=socket.gethostname(),
                source=logtype,
                event_id=event.EventID,
                level="ERROR",
                message=" ".join(event.StringInserts) if event.StringInserts else "No message",
                timestamp=str(event.TimeGenerated)
            ))

    return incidents

def send_to_mcp(incident: Incident):
    response = requests.post(MCP_SERVER_URL, json=incident)
    print("Sent incident:", response.status_code)

if __name__ == "__main__":
    errors = read_system_errors()
    for incident in errors:
        send_to_mcp(incident)
