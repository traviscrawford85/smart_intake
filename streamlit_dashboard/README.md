    Admin settings page to generate/view API keys

    FastAPI backend with endpoints for:

        Listing keys (for admin)

        Generating new keys

        Revoking keys

        Webhook endpoint with API key authentication

    Minimal frontend: Jinja2 templates for form/buttons

    Database: SQLite for API key storage (hashed)

This is production-minded: API keys are hashed, never displayed after creation, and can be rotated/revoked.

intake_admin/
│
├── app/
│   ├── main.py          # FastAPI app (all endpoints)
│   ├── models.py        # SQLAlchemy models
│   ├── db.py            # DB setup
│   ├── templates/
│   │    ├── settings.html    # Admin UI (Jinja2)
│   │    └── base.html
│   └── static/
│        └── style.css
├── requirements.txt
└── README.md


## Example: Intake Agent POST (using your API key)

# my app webhook and my app generated api-key
curl -X POST http://localhost:8000/webhook/capturenow \
    -H "Content-Type: application/json" \
    -H "x-api-key: your-generated-api-key" \
    -d '{"first_name": "Minnie", "last_name": "Mouse", "message": "Help n

    Summary

    Admin page: Generate, list, revoke keys

    API keys: Only shown once; hashed in DB

    Webhook: Checks the key every request

    Frontend: Can be expanded/secured (add login etc)