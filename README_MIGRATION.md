# ポケモンカード管理アプリ 移行ガイド

本ドキュメントでは、本アプリケーションを別のPCに移行する手順、および `git clone` 後のセットアップ方法について解説します。

---

## 1. 事前準備（旧PCでの作業）

データを引き継ぐために、現在のPCで以下のデータをバックアップします。

### ① データベース（カード情報など）の書き出し
ターミナルでアプリのディレクトリに移動し、以下のコマンドを実行します。
```bash
# データベースの内容を backup.sql として保存
docker-compose exec db pg_dump -U pokeapp_user pokeapp_db > backup.sql
```

### ② 画像データ（カード画像）の書き出し
カードに登録した画像を、コンテナ内からローカルフォルダにコピーします。
```bash
docker cp pokeapp-web-1:/app/media ./media_backup
```

---

## 2. 新環境へのセットアップ（新PCでの作業）

### ① 必要なソフトウェアのインストール
- **Docker Desktop**: [公式サイト](https://www.docker.com/products/docker-desktop/)からインストールしてください。
- **Git**: コードをクローンするために必要です。

### ② ソースコードの取得
```bash
# Gitを使ってクローンする場合
git clone <リポジトリのURL>
cd pokeapp
```

### ③ 環境設定ファイルの配置（重要）
`.gitignore` により、`.env` ファイルは共有されません。
- **旧PCからコピーする場合**: 旧PCのプロジェクトルートにある `.env` ファイルを、新PCの同じ場所（`manage.py` がある場所）にコピーします。
- **新規作成する場合**: `.env.example` をコピーして `.env` という名前のファイルを作成し、必要な情報（APIキーなど）を記述します。

### ④ アプリケーションの起動
```bash
# Dockerコンテナの構築と起動
docker-compose up -d --build
```
この時、`node_modules` など必要なパッケージは自動的にコンテナ内で構築されます。

---

## 3. データの復元

### ① データベースの復元
旧PCで作成した `backup.sql` を新PCのプロジェクトルートに置き、以下のコマンドを実行します。
```bash
docker-compose exec -T db psql -U pokeapp_user pokeapp_db < backup.sql
```

### ② 画像データの復元
バックアップした `media_backup` フォルダの中身を、新しい環境のコンテナにコピーします。
```bash
docker cp ./media_backup/. pokeapp-web-1:/app/media
```

---

## 4. 動作確認

ブラウザで `http://localhost:8000` にアクセスし、以下の点を確認してください。
1. カード一覧が表示されているか
2. カード画像が正しく表示されているか
3. 設定（Gemini APIなど）が正しく反映されているか

---

## よくある質問

- **Q: .env ファイルがないとどうなりますか？**
  - A: データベースの接続情報やAPIキーが見つからないため、アプリケーションが起動エラーになります。
- **Q: データの移行なしでアプリだけ動かしたい場合は？**
  - A: 手順2の「④ アプリケーションの起動」まで完了した後、以下のコマンドでデータベースの初期構築を行ってください。
    ```bash
    docker-compose exec web python manage.py migrate
    ```
