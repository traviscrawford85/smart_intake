# Clio Lead Intake System

A containerized system for processing and managing lead intake for Clio Grow, consisting of two microservices:

1. **Intake Agent** - FastAPI proxy server that receives leads from web forms and voice agents
2. **Intake Admin** - Streamlit dashboard for managing API keys, webhooks, and monitoring metrics

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Forms     │    │  CaptureNow     │    │   Other         │
│   & Voice Bots  │    │  Agent          │    │   Sources       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Intake Agent           │
                    │    (FastAPI Proxy)        │
                    │    Port: 8000             │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Clio Grow API          │
                    │    (Lead Inbox)           │
                    └───────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              Intake Admin Dashboard                 │
│              (Streamlit + FastAPI)                  │
│              Frontend: 8501 | Backend: 8001         │
│  • API Key Management                              │
│  • Webhook Configuration                           │
│  • Lead Metrics & Monitoring                       │
│  • System Health Checks                            │
└─────────────────────────────────────────────────────┘
```

## Project Structure

```
smart_intake/
├── docker-compose.yml          # Container orchestration
├── README_NEW.md               # This file
├── BUILD_INSTRUCTIONS.md       # Build and deployment guide
│
├── intake_agent/               # Lead processing service
│   ├── Dockerfile
│   ├── requirements_clean.txt
│   ├── fastapi_proxy_clean.py  # Main application
│   ├── .env                    # Environment variables
│   └── logs/                   # Application logs
│
└── intake_admin/               # Management dashboard
    ├── Dockerfile
    ├── requirements.txt
    ├── Dashboard.py            # Streamlit frontend
    ├── backend.py              # FastAPI backend
    └── data/                   # Persistent storage
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Clio Grow Lead Inbox Token

### Environment Setup

Edit `intake_agent/.env` with your Clio credentials:
```env
CLIO_GROW_INBOX_URL=https://grow.clio.com/inbox_leads
LEAD_INBOX_TOKEN=your_clio_token_here
```

### Running the Application

1. Start all services:
```bash
docker-compose up -d
```

2. Check service status:
```bash
docker-compose ps
```

3. View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f intake-agent
docker-compose logs -f intake-admin
```

### Accessing the Services

- **Admin Dashboard**: http://localhost:8501 (Streamlit UI)
- **Admin API**: http://localhost:8001 (FastAPI backend)
- **Intake Agent**: http://localhost:8000 (Lead processing endpoints)

## License

This project is licensed under the MIT License.
