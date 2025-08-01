# Smart Intake System - Containerization Plan

## Project Boundaries & Clean Architecture

### Service 1: Intake Admin
**Purpose**: Simple API key management and webhook authentication
- **Technology**: FastAPI with SQLite
- **Container**: `intake-admin`
- **Port**: 8080
- **Core Function**: Generate/manage API keys for secure webhook access

### Service 2: Intake Agent  
**Purpose**: Lead processing proxy for Clio Grow
- **Technology**: FastAPI with direct Clio API integration
- **Container**: `intake-agent` 
- **Port**: 8000
- **Core Function**: Receive leads from various sources, normalize, and forward to Clio

## Issues Identified & Solutions

### 1. Streamlit Dashboard Disconnect
**Problem**: `Dashboard.py` tries to connect to non-existent `/integrations` endpoints
**Solution**: Either:
- A) Remove Streamlit dashboard (recommended for production)
- B) Create a proper integration between FastAPI backend and Streamlit frontend
- C) Replace with simple HTML interface served by FastAPI

### 2. Over-Engineering
**Problem**: Complex auth flows, database models, and routing for simple token-based API
**Solution**: Simplified architecture using only lead inbox token authentication

### 3. Unused Code
**Problem**: 80% of code is unused (OAuth, complex models, test files)
**Solution**: Remove unused files and dependencies

## Recommended Architecture

### Production Setup (Recommended)
```
intake-admin/
├── app/
│   ├── main.py          # FastAPI app with HTML interface
│   ├── models.py        # Simple APIKey model
│   ├── db.py           # SQLite setup
│   └── templates/      # Jinja2 templates (not Streamlit)
├── Dockerfile
└── requirements.txt    # Minimal dependencies

intake-agent/
├── fastapi_proxy_clean.py  # Main application
├── Dockerfile
└── requirements.txt        # Minimal dependencies
```

### Development Setup (Alternative)
If you want to keep Streamlit dashboard:
```
intake-admin/
├── app/
│   ├── main.py          # FastAPI backend with /integrations endpoints
│   └── ...
├── Dashboard.py         # Streamlit frontend  
├── Dockerfile           # Multi-stage: FastAPI + Streamlit
└── requirements.txt
```

## Container Optimizations

### Security
- Non-root users in containers
- Minimal base images (python:3.11-slim)
- Environment-based secrets
- Network isolation

### Performance  
- Layer caching optimization
- Minimal dependencies
- Health checks for monitoring
- Log rotation and management

### Deployment
- Docker Compose for local development
- Production-ready with reverse proxy support
- Horizontal scaling capability
- Monitoring and observability

## Next Steps

1. **Choose Architecture**: Production (no Streamlit) vs Development (with Streamlit)
2. **Clean Unused Code**: Remove 80% of unused files
3. **Fix Dependencies**: Minimal requirements files
4. **Test Integration**: Ensure Clio API connectivity
5. **Documentation**: Update all docs for clean architecture
