# Streamlit Dashboard Entry Point
# (Move your Streamlit dashboard code here)

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configuration
INTAKE_AGENT_URL = "http://localhost:8000"  # intake_agent FastAPI server
ADMIN_API_URL = "http://localhost:8001"     # Admin backend API

st.set_page_config(
    page_title="Clio Intake Dashboard", 
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ...existing dashboard code (see previous Dashboard.py)...
