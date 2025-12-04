# GEMINI.md

## 1. プロジェクト概要

このプロジェクトは、ポケモンカードを管理するためのWebアプリケーションです。

PythonのWebフレームワークである**Django**をバックエンドに、データベースとして**PostgreSQL**を使用しています。全ての実行環境は**Docker**および**Docker Compose**によってコンテナ化されており、開発環境の構築が容易になっています。

- **目的**: 個人または家庭内で所有するポケモンカードの情報をデジタルで一元管理する。
- **主な技術スタック**:
  - **言語**: Python 3.11
  - **フレームワーク**: Django 5.0
  - **データベース**: PostgreSQL 16
  - **インフラ**: Docker / Docker Compose
  - **Python依存関係管理**: Poetry
  - **フロントエンド**: Bootstrap 5.3

## 2. ビルドと実行

### Dockerを使用した起動

プロジェクトの起動、停止は `docker-compose` コマンドで行います。

**1. 初回ビルドと起動**

```bash
docker-compose up --build -d
```

**2. 起動（2回目以降）**

```bash
docker-compose up -d
```

**3. 停止**

```bash
docker-compose down
```

アプリケーションには、Webブラウザで `http://localhost:8000` にアクセスします。

### Django管理コマンドの実行

`manage.py` を使ったコマンド（例: `migrate`, `createsuperuser`）は、`web`コンテナ内で実行します。

```bash
# webコンテナのシェルにアクセス
docker-compose exec web bash

# コンテナ内でコマンドを実行
python manage.py migrate
python manage.py createsuperuser
```

## 3. 開発規約

### 依存関係の管理

- Pythonのライブラリは **Poetry** を使用して管理します。
- 新しいライブラリを追加する場合:
  ```bash
  # webコンテナのシェルにアクセス
  docker-compose exec web bash

  # ライブラリを追加
  poetry add <ライブラリ名>
  ```
- `pyproject.toml` と `poetry.lock` の変更をコミットしてください。

### コーディングスタイル

- Pythonのコーディングスタイルは **PEP 8** に準拠することを推奨します。
- `black` や `flake8` などのフォーマッタ/リンターの導入は現在行われていませんが、将来的に導入する可能性があります。

### ドキュメント

- プロジェクトに関するドキュメントは `docs/` ディレクトリに集約します。
  - `00_tasks.md`: タスク管理
  - `10_function list.md`: 機能一覧
  - `20_architecture.md`: アーキテクチャ設計
- 大きな変更や機能追加を行う際は、関連ドキュメントの更新を推奨します。
