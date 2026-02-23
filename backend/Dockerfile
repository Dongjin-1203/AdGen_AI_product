FROM python:3.12-slim

WORKDIR /app

# 시스템 의존성 (chromium 관련 제거)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ⭐ Playwright Chromium 설치
RUN playwright install chromium && \
    playwright install-deps chromium

# 앱 코드
COPY . .

ENV PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

CMD uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2