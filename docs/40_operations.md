# 運用・デプロイ手順書

本ドキュメントでは、開発環境 (dev) と本番環境 (prd) の運用方針、および安全なデプロイ手順を記載します。

- [運用・デプロイ手順書](#運用デプロイ手順書)
  - [1. 環境構成の概要](#1-環境構成の概要)
  - [2. 運用スケジュール例](#2-運用スケジュール例)
  - [3. 基本コマンド一覧](#3-基本コマンド一覧)
    - [3.1. dev 環境](#31-dev-環境)
    - [3.2. prd 環境](#32-prd-環境)
  - [4. 開発ワークフロー](#4-開発ワークフロー)
    - [4.1. Git 運用規則](#41-git-運用規則)
      - [4.1.1. ブランチ命名規則](#411-ブランチ命名規則)
      - [4.1.2. コミットメッセージ規則](#412-コミットメッセージ規則)
      - [4.1.3. プルリクエスト (PR) 運用規則](#413-プルリクエスト-pr-運用規則)
    - [4.2. 日常の開発作業](#42-日常の開発作業)
    - [4.3. main ブランチへのマージ](#43-main-ブランチへのマージ)
    - [4.4. マージ後の動作確認](#44-マージ後の動作確認)
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
  - [8. マスタデータ管理](#8-マスタデータ管理)
    - [8.1. 自動投入の仕組み](#81-自動投入の仕組み)
    - [8.2. 手動でマスタデータを投入する](#82-手動でマスタデータを投入する)
    - [8.3. マスタデータの更新](#83-マスタデータの更新)

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

| タイミング     | 作業内容                                          |
| :------------- | :------------------------------------------------ |
| **日常**       | issue登録、dev 環境で開発、feature ブランチで作業 |
| **機能完成時** | main マージ → dev で動作確認 → prd デプロイ       |
| **週次/月次**  | ログ確認、ディスク使用量確認、不要イメージ削除    |
| **緊急時**     | ロールバック（手順4.2参照）                       |

---

## 3. 基本コマンド一覧

### 3.1. dev 環境

```bash
# ----- 起動・停止 -----

# 再ビルドして起動（Dockerfile や pyproject.toml を変更した場合）
docker compose -f docker-compose.dev.yml up -d --build

# 起動（バックグラウンド）
docker compose -f docker-compose.dev.yml up -d

# 停止
docker compose -f docker-compose.dev.yml down

# 起動（フォアグラウンド、ログ表示）
docker compose -f docker-compose.dev.yml up
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

```bash
# ----- CSS 管理コマンド -----
docker run --rm -v "$(pwd):/app" -w /app node:20-slim /bin/bash -c "npm install && npm run build"
```

### 3.2. prd 環境

```bash
# ----- 起動・停止 -----

# 起動（バックグラウンド推奨）
docker compose -f docker-compose.prd.yml up -d

# 停止
docker compose -f docker-compose.prd.yml down

# 再ビルドして起動（デプロイ時）
docker compose -f docker-compose.prd.yml up -d --build
```

```bash
# ----- ログ確認 -----

# リアルタイムログ
docker compose -f docker-compose.prd.yml logs -f web

# 直近50行のログ
docker compose -f docker-compose.prd.yml logs --tail=50 web
```

```bash
# ----- Django 管理コマンド -----

# DBマイグレーション実行
docker compose -f docker-compose.prd.yml exec web python manage.py migrate

# Django シェル起動
docker compose -f docker-compose.prd.yml exec web python manage.py shell
```

---

## 4. 開発ワークフロー

### 4.1. Git 運用規則

運用・エンハンスフェーズにおける、ブランチ・コミット・プルリクエストの命名規則と運用ルールを定めます。

**基本規則**

- Issueを必ず登録し、Issue駆動開発

表. type一覧
| type        | 用途                                       | 例                             |
| :---------- | :----------------------------------------- | :----------------------------- |
| `feat/`     | 新機能追加                                 | `feat/123-add-user-auth`       |
| `fix/`      | バグ修正                                   | `fix/45-card-image-not-shown`  |
| `refactor/` | リファクタリング                           | `refactor/67-optimize-queries` |
| `docs/`     | ドキュメント更新                           | `docs/89-update-readme`        |
| `test/`     | テストコードの追加・修正                   | `test/12-add-card-model-tests` |
| `chore/`    | 雑務（設定ファイル変更、依存関係更新など） | `chore/34-update-deps`         |


#### 4.1.1. ブランチ命名規則

**フォーマット**: `<type>/<issue番号>-<description>`

**命名ルール**:

- **Issue番号を必ず含める**: GitHub Issues で管理しているタスクと1対1で対応させる
- **説明は英語・ケバブケース**: 簡潔に変更内容を表す（例: `add-login`, `fix-null-error`）
- **全て小文字**: 大文字は使用しない

**例**:

```bash
# Issue #42 「ユーザー認証機能を追加」の場合
git checkout -b feat/42-add-user-authentication

# Issue #15 「カード検索でエラーが発生する」の場合
git checkout -b fix/15-card-search-error
```

#### 4.1.2. コミットメッセージ規則

[Conventional Commits](https://www.conventionalcommits.org/ja/) に準拠した簡易フォーマットを採用します。

**フォーマット**:

```text
<type>: <subject>

[optional body]
```

**ルール**:

- **Typeは必須**: メッセージの先頭に必ず `<type>:` を付ける
- **Subjectは簡潔に**: 50文字以内を目安に、変更内容を明確に記述
- **日本語OK**: 日本語でのSubject記述を許容

**例**:

```text
feat: ユーザー認証機能を追加

JWT認証を使用し、ログイン・ログアウトを実装。
```

```text
fix: カード検索でNullPointerExceptionが発生する問題を修正
```

#### 4.1.3. プルリクエスト (PR) 運用規則

**基本方針**:

- `main` ブランチへの直接コミットは**禁止**
- すべての変更は作業ブランチからのPRを経由する
- マージ方法は **Squash and Merge** を使用する。(merge commit, rebaseは設定で拒否済)

**PRタイトルの命名規則**:

ブランチ名と同様のフォーマットを使用します。自動で末尾にPR番号も付与されます。
※Default commit message = `Pull request title`に設定済み

```text
<type>/<issue番号> <subject>
```

**PRテンプレート**:

本リポジトリでは `.github/PULL_REQUEST_TEMPLATE.md` にテンプレートを用意しています。
PR作成時に自動で記入フォームが表示されるので、各項目を埋めてください。

**Squash and Merge を使用する理由**:

- `main` ブランチのコミット履歴がクリーンに保たれる
- 1つのPR = 1つのコミットとなり、履歴の追跡が容易
- 作業中の細かいコミット（WIP、typo修正など）がまとめられる

---

### 4.2. 日常の開発作業

```bash
# ===== Step 1: 作業ブランチを作成 =====
# ブランチ命名規則: <type>/<issue番号>-<description>
# 例: Issue #42 「ユーザー認証機能を追加」の場合
git checkout main
git pull origin main
git checkout -b feat/42-add-user-authentication

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

# - CSSを明示的に再ビルドしたい場合：
docker run --rm -v "$(pwd):/app" -w /app node:20-slim /bin/bash -c "npm install && npm run build"

# ===== Step 4: 変更をコミット =====
git add .
git commit -m "feat: ユーザー認証機能を追加"

# ===== Step 5: リモートにプッシュ =====
git push origin feat/42-add-user-authentication
```

### 4.3. main ブランチへのマージ

```bash
# Step 1: 作業ブランチをプッシュ（4.2 の Step 5 で完了済み）

# Step 2: GitHub で PR を作成
# - ブラウザで GitHub リポジトリにアクセス
# - 「Compare & pull request」ボタンをクリック
# - PRタイトルは「feat: ユーザー認証機能を追加 (#42)」のように記載
# - テンプレートに従って説明を入力して「Create pull request」
# - 差分を確認して「Squash and merge」→「Confirm squash and merge」

# Step 3: ローカルの main を更新
git checkout main
git pull origin main

# Step 4: 不要になった作業ブランチを削除
git branch -d feat/42-add-user-authentication
```

### 4.4. マージ後の動作確認

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
docker compose -f docker-compose.prd.yml build

# ===== Step 4: コンテナを新イメージに入れ替え =====
docker compose -f docker-compose.prd.yml up -d

# ===== Step 5: DBマイグレーション（モデル変更がある場合） =====
docker compose -f docker-compose.prd.yml exec web python manage.py migrate

# ===== Step 6: 動作確認 =====
curl http://localhost:8000/
# または、ブラウザで http://localhost:8000 にアクセス

# ===== Step 7: ログを確認してエラーがないことを確認 =====
docker compose -f docker-compose.prd.yml logs --tail=50 web
```

### 5.2. 緊急ロールバック

問題が発生した場合、以前のコミットに戻してから再デプロイします。

```bash
# ===== Step 1: 直前のコミットを確認 =====
git log --oneline -5

# ===== Step 2: 問題のないコミットにリセット =====
git checkout <正常だったコミットのハッシュ>

# ===== Step 3: prd を再ビルド =====
docker compose -f docker-compose.prd.yml up -d --build

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

| ❌ 禁止事項                                                               | 理由                                           |
| :----------------------------------------------------------------------- | :--------------------------------------------- |
| feature ブランチで `docker compose -f docker-compose.prd.yml up --build` | 未完成のコードが prd に反映される              |
| prd コンテナ内で直接ファイルを編集                                       | コンテナ再起動で消える、バージョン管理外になる |
| dev の DB (`pokeapp_dev_postgres`) を prd と混同                         | テストデータが本番に混入する                   |

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
docker compose -f docker-compose.prd.yml logs web

# コンテナの状態を確認
docker compose -f docker-compose.prd.yml ps
```

### 7.2. DB接続エラー

```bash
# DB コンテナが起動しているか確認
docker compose -f docker-compose.prd.yml ps db

# DB コンテナのログを確認
docker compose -f docker-compose.prd.yml logs db

# DB コンテナを再起動
docker compose -f docker-compose.prd.yml restart db
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

---

## 8. マスタデータ管理

### 8.1. 自動投入の仕組み

本アプリケーションでは、**コンテナ起動時にマスタデータが自動的に投入**されます。

**対象テーブル**:

| モデル名         | 内容                                   |
| :--------------- | :------------------------------------- |
| `CardCategory`   | カテゴリ（ポケモン、トレーナーズ）     |
| `Type`           | タイプ（草、炎、水など）               |
| `EvolutionStage` | 進化段階（たね、1進化、2進化など）     |
| `SpecialFeature` | 特別（ポケモンex、テラスタルなど）     |
| `MoveType`       | わざのエネルギータイプ                 |
| `TrainerType`    | トレーナーズの種別（グッズ、サポート） |
| `SpecialTrainer` | 特別な分類（ACE SPEC）                 |

**動作フロー** (`entrypoint.sh`):

```text
コンテナ起動
    ↓
DBマイグレーション実行 (python manage.py migrate)
    ↓
マスタデータ投入 (python manage.py seed_master_data)
    ↓
    ├─ データが存在しない → fixtures からデータ投入
    └─ データが既に存在  → スキップ（ログ出力のみ）
    ↓
サーバー起動 (dev: runserver / prd: gunicorn)
```

**ポイント**:

- **冪等性**: 既にデータがある場合はスキップするため、何度実行しても安全
- **自動実行**: `docker compose up` するだけで、マスタデータまで含めた初期セットアップが完了
- **GitHub公開対応**: リポジトリをクローンした人が追加の手順なしでアプリを利用可能

### 8.2. 手動でマスタデータを投入する

コンテナ起動時に自動実行されますが、手動で実行することも可能です。

```bash
# dev 環境
docker compose -f docker-compose.dev.yml exec web python manage.py seed_master_data

# prd 環境
docker compose -f docker-compose.prd.yml exec web python manage.py seed_master_data
```

**出力例（データがない場合）**:

```text
マスタデータを投入中...
Installed 65 object(s) from 1 fixture(s)
✓ マスタデータの投入が完了しました。
```

**出力例（データがある場合）**:

```text
✓ マスタデータは既に存在します（CardCategoryにデータあり）。スキップします。
```

### 8.3. マスタデータの更新

マスタデータを変更した場合、以下の手順で fixtures ファイルを更新します。

```bash
# Step 1: Django Admin などで dev 環境のマスタデータを編集

# Step 2: 現在のマスタデータをエクスポート
docker compose -f docker-compose.dev.yml exec web python manage.py dumpdata \
  cards.CardCategory \
  cards.Type \
  cards.EvolutionStage \
  cards.SpecialFeature \
  cards.MoveType \
  cards.TrainerType \
  cards.SpecialTrainer \
  --indent 2 > cards/fixtures/master_data.json

# Step 3: 変更をコミット
git add cards/fixtures/master_data.json
git commit -m "chore: マスタデータを更新"
```

**注意**: `seed_master_data` コマンドは「データが存在しない場合のみ投入」するため、既存環境でマスタデータを更新したい場合は、Django Admin で直接編集するか、一度テーブルを空にしてから再投入してください。
