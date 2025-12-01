# アーキテクチャ設計

## 1\. システムアーキテクチャ図

家庭内LANを経由して、Dockerコンテナ内のDjangoアプリへアクセスする経路と、データの永続化（保存）の流れを示しています。

```mermaid
graph TD
    %% スタイル定義
    classDef device fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef network fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef docker fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,stroke-dasharray: 5 5;
    classDef container fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px;
    classDef storage fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;

    subgraph UserSpace ["利用ユーザー (User Space)"]
        Smartphone["📱 家族のスマホ<br>他PC"]:::device
        HostBrowser["💻 あなたのPC<br>(ブラウザ)"]:::device
    end

    subgraph Network ["ネットワーク (Network)"]
        Router(("Wi-Fiルーター")):::network
    end

    subgraph HostPC ["ホストPC / サーバー (Your PC)"]
        Firewall["🛡️ OSファイアウォール"]:::network
        
        subgraph DockerEnv ["Docker Compose環境"]
            WebContainer["🐍 Webコンテナ<br>(Django App)"]:::container
            DBContainer["🐘 DBコンテナ<br>(PostgreSQL)"]:::container
        end

        subgraph Volumes ["データ永続化 (Volume)"]
            MediaVol[("🖼️ Media Volume<br>画像ファイル")]:::storage
            DBVol[("🗄️ DB Volume<br>カードデータ")]:::storage
        end
    end

    %% 通信フロー
    Smartphone -->|"HTTPアクセス<br>http://192.168.x.x:8000"| Router
    Router -->|LAN内通信| Firewall
    Firewall -->|ポート8000許可| WebContainer
    HostBrowser -->|localhost:8000| WebContainer

    %% データアクセスフロー
    WebContainer <-->|"SQLクエリ<br>(ポート5432)"| DBContainer
    WebContainer <-->|画像 保存/読込| MediaVol
    DBContainer <-->|データ 書き込み| DBVol

    %% クラス適用 (IDを使用)
    class DockerEnv docker
```

### 図のポイント

1. **外部からの入り口**: 家族のスマホからはWi-Fiルーターを経由し、あなたのPCのIPアドレス（例: 192.168.x.x）を叩くことでWebコンテナに到達します。
2. **データ永続化**: コンテナを削除してもデータが消えないよう、右下の「Volume」部分でホストPC（あなたのPC）のフォルダと同期させます。
3. **コンテナ間通信**: WebコンテナとDBコンテナはDocker内部のネットワークで直接通信します（外部には露出しません）。

-----

## 2\. 技術スタック一覧

今回の開発で使用する技術と、開発・運用において「何を知っておくべきか（学習・準備ポイント）」をまとめました。

| カテゴリ | 技術・ツール | バージョン (目安) | 用途 | 準備・学習ポイント |
| :--- | :--- | :--- | :--- | :--- |
| **インフラ** | **Docker / Compose** | - | アプリとDBの実行環境構築 | ・`docker-compose.yml` の基本構文<br>・Volume（データ永続化）の仕組み<br>・ポートフォワーディングの設定 |
| **言語** | **Python** | 3.11系 | バックエンド処理全般 | ・基本的な構文 (リスト内包表記など)<br>・仮想環境 (venv) の概念 ※Docker内では不要だが知識として |
| **フレームワーク** | **Django** | 5.0系 | Webアプリの骨格、管理画面 | ・**Model (DB定義)** の書き方<br>・**Admin (管理画面)** のカスタマイズ方法<br>・Template (HTML) タグの使い方 |
| **データベース** | **PostgreSQL** | 16系 | データの保存 | ・基本的にはDjangoが隠蔽するため深い知識は不要<br>・`pg_dump` などのバックアップ方法 (将来用) |
| **フロントエンド** | **Bootstrap** | 5.3 | 画面デザイン (CSS) | ・グリッドシステム (スマホ/PCの表示切替)<br>・主要クラス (`btn`, `card`, `form-control` 等) の使い方 |
| **ライブラリ** | **django-import-export** | 最新 | CSVの入出力機能 | ・管理画面への組み込み方<br>・Resourceクラスの定義方法 |
| **ライブラリ** | **django-filter** | 最新 | 検索・絞り込み機能 | ・FilterSetクラスの定義方法<br>・HTML側でのフォーム表示方法 |
| **ライブラリ** | **Pillow** | 最新 | 画像処理 | ・Djangoで画像 (`ImageField`) を扱うために必須<br>・特別な学習は不要 (インストールのみ) |
