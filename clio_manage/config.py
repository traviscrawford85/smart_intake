
import os

CLIO_CLIENT_ID = os.getenv("CLIO_CLIENT_ID", "Jvqn16tLYFJWrnc9tIryTxEB5CyFMLzknU2DmtEy")
CLIO_CLIENT_SECRET = os.getenv("CLIO_CLIENT_SECRET", "8G87Ya8UWowvaYc1GonDgzBcSgE47ADOPRZu8IOY")
CLIO_REDIRECT_URI = os.getenv("CLIO_REDIRECT_URI", "http://127.0.0.1:8080/auth/callback")
CLIO_API_BASE = "https://app.clio.com/api/v4"
CLIO_API_VERSION = "4.0.12"

DATABASE_URL = "sqlite:///./clio_agent.db"
