FROM python:3.11-slim

# 1. Install system dependencies for Chrome, Kaleido, and building Python packages
RUN apt-get update && apt-get install -y \
    chromium \
    libnss3 \
    libatk-bridge2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 3. Copy only dependency files first (better caching)
COPY pyproject.toml uv.lock ./

# 4. Install dependencies using uv
# --frozen ensures it uses the exact versions in your lockfile
RUN uv pip install --system --frozen -r pyproject.toml

# 5. Copy the rest of your code
COPY . .

# 6. Start the app
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:10000"]