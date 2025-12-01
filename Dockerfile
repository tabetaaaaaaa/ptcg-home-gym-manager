# ベースイメージ: Python 3.11 (軽量版)
FROM python:3.11-slim

# コンテナ内の作業ディレクトリ設定
WORKDIR /app

# 環境変数の設定 (Pythonのバッファリング無効化など)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 依存ライブラリのインストール
# ビルド時間を短縮するため、requirements.txtを先にコピー
# COPY requirements.txt /app/
# RUN pip install --upgrade pip && pip install -r requirements.txt

# システムの依存関係が必要な場合はここに追加（PostgreSQL用ライブラリなど）
# 今回は slim イメージなので、psycopg2-binary を使うなら追加インストール不要な場合が多いですが、
# ビルドエラーが出る場合は gcc libpq-dev などが必要になります。一旦このまま進めます。

# Poetryのインストール
RUN pip install poetry

# Poetryの設定: 仮想環境を作らない（コンテナ環境に直接インストール）
RUN poetry config virtualenvs.create false

# 依存関係ファイルのコピー
# poetry.lock がまだない場合でもエラーにならないよう * をつけたり、コピー順を工夫します
COPY pyproject.toml poetry.lock* /app/

# 依存関係のインストール
# --no-root: プロジェクト自体はインストールせず、ライブラリのみ入れる
# 初回は pyproject.toml しかないため、lockファイル生成も兼ねて実行されます
RUN if [ -f pyproject.toml ]; then poetry install --no-root; fi

# ソースコードのコピー
# COPY . /app/