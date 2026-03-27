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
    try:
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

        print(f"✓ Read {len(incidents)} ERROR events from Windows Event Log")
        return incidents
    except Exception as e:
        print(f"✗ Error reading Event Log: {e}")
        return []

def send_to_mcp(incident: Incident):
    try:
        response = requests.post(MCP_SERVER_URL, json=incident, timeout=5)
        print(f"  → Sent incident to MCP Server: Status {response.status_code}")
        return response.status_code
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Connection failed: MCP Server not running at {MCP_SERVER_URL}")
        return None
    except Exception as e:
        print(f"  ✗ Error sending incident: {e}")
        return None

if __name__ == "__main__":
    print(f"Starting Log Agent...")
    print(f"MCP Server URL: {MCP_SERVER_URL}")
    print()
    
    errors = read_system_errors()
    
    if not errors:
        print("ℹ No ERROR events found in System Event Log")
    else:
        print(f"\nSending {len(errors)} incident(s) to MCP Server...")
        sent_count = 0
        for incident in errors:
            status = send_to_mcp(incident)
            if status:
                sent_count += 1
        print(f"\n✓ Successfully sent {sent_count}/{len(errors)} incidents")
