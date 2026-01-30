# Incident System Architecture

## Overview

The Incident System is a distributed monitoring and alerting solution that detects Windows system errors and automatically creates Slack notifications. It follows a microservices architecture with three main components communicating via HTTP APIs.

## System Architecture Diagram

```
┌─────────────────────┐
│  Windows System     │
│  Event Log          │
└──────────┬──────────┘
           │
           │ (win32evtlog)
           │
┌──────────▼──────────────────────────────────────────┐
│  Log Agent (agent_logs)                             │
│  - Reads Windows System errors                      │
│  - Transforms to Incident schema                    │
│  - Sends HTTP POST to MCP Server                    │
│  Port: (Client)                                     │
└──────────┬──────────────────────────────────────────┘
           │
           │ HTTP POST /tool/new_incident
           │
┌──────────▼──────────────────────────────────────────┐
│  MCP Server (mcp_server)                            │
│  - Receives incidents from Log Agent                │
│  - Forwards to Slack Ticket Agent                   │
│  FastAPI Application                                │
│  Port: 8000                                         │
└──────────┬──────────────────────────────────────────┘
           │
           │ HTTP POST /create_ticket
           │
┌──────────▼──────────────────────────────────────────┐
│  Slack Ticket Agent (agent_ticket)                  │
│  - Receives incident data                           │
│  - Formats message for Slack                        │
│  - Sends webhook to Slack                           │
│  FastAPI Application                                │
│  Port: 9000                                         │
└──────────┬──────────────────────────────────────────┘
           │
           │ HTTP POST (Slack Webhook)
           │
           ▼
        Slack Channel
```

## Components

### 1. **Log Agent** (`agent_logs/log_agent.py`)
- **Purpose**: Monitors Windows Event Log for system errors
- **Technology**: `pywin32` for Windows Event Log access
- **Functionality**:
  - Reads Windows System event log backwards
  - Filters for ERROR level events
  - Transforms events into `Incident` objects
  - Sends incidents to MCP Server via HTTP POST
- **Entry Point**: Can be run standalone or scheduled as a task

### 2. **MCP Server** (`mcp_server/server.py`)
- **Purpose**: Central API server that routes incidents to appropriate agents
- **Technology**: FastAPI
- **Port**: `8000`
- **Endpoints**:
  - `POST /tool/new_incident`: Receives incidents and forwards to Slack Ticket Agent
- **Responsibilities**:
  - Acts as orchestrator between Log Agent and Slack Ticket Agent
  - Translates between different communication protocols if needed

### 3. **Slack Ticket Agent** (`agent_ticket/slack_ticket_agent.py`)
- **Purpose**: Creates Slack notifications for incidents
- **Technology**: FastAPI
- **Port**: `9000`
- **Endpoints**:
  - `POST /create_ticket`: Receives incident data and sends to Slack
- **Features**:
  - Formats incident data into readable Slack messages with emojis
  - Sends webhook to configured Slack channel
  - Returns status code of Slack API call

### 4. **Shared Schema** (`shared/incident_schema.py`)
- **Purpose**: Defines common data structure used across all components
- **Data Structure**: `Incident` TypedDict
  - `host`: Hostname where incident occurred
  - `source`: Source of the incident (e.g., "System")
  - `event_id`: Windows Event ID
  - `level`: Severity level (e.g., "ERROR")
  - `message`: Detailed error message
  - `timestamp`: When the incident occurred

## Data Flow

1. **Error Detection**: Log Agent polls Windows Event Log
2. **Error Collection**: Extracts ERROR level events and converts to Incident objects
3. **HTTP Transmission**: Sends incidents to MCP Server (localhost:8000)
4. **Routing**: MCP Server receives and forwards to Slack Ticket Agent (localhost:9000)
5. **Notification**: Slack Ticket Agent formats message and posts to Slack webhook
6. **User Alert**: Incident appears in configured Slack channel

## Communication Protocols

- **Inter-service communication**: HTTP REST (JSON payloads)
- **External notifications**: Slack Webhook API

## Configuration

### Key URLs
- MCP Server: `http://localhost:8000`
- Slack Ticket Agent: `http://localhost:9000`
- Slack Webhook: Configured in `slack_ticket_agent.py` (requires setup)

## Deployment Considerations

- All services run on `localhost` (suitable for single-machine deployment)
- Slack webhook URL must be configured before deployment
- Windows Event Log access requires appropriate permissions
- Services should be started in order: MCP Server → Slack Ticket Agent → Log Agent

## Technology Stack

- **Runtime**: Python 3.7+
- **Web Framework**: FastAPI + Uvicorn
- **Windows Integration**: pywin32
- **HTTP Client**: requests
- **External Service**: Slack Webhook API

## Scalability & Future Enhancements

- Replace HTTP with message queues (RabbitMQ, Kafka) for distributed deployment
- Add database layer for incident history and analytics
- Implement incident deduplication and aggregation
- Support multiple notification channels (Email, Teams, PagerDuty)
- Add incident severity-based routing and escalation
- Implement authentication between services
