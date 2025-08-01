FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY Dashboard.py backend.py ./

# Create necessary directories
RUN mkdir -p data logs

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check endpoint (check both backend and streamlit)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health && curl -f http://localhost:8501/_stcore/health || exit 1

# Expose ports (backend: 8001, streamlit: 8501)
EXPOSE 8001 8501

# Create startup script
USER root
RUN echo '#!/bin/bash\n\
# Start the backend API in the background\n\
python backend.py &\n\
BACKEND_PID=$!\n\
\n\
# Wait a moment for backend to start\n\
sleep 3\n\
\n\
# Start Streamlit dashboard\n\
streamlit run Dashboard.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true &\n\
STREAMLIT_PID=$!\n\
\n\
# Function to cleanup processes\n\
cleanup() {\n\
    echo "Shutting down..."\n\
    kill $BACKEND_PID $STREAMLIT_PID 2>/dev/null\n\
    exit 0\n\
}\n\
\n\
# Set up signal handlers\n\
trap cleanup TERM INT\n\
\n\
# Wait for either process to exit\n\
wait -n $BACKEND_PID $STREAMLIT_PID\n\
\n\
# If we get here, one process exited, so cleanup\n\
cleanup\n\
' > start.sh && chmod +x start.sh

USER appuser

# Run the startup script
CMD ["./start.sh"]
