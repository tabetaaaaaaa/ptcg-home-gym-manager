<div align="center">
  <img src="docs/logo.svg" alt="P TCG Home Gym Manager" width="100%">
</div>

<br>

<div align="center">
  <a href="https://www.gnu.org/licenses/agpl-3.0">
    <img src="https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=flat-square" alt="License: AGPL v3" />
  </a>
  <img src="https://img.shields.io/github/last-commit/Tabetaaaaaaa/pokeapp?style=flat-square" alt="GitHub last commit" />
  <img src="https://img.shields.io/github/issues/Tabetaaaaaaa/pokeapp?style=flat-square" alt="GitHub issues" />
  <img src="https://img.shields.io/github/repo-size/Tabetaaaaaaa/pokeapp?style=flat-square" alt="GitHub repo size" />
</div>

<br>

<!-- Tech Stack Badges -->
<div align="center">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python" />
  <img src="https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/google%20gemini-8E75B2?style=for-the-badge&logo=google%20gemini&logoColor=white" alt="Google Gemini" />
  <br>
  <img src="https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/daisyui-5A0EF8?style=for-the-badge&logo=daisyui&logoColor=white" alt="DaisyUI" />
  <img src="https://img.shields.io/badge/htmx-%233D72D7.svg?style=for-the-badge&logo=htmx&logoColor=white" alt="htmx" />
  <br>
  <img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/-Raspberry_Pi-C51A4A?style=for-the-badge&logo=Raspberry-Pi&logoColor=white" alt="Raspberry Pi" />
</div>

---

## 📖 概要 (Overview)

> [!INFO]
> **TCGプレイヤーのための在庫管理アプリ**

P TCG Home Gym Manager は、自宅のカード在庫を効率的に管理するためのオープンソースのWebアプリケーションです。
「**持っているはずのカードが見つからない**」「**デッキを組むときに枚数が足りるかわからない**」
といったプレイヤーの悩みを解決するために開発されました。

- **強力な検索機能**: 名前、タイプ、ワザのエネルギータイプなど、詳細な条件で在庫を検索できます。
- **さらに強力な検索機能**: 同一進化ツリー上の在庫確認・公式ウェブサイトへの遷移機能を使い、効率よく在庫/カード情報を把握できます。
- **AI による自動登録**: 写真からカードを検出し、テキスト情報を自動で読み取ります。
- **環境を選ばず動作**: Docker コンテナ化されているため、ローカル PC からサーバーまで、環境を問わず簡単にセットアップして利用できます。

> [!WARNING]
> カードの購入・売却のための機能は持ち合わせていません。今後の開発予定もありません。
> 本アプリは、**プレイヤーのためのアプリ**としてお楽しみください。

### 🎥 デモ (Demo)

<!-- TODO: ここにデモ動画のGIFまたはYouTubeリンクを埋め込んでください -->
<!-- もう少し上でもいいかも -->
<!-- 例: ![Demo Animation](./docs/demo/demo.gif) -->

> [!NOTE]
> デモ動画は準備中です。

## 🏗 システム構成 (Architecture)

本アプリケーションは、Docker Compose を利用して `dev` (開発), `prd` (本番)の2つの環境で動作するように設計されています。

技術スタックはバッジの通りです。

詳細なアーキテクチャ図・技術スタック・などについては、以下のドキュメントを参照してください。

👉 **[アーキテクチャ設計 (docs/20_architecture.md)](docs/20_architecture.md)**

## 🚀 セットアップ手順 (Getting Started)

Docker Desktop がインストールされていることを前提とします。
より詳細な手順やトラブルシューティングは以下のドキュメントを参照してください。

👉 **[運用・デプロイ手順書 (docs/40_operations.md)](docs/40_operations.md)**

### 1. リポジトリのクローン
```bash
git clone https://github.com/Tabetaaaaaaa/pokeapp.git
cd pokeapp
```

### 2. 環境変数の設定
`.env.example` をコピーして `.env.dev` を作成します。
ご自身の適切な環境変数を設定してください。

```bash
cp .env.example .env.dev
```

### 3. アプリケーションの起動 (開発環境)
```bash
docker compose -f docker-compose.dev.yml up -d
```

初回起動時に、自動的にデータベースのマイグレーションとマスタデータの投入が行われます。

### 4. 利用開始

1. **アクセス**: ブラウザで `http://localhost:8001` (dev環境) にアクセスします。
2. **アカウント作成**: ログイン画面から新規ユーザー登録を行います。
3. **カード登録**: 
   * 「新規登録」メニューから手入力で登録
   * または「まとめて登録」メニューから画像をアップロードしてAI解析
4. **検索**: トップページの検索バーから、登録したカードを検索できます。

## 🛣 ロードマップ (Roadmap)

今後の開発予定はIssuesを参照ください。

## 🤝 コントリビュート (Contributing)

バグ報告や機能追加の提案は大歓迎です！
Issuesの作成やプルリクエストを送る前に、以下のガイドラインをご確認ください。

👉 **[CONTRIBUTING.md](CONTRIBUTING.md)**

## 📜 ライセンス (License)

本ソフトウェアは **GNU Affero General Public License v3.0 (AGPL-3.0)** の下で公開されています。

👉 **[LICENSE](LICENSE)**

## 👤 著者 (Author)

**Tabetaaaaaaa**

- GitHub: [@Tabetaaaaaaa](https://github.com/Tabetaaaaaaa)
- Twitter: 
