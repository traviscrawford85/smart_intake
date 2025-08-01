# Smart Intake System

A containerized solution for managing lead intake through Clio Grow API integration.

## Architecture

### Intake Admin (`intake_admin`)
- **Purpose**: API key management and webhook endpoint for secure intake processing
- **Technology**: FastAPI with SQLite database
- **Port**: 8080 (external)
- **Features**:
  - Web-based API key generation and management
  - Secure webhook endpoint with API key authentication
  - Health monitoring endpoints

### Intake Agent (`intake_agent`)  
- **Purpose**: Lead processing proxy for Clio Grow integration
- **Technology**: FastAPI with direct Clio API integration
- **Port**: 8000 (external)
- **Features**:
  - Multiple webhook endpoints for different payload formats
  - Auto-detection of payload structure (envelope vs direct)
  - Clio Grow Lead Inbox API integration
  - Comprehensive logging and health monitoring

## Quick Start

1. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your Clio Lead Inbox Token
   ```

2. **Start Services**:
   ```bash
   docker-compose up -d
   ```

3. **Access Services**:
   - Intake Admin: http://localhost:8080
   - Intake Agent: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Configuration

### Required Environment Variables

```bash
# Clio Integration (Required)
CLIO_GROW_INBOX_URL=https://grow.clio.com/inbox_leads
LEAD_INBOX_TOKEN=your_clio_lead_inbox_token

# Database (Optional)
DATABASE_URL=sqlite:///app.db

# Environment (Optional)
ENVIRONMENT=production
```

### Obtaining Clio Lead Inbox Token

1. Log into your Clio Grow account
2. Navigate to Settings > Integrations
3. Generate a Lead Inbox Token
4. Copy the token to your `.env` file

## API Endpoints

### Intake Agent (Primary Service)

#### Webhook Endpoints
- `POST /webhook/clio-intake` - Unified endpoint (auto-detects format)
- `POST /webhook/direct` - Direct web form payloads
- `POST /webhook/envelope` - Capture Now agent envelopes

#### Monitoring
- `GET /health` - Health check with Clio API connectivity
- `GET /` - Service information and endpoint listing
- `GET /docs` - Interactive API documentation

### Intake Admin (Management Service)

#### Management Interface
- `GET /settings` - Web interface for API key management
- `POST /generate_key` - Generate new API keys
- `POST /revoke_key` - Revoke existing API keys

#### Secure Webhook
- `POST /webhook/capturenow` - Authenticated webhook (requires x-api-key header)

## Payload Formats

### Direct Payload (Web Forms)
```json
{
  "inbox_lead": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone_number": "555-0123",
    "message": "I need legal help",
    "referring_url": "https://mysite.com/contact",
    "source": "Contact Form"
  }
}
```

### Envelope Payload (Capture Now Agent)
```json
{
  "inbox_leads": [
    {
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane@example.com",
      "phone_number": "555-0456",
      "message": "Call transcript from AI assistant...",
      "referring_url": "https://mysite.com",
      "source": "Voice Agent"
    }
  ]
}
```

### Flat Payload (Legacy Support)
```json
{
  "first_name": "Bob",
  "last_name": "Wilson",
  "email": "bob@example.com",
  "phone_number": "555-0789",
  "message": "Direct submission",
  "referring_url": "https://mysite.com",
  "source": "API"
}
```

## Health Monitoring

Both services include comprehensive health monitoring:

### Container Health Checks
- Automatic health checks every 30 seconds
- HTTP-based liveness probes
- Container restart on health check failures

### Service Monitoring
- `/health` endpoints with detailed status
- Clio API connectivity testing
- Configuration validation
- Structured logging with log rotation

## Security

### API Key Authentication (Intake Admin)
- SHA-256 hashed API key storage
- Header-based authentication (`x-api-key`)
- Key revocation capability
- One-time key display for security

### Network Security
- Internal Docker network isolation
- Non-root container users
- Minimal container attack surface
- HTTPS ready (configure reverse proxy)

## Development vs Production

### Development
```bash
# Start with file watching and reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production
```bash
# Start optimized for production
docker-compose up -d
```

## Monitoring and Logs

### Log Management
- Structured JSON logging
- Log rotation (10MB files, 30-day retention)
- Centralized logging in `/app/logs`
- Docker volume persistence

### Health Monitoring
```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:8080/health

# Monitor logs
docker-compose logs -f intake-agent
docker-compose logs -f intake-admin
```

## Troubleshooting

### Common Issues

1. **Clio API Connection Fails**
   - Verify `LEAD_INBOX_TOKEN` is correct
   - Check network connectivity to `grow.clio.com`
   - Review logs for specific API errors

2. **Container Won't Start**
   - Check environment variables in `.env`
   - Verify Docker has sufficient resources
   - Review container logs: `docker-compose logs [service]`

3. **Webhook Returns 401/403**
   - Ensure API key is properly configured (Intake Admin)
   - Verify `x-api-key` header is included
   - Check API key hasn't been revoked

### Log Analysis
```bash
# View real-time logs
docker-compose logs -f

# Search for errors
docker-compose logs | grep ERROR

# Check specific service
docker-compose logs intake-agent | grep clio
```

## Deployment

### Production Checklist
- [ ] Update `.env` with production values
- [ ] Configure reverse proxy (nginx/traefik) for HTTPS
- [ ] Set up log aggregation (ELK, Splunk, etc.)
- [ ] Configure monitoring alerts
- [ ] Backup database volumes
- [ ] Update Docker Compose for production settings

### Scaling
```bash
# Scale intake agent for high load
docker-compose up -d --scale intake-agent=3
```

## Support

For issues and questions:
1. Check health endpoints for service status
2. Review logs for specific error messages
3. Verify Clio API token and permissions
4. Test with simple payload using `/docs` interface
