# Incident System

A distributed incident detection and notification system that monitors Windows system errors and sends real-time alerts to Slack.

## 🎯 Overview

The Incident System automatically detects critical errors from Windows Event Logs and creates Slack notifications. It consists of three microservices that work together to monitor, process, and alert on system incidents.

## Tasks
 
  I built a multi-agent incident management system on Windows using FastAPI, uvicorn, NSSM, and Slack integrations.

**Key Features:**
- 🔍 Real-time Windows Event Log monitoring
- 📤 Automatic incident forwarding and routing
- 💬 Slack channel notifications
- 🏗️ Microservices architecture for easy scaling
- 📊 Structured incident schema for consistency

## 📋 System Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design, component descriptions, and data flow diagrams.

### Quick Overview

```
Windows Event Log → Log Agent → MCP Server → Slack Ticket Agent → Slack
```

Three main components:
1. **Log Agent** - Monitors Windows errors
2. **MCP Server** - Routes incidents (FastAPI on port 8000)
3. **Slack Ticket Agent** - Creates Slack alerts (FastAPI on port 9000)

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Windows operating system (for Event Log access)
- Slack workspace with webhook URL
- Administrator access to read Windows Event Log

### Installation

1. **Clone/navigate to the repository:**
   ```bash
   cd incident-system
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Slack webhook:**
   - Open `agent_ticket/slack_ticket_agent.py`
   - Replace `SLACK_WEBHOOK_URL` with your Slack webhook URL
   - Get your webhook URL from: https://api.slack.com/messaging/webhooks

### Running the System

1. **Start the MCP Server:**
   ```bash
   python -m uvicorn mcp_server.server:app --host localhost --port 8000
   ```

2. **In another terminal, start the Slack Ticket Agent:**
   ```bash
   python -m uvicorn agent_ticket.slack_ticket_agent:app --host localhost --port 9000
   ```

3. **In a third terminal, run the Log Agent:**
   ```bash
   python agent_logs/log_agent.py
   ```

## 📁 Project Structure

```
incident-system/
├── agent_logs/              # Log monitoring agent
│   ├── __init__.py
│   └── log_agent.py         # Reads Windows Event Log
├── agent_ticket/            # Slack notification agent
│   ├── __init__.py
│   └── slack_ticket_agent.py # Creates Slack notifications
├── mcp_server/              # Central routing server
│   ├── __init__.py
│   └── server.py            # FastAPI application
├── shared/                  # Shared utilities and schemas
│   ├── __init__.py
│   └── incident_schema.py   # Incident data structure
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── ARCHITECTURE.md         # Detailed architecture documentation
```

## 🔧 Configuration

### Environment Variables (Optional)

You can set these for different deployments:

```bash
# MCP Server
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000

# Slack Ticket Agent
TICKET_AGENT_HOST=localhost
TICKET_AGENT_PORT=9000
```

### Key Configuration Points

| Component | Configuration | Default |
|-----------|---------------|---------|
| Log Agent | MCP Server URL | `http://localhost:8000/tool/new_incident` |
| MCP Server | Ticket Agent URL | `http://localhost:9000/create_ticket` |
| Slack Agent | Slack Webhook URL | `https://hooks.slack.com/services/XXX/YYY/ZZZ` |
| MCP Server | Listen Port | `8000` |
| Ticket Agent | Listen Port | `9000` |

## 📊 Incident Data Schema

All incidents follow this structure:

```python
class Incident(TypedDict):
    host: str              # Hostname where incident occurred
    source: str            # Source of incident (e.g., "System")
    event_id: int         # Windows Event ID
    level: str            # Severity level (e.g., "ERROR")
    message: str          # Detailed error message
    timestamp: str        # ISO timestamp of incident
```

## 🔄 API Endpoints

### MCP Server (Port 8000)

**POST** `/tool/new_incident`
- Receives incident from Log Agent
- Forwards to Slack Ticket Agent
- Returns: `{"status": "forwarded", "ticket_agent": status_code}`

```bash
curl -X POST http://localhost:8000/tool/new_incident \
  -H "Content-Type: application/json" \
  -d '{
    "host": "WORKSTATION-01",
    "source": "System",
    "event_id": 7000,
    "level": "ERROR",
    "message": "Service failed to start",
    "timestamp": "2026-01-30T10:30:45"
  }'
```

### Slack Ticket Agent (Port 9000)

**POST** `/create_ticket`
- Receives incident data
- Formats and sends to Slack
- Returns: `{"slack_status": status_code}`

## 🛠️ Development

### Adding New Features

To add a new notification channel (e.g., Email):

1. Create a new agent in a new directory (e.g., `agent_email/`)
2. Follow the same pattern as `slack_ticket_agent`
3. Create a new FastAPI endpoint
4. Update `mcp_server/server.py` to route to the new agent

### Testing Locally

Send a test incident:

```bash
curl -X POST http://localhost:8000/tool/new_incident \
  -H "Content-Type: application/json" \
  -d '{
    "host": "TEST-HOST",
    "source": "System",
    "event_id": 0,
    "level": "ERROR",
    "message": "Test incident from development",
    "timestamp": "2026-01-30T10:30:45"
  }'
```

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" on port 8000 | Ensure MCP Server is running: `python -m uvicorn mcp_server.server:app --port 8000` |
| "Connection refused" on port 9000 | Ensure Slack Ticket Agent is running: `python -m uvicorn agent_ticket.slack_ticket_agent:app --port 9000` |
| No Slack notifications | Check webhook URL is correct and not expired. Verify Slack workspace permissions. |
| Permission denied reading Event Log | Run as Administrator or add user to Event Log Readers group |
| Module import errors | Ensure you're in the project root and have run `pip install -r requirements.txt` |

## 📦 Dependencies

- **pywin32**: Windows API access for Event Log reading
- **requests**: HTTP client for inter-service communication
- **fastapi**: Web framework for APIs
- **uvicorn**: ASGI server for running FastAPI apps
- **typing_extensions**: Type hints for Python 3.7 compatibility

## 🔐 Security Considerations

- Slack webhook URL is exposed in code (move to environment variables in production)
- Services communicate over HTTP (use HTTPS/mutual TLS in production)
- No authentication between services (add API keys/OAuth in production)
- Event Log read with current user privileges (consider dedicated service account)

## 📈 Scaling

For production deployment:

1. Move services to separate machines
2. Replace HTTP with message queue (RabbitMQ/Kafka)
3. Add database for incident history
4. Implement proper authentication and TLS
5. Add monitoring and health checks
6. Container deployment (Docker/Kubernetes)

See [ARCHITECTURE.md](ARCHITECTURE.md#scalability--future-enhancements) for more details.

## 📝 License

[Add your license information here]

## 👥 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For issues or questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for design details
- Check component logs for error messages

---

**Last Updated**: January 30, 2026
