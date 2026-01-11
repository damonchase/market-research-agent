FROM python:3.11-slim

# Install Chromium and its dependencies for Kaleido
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Install uv and dependencies
RUN pip install uv
RUN uv export --format requirements-txt > requirements.txt
RUN pip install -r requirements.txt

# Start command
CMD ["gunicorn", "-w", 4, "-k", uvicorn.workers.UvicornWorker, "app.main:app", "--bind", "0.0.0.0:10000"]