# --- Stage 1: Node Builder (Tailwind CSS) ---
FROM node:20-slim AS node-builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY . .
RUN npm run build

# --- Stage 2: Python Builder (Dependencies) ---
FROM python:3.11-slim AS python-builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry && poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --no-ansi --no-root --only main

# --- Stage 3: Final Runtime ---
FROM python:3.11-slim AS runtime
WORKDIR /app

# 実行に必要な最小限のライブラリ（libpq, libgl1 for opencv）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 環境変数の設定
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_ENV=production
ENV PORT=8000

# BuilderステージからPythonパッケージをコピー
COPY --from=python-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-builder /usr/local/bin /usr/local/bin

# Node Builderからビルド済みアセットをコピー
COPY --from=node-builder /app/static /app/static

# ソースコードのコピー
COPY . .

# 静的ファイルの集約（本番用）
RUN SECRET_KEY=build-time-dummy-key GEMINI_API_KEY_1=dummy DEBUG=False python manage.py collectstatic --noinput

# 実行スクリプトの準備
RUN chmod +x entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["sh", "./entrypoint.sh"]