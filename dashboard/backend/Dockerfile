FROM python:3.12-slim

WORKDIR /app

# Build context is the theta-lab repo ROOT (not dashboard/backend) -- the
# dashboard imports mcp/reports and scripts/realized_pnl.py directly and
# needs the same data/ layout those modules already expect.
COPY dashboard/backend/requirements.txt /app/dashboard/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/dashboard/backend/requirements.txt

COPY mcp /app/mcp
COPY scripts /app/scripts
COPY config /app/config
COPY dashboard/backend /app/dashboard/backend

# CWD stays at the repo root (WORKDIR /app) -- unified_master_report_production.py
# and realized_pnl.py both use CWD-relative paths ("data/...", "logs/...")
# exactly as they do when run directly from /home/rahulvadera/projects/theta-lab
# (see CLAUDE.md). PYTHONPATH adds the dashboard package's own location so
# `uvicorn app.main:app` still resolves from here instead of needing WORKDIR
# to be dashboard/backend (which would break every relative data/logs path).
ENV PYTHONPATH=/app/dashboard/backend
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
