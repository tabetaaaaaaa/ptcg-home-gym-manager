# ベースイメージ: Python 3.11 (軽量版)
FROM python:3.11-slim

# 環境変数の設定
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 作業ディレクトリ設定
WORKDIR /app

# --- Node.jsのインストール ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Pythonパッケージのビルドに必要なツール
    build-essential \
    libpq-dev \
    # Node.jsインストール用
    curl && \
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    # クリーンアップ
    apt-get purge -y --auto-remove curl && \
    rm -rf /var/lib/apt/lists/*

# Poetryのインストール
RUN pip install poetry

# Poetryの設定: 仮想環境を作成しない
RUN poetry config virtualenvs.create false

# Python依存関係のインストール
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --no-ansi --no-root

# Node.js依存関係のインストール
# package-lock.jsonは初回はないため、エラーにならないように`*`をつけます
COPY package.json package-lock.json* ./
# `npm ci`の方がロックファイルに基づいてクリーンインストールするため、より再現性が高くなります
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# ソースコードはdocker-compose.ymlのvolumesでマウントするため、ここではコピーしない