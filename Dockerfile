FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm-dev \
    libasound2 \
    libpangocairo-1.0-0 \
    libx11-xcb1 \
    libx11-6 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps chromium

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
