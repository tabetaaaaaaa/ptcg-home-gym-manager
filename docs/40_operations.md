# 運用・デプロイ手順書

本ドキュメントでは、開発環境 (dev) と本番環境 (prd) の運用方針、および安全なデプロイ手順を記載します。

- [運用・デプロイ手順書](#運用デプロイ手順書)
  - [1. 環境構成の概要](#1-環境構成の概要)
  - [2. 運用スケジュール例](#2-運用スケジュール例)
  - [3. 基本コマンド一覧](#3-基本コマンド一覧)
    - [3.1. dev 環境](#31-dev-環境)
    - [3.2. prd 環境](#32-prd-環境)
  - [4. 開発ワークフロー](#4-開発ワークフロー)
    - [4.1. 日常の開発作業](#41-日常の開発作業)
    - [4.2. main ブランチへのマージ](#42-main-ブランチへのマージ)
    - [4.3. マージ後の動作確認](#43-マージ後の動作確認)
  - [5. prd デプロイ手順](#5-prd-デプロイ手順)
    - [5.1. 標準デプロイ（ダウンタイム最小化版）](#51-標準デプロイダウンタイム最小化版)
    - [5.2. 緊急ロールバック](#52-緊急ロールバック)
  - [6. 注意事項](#6-注意事項)
    - [6.1. 絶対にやってはいけないこと](#61-絶対にやってはいけないこと)
    - [6.2. デプロイ前チェックリスト](#62-デプロイ前チェックリスト)
    - [6.3. prd 稼働中に dev で安全に作業できる理由](#63-prd-稼働中に-dev-で安全に作業できる理由)
  - [7. トラブルシューティング](#7-トラブルシューティング)
    - [7.1. コンテナが起動しない](#71-コンテナが起動しない)
    - [7.2. DB接続エラー](#72-db接続エラー)
    - [7.3. ポートが既に使用されている](#73-ポートが既に使用されている)
    - [7.4. ディスク容量不足](#74-ディスク容量不足)
    - [7.5. マイグレーションエラー](#75-マイグレーションエラー)

---

## 1. 環境構成の概要

環境構成の詳細は [アーキテクチャ設計 (20_architecture.md)](./20_architecture.md) を参照してください。
- **dev 環境**: ポート `8001`、開発・テスト用
- **prd 環境**: ポート `8000`、ユーザー向け本番サービス
- 同一PC上で dev と prd を**同時運用可能**

環境ごとに専用の `.env` ファイルを使用します：

| ファイル       | 用途         | 主な差分                           |
| :------------- | :----------- | :--------------------------------- |
| `.env.dev`     | dev 環境用   | `DEBUG=True`（詳細エラー表示）     |
| `.env.prd`     | prd 環境用   | `DEBUG=False`（セキュリティ確保）  |
| `.env.example` | テンプレート | 新規セットアップ時にコピーして使用 |


---

## 2. 運用スケジュール例

| タイミング     | 作業内容                                       |
| :------------- | :--------------------------------------------- |
| **日常**       | dev 環境で開発、feature ブランチで作業         |
| **機能完成時** | main マージ → dev で動作確認 → prd デプロイ    |
| **週次/月次**  | ログ確認、ディスク使用量確認、不要イメージ削除 |
| **緊急時**     | ロールバック（手順4.2参照）                    |

---

## 3. 基本コマンド一覧

### 3.1. dev 環境

```bash
# ----- 起動・停止 -----

# 起動（フォアグラウンド、ログ表示）
docker compose -f docker-compose.dev.yml up

# 起動（バックグラウンド）
docker compose -f docker-compose.dev.yml up -d

# 停止
docker compose -f docker-compose.dev.yml down

# 再ビルドして起動（Dockerfile や pyproject.toml を変更した場合）
docker compose -f docker-compose.dev.yml up --build
```

```bash
# ----- ログ確認 -----

# リアルタイムログ
docker compose -f docker-compose.dev.yml logs -f web

# 直近50行のログ
docker compose -f docker-compose.dev.yml logs --tail=50 web
```

```bash
# ----- Django 管理コマンド -----

# DBマイグレーションファイル作成（モデル変更後）
docker compose -f docker-compose.dev.yml exec web python manage.py makemigrations

# DBマイグレーション実行
docker compose -f docker-compose.dev.yml exec web python manage.py migrate

# スーパーユーザー作成
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser

# Django シェル起動（デバッグ用）
docker compose -f docker-compose.dev.yml exec web python manage.py shell
```

### 3.2. prd 環境

```bash
# ----- 起動・停止 -----

# 起動（バックグラウンド推奨）
docker compose -f docker-compose.prod.yml up -d

# 停止
docker compose -f docker-compose.prod.yml down

# 再ビルドして起動（デプロイ時）
docker compose -f docker-compose.prod.yml up -d --build
```

```bash
# ----- ログ確認 -----

# リアルタイムログ
docker compose -f docker-compose.prod.yml logs -f web

# 直近50行のログ
docker compose -f docker-compose.prod.yml logs --tail=50 web
```

```bash
# ----- Django 管理コマンド -----

# DBマイグレーション実行
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Django シェル起動
docker compose -f docker-compose.prod.yml exec web python manage.py shell
```

---

## 4. 開発ワークフロー

### 4.1. 日常の開発作業

```bash
# ===== Step 1: feature ブランチを作成 =====
git checkout main
git pull origin main
git checkout -b feature/新機能名

# ===== Step 2: dev 環境を起動 =====
docker compose -f docker-compose.dev.yml up
# dev 環境ではこのタイミングで `entrypoint.sh` により `npm run watch` が自動実行されます。
# CSSを手動でビルドする必要はありません。

# ===== Step 3: 開発作業 =====
# - コードを編集（ホットリロードで即時反映）
# - ブラウザで http://localhost:8001 にアクセスして動作確認
# - モデルを変更した場合はマイグレーションを実行：
docker compose -f docker-compose.dev.yml exec web python manage.py makemigrations
docker compose -f docker-compose.dev.yml exec web python manage.py migrate

# ===== Step 4: 変更をコミット =====
git add .
git commit -m "feat: 新機能の説明"

# ===== Step 5: リモートにプッシュ =====
git push origin feature/新機能名
```

### 4.2. main ブランチへのマージ

```bash
# Step 1: feature ブランチをプッシュ（3.1 の Step 5 で完了済み）

# Step 2: GitHub で PR を作成
# - ブラウザで GitHub リポジトリにアクセス
# - 「Compare & pull request」ボタンをクリック
# - タイトルと説明を入力して「Create pull request」
# - 差分を確認して「Merge pull request」→「Confirm merge」

# Step 3: ローカルの main を更新
git checkout main
git pull origin main

# Step 4: 不要になった feature ブランチを削除
git branch -d feature/新機能名
```

### 4.3. マージ後の動作確認

**マージが完了したら、dev 環境で main ブランチの動作を確認します。**

```bash
# ===== Step 1: dev を main ブランチに切り替え =====
git checkout main
git pull origin main

# ===== Step 2: dev 環境が起動していることを確認 =====
# （停止していた場合は起動）
docker compose -f docker-compose.dev.yml up -d

# ===== Step 3: ブラウザで動作確認 =====
# http://localhost:8001 にアクセスして、マージした機能が正常に動作することを確認

# ===== Step 4: 確認完了 =====
# - 問題なければ、prd デプロイ（セクション4）に進む
# - 続けて開発する場合は、新しい feature ブランチを作成
# - 作業終了の場合は dev を停止：
docker compose -f docker-compose.dev.yml down
```

---

## 5. prd デプロイ手順

### 5.1. 標準デプロイ（ダウンタイム最小化版）

```bash
# ===== Step 1: main ブランチにいることを確認 =====
git checkout main
git pull origin main

# ===== Step 2: 安全確認 =====
git branch --show-current
# 出力が "main" であることを確認

git status
# "nothing to commit, working tree clean" であることを確認

# ===== Step 3: イメージを事前ビルド =====
# ※ この時点では prd コンテナは稼働したまま
docker compose -f docker-compose.prod.yml build

# ===== Step 4: コンテナを新イメージに入れ替え =====
docker compose -f docker-compose.prod.yml up -d

# ===== Step 5: DBマイグレーション（モデル変更がある場合） =====
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# ===== Step 6: 動作確認 =====
curl http://localhost:8000/
# または、ブラウザで http://localhost:8000 にアクセス

# ===== Step 7: ログを確認してエラーがないことを確認 =====
docker compose -f docker-compose.prod.yml logs --tail=50 web
```

### 5.2. 緊急ロールバック

問題が発生した場合、以前のコミットに戻してから再デプロイします。

```bash
# ===== Step 1: 直前のコミットを確認 =====
git log --oneline -5

# ===== Step 2: 問題のないコミットにリセット =====
git checkout <正常だったコミットのハッシュ>

# ===== Step 3: prd を再ビルド =====
docker compose -f docker-compose.prod.yml up -d --build

# ===== Step 4: 動作確認 =====
curl http://localhost:8000/

# ===== Step 5: main ブランチに反映（必要に応じて） =====
git checkout main
git reset --hard <正常だったコミットのハッシュ>
git push --force origin main  # ⚠️ 強制プッシュは慎重に
```

---

## 6. 注意事項

### 6.1. 絶対にやってはいけないこと

| ❌ 禁止事項                                                                | 理由                                           |
| :------------------------------------------------------------------------ | :--------------------------------------------- |
| feature ブランチで `docker compose -f docker-compose.prod.yml up --build` | 未完成のコードが prd に反映される              |
| prd コンテナ内で直接ファイルを編集                                        | コンテナ再起動で消える、バージョン管理外になる |
| dev の DB (`pokeapp_dev_postgres`) を prd と混同                          | テストデータが本番に混入する                   |

### 6.2. デプロイ前チェックリスト

- [ ] `git branch --show-current` で `main` にいることを確認
- [ ] `git status` で未コミットの変更がないことを確認
- [ ] dev 環境で main ブランチの動作確認が完了している
- [ ] DBマイグレーションが必要か確認（`migrations/` ディレクトリの差分）

### 6.3. prd 稼働中に dev で安全に作業できる理由

詳細は [アーキテクチャ設計 (20_architecture.md)](./20_architecture.md) を参照してください。

要点：
- コンテナ名・ポート・ボリュームがすべて分離されている
- prd はビルド時点のコードがイメージ内に固定されており、ホストのコード変更を見ない

---

## 7. トラブルシューティング

### 7.1. コンテナが起動しない

```bash
# ログを確認
docker compose -f docker-compose.prod.yml logs web

# コンテナの状態を確認
docker compose -f docker-compose.prod.yml ps
```

### 7.2. DB接続エラー

```bash
# DB コンテナが起動しているか確認
docker compose -f docker-compose.prod.yml ps db

# DB コンテナのログを確認
docker compose -f docker-compose.prod.yml logs db

# DB コンテナを再起動
docker compose -f docker-compose.prod.yml restart db
```

### 7.3. ポートが既に使用されている

```bash
# 使用中のポートを確認
lsof -i :8000

# 該当プロセスを終了（PID は上記コマンドで確認）
kill -9 <PID>
```

### 7.4. ディスク容量不足

```bash
# 未使用の Docker リソースをクリーンアップ
docker system prune -a

# 未使用ボリュームを削除（⚠️ 使用中のデータは消えない）
docker volume prune
```

### 7.5. マイグレーションエラー

```bash
# マイグレーションの状態を確認
docker compose -f docker-compose.dev.yml exec web python manage.py showmigrations

# 特定のアプリのマイグレーションをリセット（⚠️ データが消える可能性あり）
docker compose -f docker-compose.dev.yml exec web python manage.py migrate <app_name> zero
```
