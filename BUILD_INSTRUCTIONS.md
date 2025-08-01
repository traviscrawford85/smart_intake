docker-compose build
docker-compose build intake-admin
docker-compose build intake-agent
docker-compose up -d
docker-compose ps
# Build and Test Instructions

## Building the Container

```bash
# Build the single service container
docker-compose build
```

## Testing the Setup

### 1. Start the Service
```bash
# Copy environment configuration
cp .env.example .env

# Edit .env with your Clio Lead Inbox Token
nano .env

# Start the service
docker-compose up -d

# Verify the service is running
docker-compose ps
```

### 2. Health Checks
```bash
# Check API health
curl http://localhost:8000/health
```

### 3. Test Lead Submission
```bash
# Test direct payload format
curl -X POST http://localhost:8000/webhook/clio-intake \
  -H "Content-Type: application/json" \
  -d '{
    "inbox_lead": {
      "first_name": "Test",
      "last_name": "User",
      "email": "test@example.com",
      "phone_number": "555-0123",
      "message": "Test message from container setup",
      "referring_url": "https://test.com",
      "source": "Container Test"
    }
  }'

# Test envelope payload format
curl -X POST http://localhost:8000/webhook/clio-intake \
  -H "Content-Type: application/json" \
  -d '{
    "inbox_leads": [
      {
        "first_name": "Test",
        "last_name": "Envelope",
        "email": "envelope@example.com",
        "phone_number": "555-0456",
        "message": "Test envelope message",
        "referring_url": "https://test.com",
        "source": "Envelope Test"
      }
    ]
  }'
```

### 4. API Documentation
```bash
# View interactive API docs
open http://localhost:8000/docs
```

docker-compose logs -f
docker-compose logs -f intake-agent
docker-compose logs -f intake-admin
### 5. Log Monitoring
```bash
# View logs in real-time
docker-compose logs -f
```

docker-compose -f docker-compose.yml up -d
docker-compose up -d --restart=unless-stopped
## Production Deployment

### 1. Environment Configuration
```bash
# Production environment file
cat > .env << EOF
CLIO_GROW_INBOX_URL=https://grow.clio.com/inbox_leads
LEAD_INBOX_TOKEN=your_production_token_here
DATABASE_URL=sqlite:///app.db
ENVIRONMENT=production
EOF
```

### 2. Production Docker Compose
```bash
# Start in production mode
docker-compose up -d

# Enable auto-restart
docker-compose up -d --restart=unless-stopped
```

### 3. Reverse Proxy Setup (Nginx Example)
```nginx
# /etc/nginx/sites-available/intake-system
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Verification Checklist

- [ ] Service starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] Test payloads process successfully
- [ ] Logs show successful Clio API communication
- [ ] API documentation is accessible
- [ ] Container restarts automatically on failure
- [ ] Environment variables are properly configured
