
# 実装計画 (ロードマップ)

LAN内アクセスを前提とした、アジャイル的な段階的開発計画です。

## Step 1: 開発環境の基盤構築 (Docker): DONE

- **やること**:
  - `Dockerfile`, `docker-compose.yml`, `requirements.txt` の作成
  - Djangoプロジェクトの作成と初期設定
- **ゴール**: `docker-compose up` コマンドで環境が立ち上がり、ブラウザでDjangoの初期画面が表示されること。

## Step 2: データモデルの設計と実装 (Backend): DONE

- **やること**:
  - `PokemonCard` モデルの定義（名称、属性、進化、枚数など）
  - データベースへのマイグレーション実行
- **ゴール**: データベース内にテーブルが作成され、データ保存の準備が整うこと。

## Step 3: 管理機能とCSV入出力の先行実装 (Admin): DONE

- **やること**:
  - Django管理画面 (Admin) の設定
  - `django-import-export` ライブラリの導入と設定
- **ゴール**: 管理画面からカード情報の登録・編集ができ、CSVでのエクスポート・インポートが動作すること。

## Step 4: 検索・一覧画面の実装 (Frontend - Read)

### 計画詳細化 (DaisyUI 導入)

DaisyUI の導入に伴い、Step4を以下の4フェーズに分けて段階的に実装します。

#### フェーズ1: フロントエンド開発環境の構築: DONE

- **目的**: DaisyUIを利用するためのCSSビルド環境 (Node.js) をDockerコンテナ内に構築し、Djangoプロジェクトと統合します。
- **やること**:
  - `Dockerfile`を更新し、Pythonに加えて`Node.js`と`npm`をインストールする。
  - `package.json`を作成し、`tailwindcss`, `daisyui`, `postcss`などの依存関係を定義する。
  - `tailwind.config.js`を作成し、DaisyUIプラグインの有効化と、監視対象のテンプレートファイルパスを設定する。
  - `docker-compose.yml`を更新し、コンテナ起動時にCSSビルドが実行されるように設定する。
  - Djangoの`settings.py`で、ビルドされたCSSが出力されるディレクトリを静的ファイルパスとして設定する。

#### フェーズ2: 基本レイアウトの作成: DONE

- **目的**: アプリケーション全体の骨格となるベーステンプレートをDaisyUIのコンポーネントで作成します。
- **やること**:
  - `templates/base.html`を作成し、DaisyUIのテーマ (`data-theme`) を設定する。
  - ヘッダー（ナビゲーションバー）、メインコンテンツ、フッターといった基本的なレイアウトをDaisyUIのクラスを用いて実装する。

#### フェーズ3: カード一覧画面の作成 (Read): DONE

- **目的**: データベース上のカード情報を、レスポンシブな一覧画面として表示します。
- **やること**:
  - `cards/views.py`に`CardListView`を作成し、全カードデータを取得するロジックを実装する。
  - `cards/urls.py`と`config/urls.py`で、一覧画面へのURLルーティングを設定する。
  - `cards/templates/cards/card_list.html`を作成し、DaisyUIの`card`コンポーネントと`grid`レイアウトを用いて、カード情報を一覧表示する。
  - フェーズ2で作成したレイアウト確認用の一時ビュー (`temp_base_view`) とURL (`/temp-base/`) を削除する。

#### フェーズ4: 検索・絞り込み機能の実装 (Filter): DONE

- **目的**: `django-filter`を導入し、キーワードや属性によるカードの絞り込み機能を追加します。
- **やること**:
  - `poetry add django-filter`コマンドでライブラリをインストールする。
  - `cards/filters.py`を新規作成し、検索条件を定義する`FilterSet`を実装する。
  - `CardListView`を改修し、GETリクエストに応じたフィルタリング処理を組み込む。
  - 一覧画面に検索フォームを設置し、`input`や`select`といった各部品をDaisyUIのコンポーネントでスタイリングする。

- **ゴール**: DaisyUIによるモダンなデザインのカード一覧画面が表示され、キーワードや属性でカードをフィルタリングできること。

## Step 5: 在庫操作と登録機能の実装 (Frontend - Write)

- **やること**: `htmx` を導入し、画面遷移なしでカードの登録・枚数増減・削除をモーダルや非同期処理で行う。
- **ゴール**: 管理画面に入らずとも、スマホ用画面だけでカードの登録・削除・枚数変更ができ、UXが大幅に向上すること。

### 計画詳細化 (`htmx`導入)

`htmx`の導入に伴い、Step5を以下の4フェーズに分けて段階的に実装します。

#### フェーズ1: `htmx`の環境構築: DONE

- **目的**: `htmx`をプロジェクトに導入し、非同期通信の準備を整えます。
- **やること**:
  - `poetry add django-htmx` を実行し、`django-htmx`をインストールします。
  - `config/settings.py` の `INSTALLED_APPS` に `'django_htmx'` を追加し、`MIDDLEWARE` に `django_htmx.middleware.HtmxMiddleware` を追加します。
  - `templates/base.html` に、`htmx.min.js` を読み込むための `<script>` タグを追加します。

#### フェーズ2: 新規登録機能の実装 (モーダル対応): DONE

- **目的**: モーダルウィンドウ内で完結するカード登録機能を作成します。
- **やること**:
  - `cards/views.py`に、フォームのHTML部品を返却するロジックと、POSTされたデータを保存して新しいカードのHTML部品を返却するロジックを持つビューを作成します。
  - `cards/urls.py`に、上記ビューに対応するURL（例: `/new/`）を定義します。
  - テンプレートの部品化:
    - `templates/cards/_card_form.html` (新規作成): カード登録フォームのみを持つHTML部品テンプレート。
    - `templates/cards/_card_item.html` (新規作成): カード1枚分の表示を担うHTML部品テンプレート。
    - `templates/cards/card_list.html` (修正): 「新規登録」ボタンに `htmx` 属性 (`hx-get`, `hx-target`) を追加し、モーダル内にフォームを呼び出すように設定。モーダル表示用のプレースホルダー `div` を配置。`htmx`が新しいカードを追加するためのターゲットとなる `div` をリストの先頭に配置。

#### フェーズ3: 枚数増減機能の実装 (非同期更新): DONE

- **目的**: 画面をリロードすることなく、カードの枚数を増減させます。
- **やること**:
  - `cards/views.py`に、枚数を更新し、更新後のカード部品 (`_card_item.html`) をHTMLとして返すビューを作成します。
  - `cards/urls.py`に、枚数増減アクション用のURL（例: `/<int:pk>/increase/`）を定義します。
  - テンプレート修正: `templates/cards/_card_item.html` 内の「+」「-」ボタンに `htmx` 属性 (`hx-post`, `hx-target`, `hx-swap`) を追加します。`hx-target` にカード自身のIDを指定し、`hx-swap="outerHTML"` を設定することで、押されたカード全体が新しい内容に置き換わるようにします。

#### フェーズ4: 削除機能の実装 (モーダル対応): DONE

- **目的**: 確認モーダルウィンドウを経て、非同期でカードを削除します。
- **やること**:
  - `cards/views.py`に、削除確認モーダルのHTML部品を返すロジックと、実際の削除処理を行うロジックを持つビューを作成します。削除が成功した場合は、中身が空のHTTPレスポンスを返します。
  - `cards/urls.py`に、上記ビューに対応するURL（例: `/<int:pk>/delete/`）を定義します。
  - テンプレートの部品化:
    - `templates/cards/_card_confirm_delete.html` (新規作成): 削除確認メッセージとボタンのみを持つHTML部品テンプレート。
    - `templates/cards/_card_item.html` (修正): 「削除」ボタンに `htmx` 属性を追加し、クリック時に確認モーダルを呼び出すように設定。削除成功時に `htmx` が要素を消せるよう、カード全体を囲む `div` にユニークなIDを付与します。

#### フェーズ5: 編集機能の実装 (モーダル対応): DONE

- **目的**: 新規登録機能と同様のモーダルウィンドウで、既存のカード情報を編集できるようにする。
- **やること**:
  - `cards/views.py`に、既存のカードデータをフォームにロードしてHTML部品を返却するロジックと、POSTされたデータを保存して更新後のカードのHTML部品を返却するロジックを持つビューを作成する。
  - `cards/urls.py`に、上記ビューに対応するURL（例: `/<int:pk>/edit/`）を定義する。
  - テンプレート修正: `templates/cards/_card_item.html` 内の「編集」ボタンに `htmx` 属性 (`hx-get`, `hx-target`) を追加し、モーダル内にフォームを呼び出すように設定。更新成功時に `htmx` が要素を置き換えられるよう、カード全体を囲む `div` にユニークなIDを付与する。

## Step 6: ソート機能の実装 (Display): DONE

- **目的**: カード一覧画面に、名前、枚数、属性、進化どあい、特徴など、複数の項目で並び替えできるソート機能を追加する。
- **やること**:
  - `django-filter`の`OrderingFilter`を利用して、ソート機能を実装する。
  - `cards/filters.py`の`CardFilter`に`OrderingFilter`を追加し、ソート可能なフィールドを定義する。
  - `CardListView` (`views.py`) がソート順のクエリパラメータを受け取れるようにする。
  - テンプレート (`card_list.html`) に、ソート順を選択するためのUI（例: ドロップダウンメニューやリンク）を設置する。各リンクには、`?o=fieldname`や`?o=-fieldname`（降順）といったクエリパラメータを含める。
- **ゴール**: ユーザーが一覧画面の表示順を自由に変更でき、目的のカードをより効率的に見つけられるようになること。

## Step 7: 画像機能と仕上げ (Optional): DONE

- **やること**:
  - モデルへの画像フィールド追加とアップロード処理の実装
  - 一覧画面への画像表示 (サムネイル)
  - Dockerボリューム設定による画像の永続化確認
- **ゴール**: カードの写真が登録でき、スマホ画面で画像付きのリストが見られること。

## Step 8: LAN内アクセス設定と実機検証 (Network): DONE

- **やること**:
  - Django設定 (`ALLOWED_HOSTS`) の変更
  - PC側のファイアウォール設定確認
  - 家族のスマホからの接続テスト
- **ゴール**: 家族のスマホからアプリにアクセスし、操作できること。

## Step 9: バッジのカスタマイズ機能の実装 (Display): DONE

- **目的**: カード一覧画面に表示されるバッジ（タイプ、特徴など）の色と並び順を、管理画面から動的に設定できるようにする。
- **やること**:
  - `Type`, `EvolutionStage`, `SpecialFeature` モデルに、色クラスを保存する `color_class` フィールドと、表示順を制御する `display_order` フィールドを追加する。
  - データベースのマイグレーションを実行する。
  - 管理画面 (`admin.py`) を修正し、新しいフィールドを編集可能にする。
  - `CardListView` (`views.py`) を修正し、`display_order` に基づいてバッジがソートされるようにクエリを調整する (`Prefetch` の利用)。
  - テンプレート (`card_list.html`) を修正し、バッジの色が `color_class` フィールドの値に基づいて動的に適用されるように変更する。
- **ゴール**: 管理画面で「炎」タイプに「赤系のバッジ」を、「水」タイプに「青系のバッジ」を割り当てるなど、非エンジニアでも直感的に表示をカスタマイズできるようになること。

## Step 10: UI/UXの改善 (Polish): DONE

- **目的**: アプリケーション全体のデザインを見直し、より洗練された使いやすいUI/UXを実現する。
- **やること**:
  - **フォーム部品の装飾**:: DONE
    - 新規登録フォームや検索フォーム内の各部品（チェックボックス、複数選択など）を、DaisyUI公式ドキュメントで紹介されているような、より装飾的で分かりやすいデザインにカスタマイズする。
    - 例えば、チェックボックスをスイッチのような見た目の「トグル（toggle）」コンポーネントに変更するなど、フィールドの種類に応じた最適なUIを検討・適用する。
    - この実現には、`cards/forms.py` や `cards/filters.py` でのウィジェット設定の高度化や、テンプレートファイル (`_card_form.html`など) でのHTML構造の調整が必要となる。
  - **アイコンの導入**:
    - 編集・削除ボタンのテキストをHeroiconsのSVGアイコンに置き換え、必要に応じてDjangoの`include`タグでアイコンをコンポーネント化する。
    - SVGパスの変更に対応できるよう、パッケージのバージョン固定などの工夫を検討する。
  - **画像編集UIの洗練**: 画像をアップロード・編集・削除するフォームのデザインを、Daisy UIベースの洗練されたデザインに変更する。
  - **デザインの調和**: 検索フォームのデザインを、カード表示コンポーネントと調和するよう、角丸や配色を調整する。: DONE
  - **全体テーマの洗練**: アプリケーション全体のカラーテーマやフォントを見直し、一貫性のあるデザインを適用する。: DONE
  - **一覧表示モードの切り替え**: 画像重視のcardタイプではなく、一画面でより多くの情報を確認できるlistタイプの表示にモード切り替えできるようにする。: DONE
  - **ページング&最上部に戻るボタン**: より多くのカードが登録された場合の閲覧性を向上させるため、ページングや、下部までスクロールしたあと最上部の検索欄へワンクリックで戻ることができるようにする。: DONE
- **ゴール**: 機能性だけでなく、見た目にも満足度の高い、直感的に操作できるアプリケーションに仕上げること。

## Step 11: 新規登録フォームの連続登録対応 (UX): DONE

- **目的**: 新規登録フォームで登録ボタンを押下した際、モーダルを閉じずに次のカードを連続して登録できるようにする。
- **やること**:
  - `cards/views.py` の新規登録ビューを修正し、登録成功後にフォームをリセットした状態のHTML部品を返すようにする。
  - `_card_form.html` テンプレートに、登録成功時のフィードバック（例: 「登録しました」というトースト通知）を表示する仕組みを追加する。
  - HTMXの `hx-swap` 属性や `HX-Trigger` レスポンスヘッダーを活用し、リスト部分には新しいカードを追加しつつ、フォーム部分は初期状態に戻すロジックを実装する。
  - 「登録して閉じる」と「登録して続ける」の2つのボタンを用意する必要はない。
- **ゴール**: 複数のカードを一度に登録する際、毎回モーダルを開き直す手間がなくなり、登録作業の効率が大幅に向上すること。

## Step 12: ポケモンカード以外の種別対応 (Data Model): DONE

- **目的**: ポケモンカードだけでなく、トレーナーズカード（道具、サポート、スタジアムなど）も管理できるようにする。
- **やること**:
  1. `PokemonCard` モデルに、カードの種別（ポケモン、道具、サポート、スタジアムなど）を識別するフィールドを追加する。
  2. 種別に応じて、関係性のないフィールド（例: 道具カードには進化段階やタイプが不要）を適切にnull許可するか、種別ごとのモデルを検討する。
  3. 管理画面 (`admin.py`) を更新し、新しいフィールドを編集可能にする。
  4. DaisyUIのtab形式で既存の検索画面とトレーナーズ検索画面を分ける。
     1. 既存の検索画面には一切手を加えないが、ポケモンしか検索されないようにフィルタする。
     2. ヘッダーは2画面統一で、メイン部分をtabで分ける。
     3. フォームでは、ポケモン画面では自動的にCardCategoryにポケモン、トレーナー図画面ではトレーナー図が入るように処理する。
  5. トレーナー図検索画面は、フォーマットは既存検索画面と統一で、検索項目やフォームの入力項目だけが異なるようにする。
- **ゴール**: ポケモンだけでなく、道具やサポートといったトレーナーズカードも同じアプリケーション内で一元管理できるようになること。

## Step 13: 関連サーチ機能の実装 (Usability): DONE

- **目的**: デッキ構築の際、あるカードの進化系統や関連カードを一覧で確認できるようにし、情報収集を効率化する。
- **やること**:
  - **UIの追加**:
    - 一覧画面の各カード（カード形式・テーブル形式）に「関連サーチ」ボタンを追加する。
    - カード形式では、編集/削除ボタンの下に配置する。
    - テーブル形式では、「詳細」ボタンと同じ列に配置する。
  - **モーダルの実装**:
    - 「関連サーチ」ボタンを押すと、関連カード一覧を表示するモーダルが表示される。
    - モーダルは、右上の「×」ボタンまたはモーダル外のクリックで閉じられるようにする。
  - **モーダル内の表示**:
    - 関連カードを「たね」「1進化」「2進化」「V進化」「M進化」などの進化段階 (`EvolutionStage`) ごとにセクション分けして表示する。
    - セクションの表示順序はEvolution Stageテーブルの表示順を用いて制御する。
    - 各セクションはテーブル形式でカード情報を表示する。
    - 該当するカードがないセクションには「ポケモンがいません」と表示する。
  - **検索ロジックの実装**:
    - ユーザー提案のロジック（対象カードのname/evolves_fromで再帰的に検索）は、実装が複雑になり、パフォーマンスの問題も懸念されます。代わりに、以下の改善案を提案します。
    - **改善案**:
      1. **進化の根を探す**: クリックされたカードから `evolves_from` を再帰的にたどり、進化系統の最も根元となる「たねポケモン」の名前 (`root_name`) を特定する。
      2. **進化系統をすべて集める**: `root_name` を起点に、関連する全てのカード名を再帰的にリストアップする。`evolves_from` をたどる際、進化先が複数ある場合（例: イーブイの進化系）でも、それらすべてを網羅的に探索します。
      3. **カードの取得**: リストアップされた名前を持つ `PokemonCard` をすべてデータベースから取得して表示する。
- **ゴール**: ユーザーが任意のカードから、その進化ライン全体をワンクリックで確認できるようになること。

## Step 14: まとめて登録機能の実装 (Bulk Registration): DONE

- **目的**: YOLO-World画像認識を使用して、複数のポケモンカードを一度に登録できる機能を実装する。ユーザーが複数カードの写真をアップロードすると、YOLO-World → OpenCV → Gemini AIで画像解析を行い、解析結果をテーブル形式で表示して編集・一括登録できるようにする。

### 計画詳細化

YOLO-World、OpenCV、Gemini AIを統合した画像解析機能の実装に伴い、Step14を以下の9フェーズに分けて段階的に実装します。

#### フェーズ1: 依存パッケージと環境設定: DONE

- **目的**: 画像解析に必要なライブラリをインストールし、APIキーやモデル永続化、画像・原文保存用のVolume設定を行う。
- **やること**:
  - `pyproject.toml`に以下の3パッケージを追加: `ultralytics` (YOLO-World)、`opencv-python-headless` (画像処理)、`google-generativeai` (Gemini API)
  - `docker-compose exec web poetry add ultralytics opencv-python-headless google-generativeai` を実行し、Dockerコンテナを再ビルドする。
  - `.env`ファイルに`GEMINI_API_KEY=your_api_key_here`を追加する。
  - `config/settings.py`に`GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')`を追加する。
  - `docker-compose.yml`の`web`サービスに以下のvolumeマウントを追加する:
    - `yolo_models:/root/.cache/ultralytics`: YOLO-Worldモデルファイル（初回ダウンロード約20MB）の永続化
    - `bulk_register_data:/app/media/bulk_register`: オリジナル画像、YOLO解析後のグリッド画像、Gemini出力原文の永続保存用（タイムスタンプ付きファイル名で管理）
  - `volumes`セクションに`yolo_models:`と`bulk_register_data:`を追加する。

#### フェーズ2: バリデーションモジュールの実装: DONE

- **目的**: Gemini APIの出力を検証し、不正なデータを除外するモジュールを作成する。
- **やること**:
  - `cards/validation.py`を新規作成し、`GeminiResponseValidator`クラスを実装する。
  - `validate_and_parse_json()`メソッドを実装: Markdownコードブロックを除去し、JSON形式をチェックしてパースする。JSON形式でない場合は、ユーザーに再実行を促すメッセージと共に`ValueError`を投げる。
  - `filter_valid_categories()`メソッドを実装: `category="pokemon"`または`category="trainers"`のみを抽出し、`category="Other"`は除外する。フィルタ後のアイテムリストとクロップ画像パスのリストを返す。

#### フェーズ3: 画像解析モジュールの実装 : DONE

- **目的**: YOLO-World、OpenCV、Gemini AIを統合した画像解析ロジックを実装し、オリジナル画像・YOLO解析結果画像・Gemini出力原文を永続保存する。
- **やること**:
  - `cards/ai_analyzer.py`を新規作成し、`CardAnalyzer`クラスを実装する。PoCのNotebook（`docs/study/画像認識検証/testing_YOLO-World.ipynb`）のロジックを移植する。
  - `__init__()`メソッドでYOLO-WorldモデルとGeminiモデルを初期化する。
  - `analyze_image(image_path, session_key)`メソッドを実装: 画像からカード情報をJSON配列で返す。処理フローは、YOLO検出（カード領域の矩形検出）→ OpenCVでクロップ&個別画像保存（プレビュー表示用）→ グリッド化（Gemini解析用）→ Gemini解析（グリッド画像 → JSON、選択肢をプロンプトに含める）。タイムスタンプ（例: `YYYYMMDD_HHMMSS`）を生成し、ファイル名に含める。
  - `_save_original_image()`メソッドを実装: オリジナル画像を`/app/media/bulk_register/original_{timestamp}_{original_filename}`として永続保存する。
  - `_save_grid_image()`メソッドを実装: YOLO解析直後のグリッド化する前の画像を`/app/media/bulk_register/grid_{timestamp}.jpg`として永続保存する。
  - `_save_gemini_response()`メソッドを実装: Gemini APIの出力原文（JSON文字列）を`/app/media/bulk_register/gemini_response_{timestamp}.json`として永続保存する。タイムスタンプにより、オリジナル画像・グリッド画像・Gemini出力原文を紐づけられるようにする。
  - `_get_choice_options()`メソッドを実装: DBから選択肢（Type, EvolutionStage, SpecialFeature等）を取得してプロンプトに含める文字列を生成する。選択肢部分以外はプロンプトに変更を絶対に加えない。
  - `_create_grid_and_save_crops()`メソッドを実装: クロップ画像を個別保存しつつグリッド画像を作成する。YOLO解析直後のグリッド化する前の画像は`_save_grid_image()`で永続保存する。
  - `_analyze_with_gemini()`メソッドを実装: Gemini APIでカード情報抽出を行う（選択肢をプロンプトに含める）。APIレスポンスの原文は`_save_gemini_response()`で永続保存する。

#### フェーズ4: データマッピングモジュールの実装: DONE

- **目的**: バリデーション済みのGemini出力をDjangoモデル用データに変換するモジュールを作成する。
- **やること**:
  - `cards/data_mapper.py`を新規作成し、`CardDataMapper`クラスを実装する。
  - `map_to_model_data(gemini_item)`クラスメソッドを実装: Gemini出力1件をDjangoモデル保存用辞書に変換する。選択肢モデル（Type, EvolutionStage等）は名前でルックアップする。存在しない場合は、選択肢を作成せず、プレビュー時にその値を表示しユーザーに修正を促す動線を作る。カテゴリ判定（pokemon/trainers）を行う。

#### フェーズ5: ビュー関数の実装: DONE

- **目的**: 画像アップロード、解析、編集、一括登録の各処理を行うビュー関数を実装する。
- **やること**:
  - `cards/views.py`に4つのビュー関数を追加する:
    - `bulk_register_upload`: アップロードモーダル表示（GET）
    - `bulk_register_analyze`: 画像解析実行 → バリデーション → セッション保存 → プレビューテーブル返却（POST）。処理フローは、画像受信・一時保存 → `CardAnalyzer.analyze_image()`実行 → `GeminiResponseValidator`でバリデーション → `category="Other"`を除外 → セッション保存（カードデータ + クロップ画像パス + オリジナル画像パス） → プレビューテーブル返却。エラー時は`ValueError`や`RuntimeError`をキャッチしてアラート表示する。
    - `bulk_register_edit_item(session_key, item_id)`: 個別アイテム編集（GET: フォーム表示、POST: セッション更新）。編集時もDBには保存せず、セッションを更新する。
    - `bulk_register_submit`: セッションからデータ取得 → 一括DB保存 → 画像削除（POST）。DB登録完了直後にクロップ画像（プレビュー表示用の一時画像）のみをトリガー削除する（cron不要）。オリジナル画像、YOLO解析直後のグリッド化する前の画像、Gemini出力原文は名前付きVolume（`bulk_register_data`）に永続保存されており、削除しない。成功時は`HX-Trigger: cardCreated`で既存のリスト更新機構と連携する。一括登録時は部分的な成功を許容し、成功した件数とエラー件数を表示する。
  - `cards/urls.py`に以下のURLを追加する:
    - `path('bulk-register/', bulk_register_upload, name='bulk_register_upload')`
    - `path('bulk-register/analyze/', bulk_register_analyze, name='bulk_register_analyze')`
    - `path('bulk-register/edit/<str:session_key>/<int:item_id>/', bulk_register_edit_item, name='bulk_register_edit_item')`
    - `path('bulk-register/submit/', bulk_register_submit, name='bulk_register_submit')`

#### フェーズ6: アップロードモーダルの実装: DONE

- **目的**: ドラッグ&ドロップ対応の画像アップロードUIを作成する。
- **やること**:
  - `templates/cards/_bulk_register_modal.html`を新規作成する。
  - ドラッグ&ドロップ対応のファイルアップロード機能を実装する。
  - ローディング表示（`htmx-indicator`）を追加する。
  - プレビューエリア（HTMX `hx-target`で動的置換）を配置する。
  - JavaScript処理を実装: ドロップゾーンクリック → ファイル選択ダイアログ、ファイル選択 → 自動送信（`htmx.trigger(form, 'submit')`）、ドラッグ&ドロップ → ファイル設定 → 自動送信。

#### フェーズ7: プレビューテーブルの実装: DONE

- **目的**: 解析結果をテーブル形式で一覧表示し、編集・一括登録できるUIを作成する。
- **やること**:
  - `templates/cards/_bulk_register_preview.html`を新規作成する。
  - 解析結果をテーブル形式で一覧表示する。全てのGemini出力フィールドを表示: 
    - カテゴリごとにセクションを分ける。 `templates/cards/_related_cards_modal.html` を参照。
    - カラムはカテゴリ問わず共通で、クロップ画像、操作ボタン、カード名、進化元、進化段階、タイプ、特別分類、わざタイプ、弱点、トレーナーズ種別、ACE SPEC。
  - 各行の先頭にクロップ画像のサムネイルを表示する。
  - 各行に「編集」ボタンを追加し、既存の編集フォーム（`_card_form.html`）を呼び出すようにHTMX連携を設定する（`hx-get`でモーダル表示）。
  - 下部に「すべて登録」ボタンを追加し、`hx-post`で一括登録実行 → `HX-Trigger: cardCreated, closeModal`を設定する。

#### フェーズ8: ヘッダーボタンの追加: DONE

- **目的**: メイン画面からまとめて登録機能にアクセスできるボタンを追加する。
- **やること**:
  - `templates/base.html`のnavbar-endセクションに「まとめて登録」ボタンを追加する。
  - ボタンに`hx-get="{% url 'cards:bulk_register_upload' %}"`と`hx-target="#dialog-target"`を設定する。

#### フェーズ9: 統合テストと動作確認: DONE

- **目的**: エンドツーエンドのフローが正常に動作することを確認する。
- **やること**:
  - エンドツーエンドフロー確認: 画像アップロード → 解析 → プレビュー表示 → 編集 → 一括登録の一連の流れをテストする。
  - 例外処理動作確認: YOLO未検出、Gemini API失敗、JSON不正、選択肢不一致、DB保存エラーなどの各エラーケースで適切にエラーメッセージが表示されることを確認する。
    - API失敗は確認済み、それ以外は面倒だからいいや
  - 画像削除確認: 一括登録完了後にクロップ画像（プレビュー表示用の一時画像）が正しく削除されることを確認する。オリジナル画像、YOLO解析直後画像、Gemini出力原文がタイムスタンプ付きファイル名で永続保存されていることを確認する。: DONE

- **ゴール**: ユーザーが複数カードの写真をアップロードすると、自動的に画像解析が行われ、解析結果を確認・編集してから一括登録できるようになること。管理画面に入らずとも、スマホ用画面だけで効率的にカードを登録できること。

- **memo**
  - DONE
    - Ohterが表示されている問題の修正: DONE
    - プレビューで技のタイプなど全ての情報が表形式で見れるようにする: DONE
      - タイプのバッジの色問題: DONE
      - 解析が完了しない問題、モーダル閉じちゃう: DONE
    - 永久保存フォルダが変な問題: DONE
      - フォルダが変なだけじゃなくて、gridした結果しかない。その手前のYOLOの出力結果が欲しい
    - プレビューで既存の同名カードを検索できて、どれかと一緒ならそこに枚数足せるようにする。: DONE
    - プレビューで除外したら、もっと除外感出す。一度除外したものも復活できるようにボタンではなくトリガーとかが良いかもしれない。: DONE
    - 各種UIの改善: DONE
    - リロードしないと総件数が出ない件の修正。普通に削除するも、今回の機能で新規登録するも。: DONE
    - 一括登録モーダルが横長すぎる件の解消: DONE
      - 画像をULする前のUIは問題ないので、UL後も中央よせでULエリアと同じ高さになるようにすれば良いのでは
    - もっと名前がクリックできそうな感じにする: DONE
    - ヘッダーボタンの色: DONE
    - アイコンの使用有無: DONE
    - hoverしたらヘルプが出る機能とただの注釈の使い分け: DONE
    - pokeapp_media_dataに保存される写真の名前を`tcg_p_name_cardid`型にする: DONE 
    - cardidって今どうなっているのか確認: ok
      - 連番になっている、将来ユーザーが増えたらそこにユーザーフィールドを追加すれば良いとのこと。医療や金融などスキーマレベル分離が必要な事例以外は、GitHubとかもそうなっている標準構成だと言っている。
    - 弱点と抵抗力も確認できないかPoCした上で、データモデルおよび各種実装に組み込む
      - 弱点, 抵抗力, にげるコスト, hpを組み込み
      - 表示: DONE
      - 検索: DONE
      - 編集: DONE
    - **Gemini APIの料金**: Gemini 2.5 Flash（無料枠）を使用しますが、リクエスト数に制限があります。本番環境では有料プランへの移行を検討してください。
      - APIが無料枠を超過したらAPIKEYを切り替えることができるか？速度は落ちると思う: DONE
      - Projectは10個まで作れるらしいので1日200件までの制約でやるのはありかも、それを超えたら有料枠に移行させるとか？

## Step 15: その他メニュー機能の作成 (Usability): DOING

- **目的**: 公開に向けたその他機能を整備し、より使いやすく改善する。
- **やること**:
  - **一般ユーザー向け機能の開放**（必須）:
    - ヘッダー右上にメニューボタン（例: ハンバーガーメニュー）を配置する。: DONE
    - メニューから「CSVエクスポート」および「CSVインポート」を選択できるようにする。: DONE
  - **CSVデータ移行機能の解放**（必須）:DONE
    - エクスポート機能: DONE
      - 現在の検索・フィルタリング条件を反映したカード一覧をCSVとしてダウンロードできるようにする。
      - CSVのヘッダーを日本語化する（例: "name" → "名前"、"quantity" → "枚数"）。
      - idではなく名称で出力される（例: 「たね」「炎」）
    - インポート機能: DONE
      - ファイルアップロードフォームを提供し、アップロードされたCSVを解析してデータベースに登録・更新する。
      - インポート時、IDの代わりに名称（例: 「たね」「炎」）で関連データを指定できるようにする（ファイル内で参照可能なものも含む）。
    - 追加
      - エクスポート時にワンクッションはさむ: DONE
      - インポート時のモーダルUI回収: DONE
      - 更新日時のソート機能も設ける: DONE
      - インポート・エクスポートを移行機能としてのUIに変更: DONE
      - インポートのボタンの配置を変更: DONE
  - **ログイン機能の実装**(必須)
    - できるだけ簡便なログイン機能を設ける。DjangoやDaisyUIの標準機能を用いる。
    - データモデルを変更し、他人のカード情報へはアクセスできないようにする
    - パスワードリセット機能を設ける。
    - 既存データはシステムユーザーに紐づけることができるよう勧める。
    - プロフィール編集機能を設ける（優先度中）
    - 招待システムを導入する（優先度低）
    - ソーシャルログイン機能を設ける（将来）
    - ユーザーごとに1日あたりの生成AI利用回数上限を設ける
  - **ヘルプ画面の実装**(必須):DONE
    - ナビバーにヘルプボタンを設け、モーダルでヘルプを表示させる。
    - 簡単な機能紹介やカードタイプの閲覧方法を紹介する。
  
  ```md
    ヘルプ

  このアプリケーションは、あなたが所持しているポケモンカードとトレーナーズカードを管理するため
  のツールです。

  1. 基本的な使い方

   * ポケモンカード・トレーナーズカードの一覧表示
       * 画面上部のナビゲーションから、それぞれのカード一覧ページに移動できます。
       * カード画像をクリックすると、詳細情報を確認できます。

  2. カードの検索

   * キーワード検索
       * カード名や説明文に含まれるキーワードでカードを検索できます。
   * 絞り込み検索
       * レアリティ、タイプ、HPなど、より詳細な条件を指定してカードを絞り込むことができます。
   * 関連カードの表示
       * 特定のポケモンカードの詳細画面から、進化元や進化先、または関連するサポートカードなど、
         関連性の高いカードを一覧で確認できます。

  3. カードの登録

  このアプリでは、3つの方法でカードを登録できます。

   * 個別登録
       * 1枚ずつカード情報を手動で入力して登録します。
   * CSVインポート
       * 指定されたフォーマットのCSVファイルをアップロードすることで、複数枚のカードを一度に登
         録できます。
   * 画像から一括登録
       * カードの画像をアップロードすると、AIがカード情報を自動で読み取り、一括で登録できます。

  4. カードの編集と削除
   * 個別編集・削除
       * カード詳細画面から、情報を編集したり、カードを削除したりできます。
   * 一括編集
       * 一覧画面で複数のカードを選択し、枚数などの情報をまとめて更新できます。
  ```

  - **ユーザビリティ向上**:(今後開発)
    - CSVインポート機能に関するヘルプ画面を設ける（優先度: 中）。
    - インポート用のCSVフォーマット例（サンプルデータ入り）をダウンロードできる機能を設ける（優先度: 低/現在はデータ移行用の機能として想定しているのでExportしたものをImportするだけの想定）。
- **ゴール**: データ移行・ユーザー別データ保持を可能にし、本番化に耐えうる機能群を提供する。

## Step 16: Google Cloud デプロイと本番移行 (Deployment)

- **目的**: Google Cloud Free Tier (無料枠) を最大限活用し、ランニングコストをかけずに本番環境を運用する。
- **アーキテクチャ方針**: GCE (e2-micro, us-central1) 単独インスタンス上に Docker Compose で全サービスを展開する。メモリ制約 (1GB) 対策としてSwap領域の活用を必須とする。

### 計画詳細化 (e2-micro構成)

#### Phase 1: アーキテクチャ設計とドキュメント化 (Design)
- **やること**:
  - アーキテクチャ図・ADRの作成
    - Mermaid記法でアーキテクチャ図（GCE, Docker構成, Volume, Network）を作成する。
  - リソース計画策定
    - 30GBディスクの配分、Swap領域サイズ(4GB推奨)、各コンテナのメモリ制限値を定義する。

#### Phase 2: Google Cloud インフラ構築 (Infrastructure)
- **やること**:
  - GCPプロジェクト作成と課金有効化（無料枠利用のため）。
  - **予算アラートの作成**: 課金額が1円でも発生したら通知が届くよう設定し、意図せぬ請求を防ぐ（**必須**）。
  - VMインスタンス (e2-micro, us-central1) の作成。OSはUbuntu 22.04 LTSを選択予定。
  - 静的IPアドレスの予約と割り当て。
  - ファイアウォール設定: HTTP(80), HTTPS(443), SSH(22) の許可。
  - **OSセットアップ**:
    - Swap領域 (4GB) の作成と永続化設定（**最重要**）。
    - Git, Docker, Docker Compose のインストール。

#### Phase 3: アプリケーションの本番対応 (App Update)
- **やること**:
  - **ハイブリッド静的ファイル配信構成**:
    - `whitenoise`: CSSなど軽量なファイル配信を担当し、構成を簡素化する。
    - **Nginxコンテナの追加**: 画像ファイル (`/media/`) の高速配信を担当させる。
  - **Dockerfileの修正**: 本番用のCSSビルドコマンド (`npm run build`, `python manage.py tailwind build`) を追加し、デザイン崩れを防ぐ。
  - **セッション設定の修正**: `settings.py` の `SESSION_ENGINE` を `django.contrib.sessions.backends.db` に変更し、Gunicorn対応とする。
  - **セキュリティ設定**:
    - `CSRF_TRUSTED_ORIGINS` にGCEの固定IPアドレスを追加する。
    - HTTPS強制 (`SECURE_SSL_REDIRECT`) は **OFF** とし、HTTP運用を可能にする。
  - `gunicorn` を導入し、本番用の起動コマンド (`docker-compose.prod.yml` 等) を用意する。

#### Phase 4: データ移行 (Migration)
- **やること**:
  - `.env` ファイルのセキュアな転送（生成済みのSECRET_KEYやパスワードを含む）。
  - **データベース移行**: ローカルで `pg_dump` を取得し、SCPでVMへ転送後、`psql` でリストアする手順を確立する。
  - **メディアファイル移行**: `media/` フォルダをアーカイブして転送し、VM上のDocker Volumeマウント先へ展開する。
  - **AIモデル移行**: `yolov8s-worldv2.pt` などの大容量ファイルをVMへ配置する。

#### Phase 5: 公開に向けた包括的リスク評価 (Risk Assessment)
- **やること**:
  - **セキュリティリスク**: 認証突破、DDoS、個人情報漏洩の可能性に加え、HTTP運用による盗聴リスク、Django Admin画面への攻撃リスクなどを洗い出す。
  - **性能・可用性リスク**: e2-micro (1GBメモリ) での限界（同時接続数やAI処理時のレイテンシ）、単一障害点 (SPOF) となるGCE構成のリスク評価。
  - **構成・運用リスク**: ドメイン未取得によるHTTPS化断念の影響、Nginxハイブリッド構成の限界（完全分離への移行要否）、バックアップ運用の実効性など、LAN内前提で妥協したポイントを再評価する。
  - **対応策の策定**: 各リスクに対し、「許容する」「運用でカバーする」「追加コストを払って解決する（Cloud Armor, Cloud SQL, Load Balancer導入等）」のいずれを選択するか、コスト試算と共に決定する。

#### Phase 6: デプロイとCI/CD構築 (Automation)
- **やること**:
  - GitHub Actions ワークフロー (`.github/workflows/deploy.yml`) の作成。
  - SSH Key を GitHub Secrets に登録し、PushトリガーでVM上の `git pull` と `docker-compose up -d --build` を実行させる。
  - 初回デプロイと動作確認（ブラウザアクセス、YOLO解析動作、DB接続確認）。

- **ゴール**: 独自のURL（IPアドレスまたはドメイン）でアクセスでき、これまでの開発データが引き継がれた状態で、家族がいつでも使える状態になること。

## Step 17: インフラのコード化 (IaC - Terraform)

- **目的**: 手動構築したGCPインフラをTerraformでコード化し、構成管理の自動化と学習を行う。
- **方針**: Step 16で構築した既存リソースをTerraformに取り込み（Import）、コードと実際の状態を整合させる「リバースエンジニアリング」アプローチをとる。

### 計画詳細化

#### Phase 1: Terraform環境構築とBackend設定
- **やること**:
  - ローカル環境へのTerraformインストール。
  - `terraform` ディレクトリの作成と基本ファイル (`provider.tf`) の作成。
  - Stateファイル管理用のGCSバケット作成（手動）とBackend設定（チーム開発を見据えたtfstate管理のベストプラクティス学習）。

#### Phase 2: 既存リソースのImport
- **やること**:
  - `terraform import` コマンドを使用し、Step 16で作成した重要リソースを管理下に入れる。
    - compute_instance (GCE)
    - compute_address (Static IP)
    - compute_firewall (Firewall Rules)
  - `import` ブロックを使用した宣言的なインポート手法を実践する。

#### Phase 3: コードの整理と検証
- **やること**:
  - ハードコーディングされた値を変数化 (`variables.tf`) する。
  - 差分確認: `terraform plan` を実行し、"No changes" となるまでコードを修正する。
  - 安全な変更（例: ラベル追加）をコードで行い、`terraform apply` で反映されることを確認する。

- **ゴール**: インフラ構成がコードとして管理され、GUIコンソールを使わずに設定変更が可能になっていること。Terraformの基本操作を習得していること。

## Step 18: お気に入りフラグ機能の実装 (Grouping)

- **目的**: デッキ構築やユーザーごとのグルーピングに活用できる、カスタマイズ可能なマーカー機能を提供する。
- **やること**:
  - `FavoriteFlag` モデルを新規作成し、フラグ番号（1～5）、名称、色クラス、表示順などのフィールドを定義する。
  - `PokemonCard` モデルに、`FavoriteFlag` への ManyToMany リレーションを追加する。
  - データベースのマイグレーションを実行する。
  - 管理画面 (`admin.py`) に `FavoriteFlag` を登録する。
  - メイン画面でのフラグ設定機能を実装する:
    - ナビゲーションバーに「設定」リンクまたはアイコンを追加する。
    - `cards/views.py` に、フラグ設定画面を表示するビューと、設定を保存するビューを作成する。
    - `cards/urls.py` に、設定画面用のURL（例: `/settings/flags/`）を定義する。
    - 設定画面用のテンプレート（例: `flag_settings.html`）を作成し、5つのフラグの名称と色を編集できるフォームを提供する。
    - HTMXを活用し、フォーム送信後に非同期で保存し、成功メッセージを表示する。
  - フォーム (`cards/forms.py`) を修正し、カード登録・編集時にお気に入りフラグを選択できるようにする。
  - フィルタ (`cards/filters.py`) を修正し、お気に入りフラグによる絞り込み機能を追加する。
  - テンプレート (`_card_item.html`, `_card_form.html`) を修正し、お気に入りフラグをバッジとして表示する。
  - 一覧画面で、お気に入りフラグのオン/オフを非同期で切り替えられるUI（例: クリックでトグル）を検討する。
- **ゴール**: ユーザーが管理画面にアクセスせず、メイン画面の設定ページから自由に名称を設定できる5つのフラグを使って、デッキ構築や用途別のカード管理が効率的に行えるようになること。

### 運用開始後の追加実装における留意点調査

本セクションでは、Step13完了後に家庭内運用を開始し、データ登録が進んだ状態でStep16を実装する際の懸念事項を、MECE（Mutually Exclusive, Collectively Exhaustive）に整理します。

#### A. データ整合性への影響: **影響なし ✅**

**懸念:** 新しいフィールド追加時に既存レコードが破損するのでは？

**調査結果:**
- ManyToManyフィールド（`favorite_flags`）の追加は、`blank=True` で定義すれば既存データに**影響ゼロ**
- 既存の `types`, `special_features`, `move_types` 等と同じパターンで実装されており、過去のマイグレーション（0011: `CardCategory`追加時）でも問題なし
- 中間テーブル（例: `cards_pokemoncard_favorite_flags`）が自動生成されるが、既存データは何も変更されない

#### B. デフォルト値の強制設定: **該当なし ✅**

**懸念:** 全カードに自動的に何らかのフラグが立つのでは？

**調査結果:**
- ManyToManyリレーションは「関連なし」がデフォルト状態
- BooleanField方式（`is_favorite = models.BooleanField(default=False)`）の場合でも、`False`（未選択）が初期値で問題なし
- **ユーザーが明示的に設定するまで、フラグは立たない**

#### C. 既存データの参照破壊: **影響なし ✅**

**懸念:** ForeignKeyやManyToManyの追加で、既存の関連データが壊れるのでは？

**調査結果:**
- 新しいテーブル（`FavoriteFlag`）と中間テーブルが追加されるだけ
- 既存の `PokemonCard.types`, `PokemonCard.special_features` などは**完全に独立**して動作継続
- クエリ最適化パターン（`prefetch_related`）に `'favorite_flags'` を追加するだけで対応可能

#### D. クエリ性能への影響: **影響軽微 ⚠️**

**懸念:** 新しいManyToManyリレーションでN+1問題が発生するのでは？

**調査結果:**
- `prefetch_related('favorite_flags')` を追加すれば、既存の最適化パターンと同等
- 現在の実装に1行追加するだけで対応可能:

```python
PokemonCard.objects.select_related(
    'evolution_stage', 'trainer_type', 'category'
).prefetch_related(
    'types', 'special_features', 'move_types', 'special_trainers',
    'favorite_flags'  # ← 追加
)
```

**注意点:** フラグでのフィルタリングが頻繁に行われる場合、中間テーブルにインデックスが必要になる可能性あり（Django自動生成で通常は問題なし）

#### E. マイグレーション失敗のリスク: **低リスク ✅**

**懸念:** 何百件データがある状態でマイグレーションが失敗するのでは？

**調査結果:**
- 過去のマイグレーション履歴（特に0011: `CardCategory`追加時）で、同様の追加が成功している
- ManyToManyフィールドの追加は**非破壊的操作**（既存テーブルの変更なし）
- マイグレーション0011の実績例:

```python
migrations.AddField(
    model_name='pokemoncard',
    name='category',
    field=models.ForeignKey(default=1, ...)
)
```

**推奨対策:** マイグレーション前に必ずバックアップ

```bash
docker-compose exec db pg_dump -U pokeapp_user pokeapp_db > backup.sql
```

#### F. UI/UX一貫性の維持: **実装次第 ⚠️**

**懸念:** 既存の表示レイアウトが崩れるのでは？

**調査結果:**
- テンプレートファイル（`_card_item.html`, `_card_form.html`）の修正が必要
- 既存のバッジ表示パターン（types, special_features）と同じスタイルで実装すれば違和感なし

**推奨実装:**

```html
<!-- 既存パターン (special_features) -->
{% for feature in card.special_features.all %}
  <div class="badge badge-secondary badge-sm">{{ feature.name }}</div>
{% endfor %}

<!-- 新規実装 (favorite_flags) -->
{% for flag in card.favorite_flags.all %}
  <div class="badge badge-accent badge-sm">{{ flag.name }}</div>
{% endfor %}
```

**注意点:** 5つのフラグを全て表示する場合、画面の横幅に注意が必要

#### G. フィルタリング機能の整合性: **実装次第 ⚠️**

**懸念:** 既存の検索/フィルタ機能と干渉するのでは？

**調査結果:**
- `cards/filters.py` の `PokemonCardFilter` に追加するだけで対応可能
- 既存パターン:

```python
types = django_filters.ModelMultipleChoiceFilter(
    queryset=Type.objects.all(),
    widget=forms.CheckboxSelectMultiple
)
```

- Step16実装後:

```python
favorite_flags = django_filters.ModelMultipleChoiceFilter(
    queryset=FavoriteFlag.objects.all(),
    widget=forms.CheckboxSelectMultiple
)
```

**注意点:** フィルタUIが縦長になる場合、アコーディオンやタブ分割を検討

#### H. 管理画面の互換性: **影響なし ✅**

**懸念:** Django Admin画面で既存データが操作できなくなるのでは？

**調査結果:**
- `cards/admin.py` に `FavoriteFlagAdmin` を追加
- 既存の `PokemonCardAdmin` に `filter_horizontal = ('favorite_flags',)` を追加するだけで対応可能

```python
class PokemonCardAdmin(admin.ModelAdmin):
    filter_horizontal = ('types', 'special_features', 'move_types',
                        'special_trainers', 'favorite_flags')  # ← 追加
```

#### I. CSV入出力機能への影響: **実装調整必要 ⚠️**

**懸念:** Step15のCSV入出力機能に影響するのでは？

**調査結果:**
- ManyToManyフィールドはCSVでの表現方法を検討する必要あり
- `django-import-export` を使用している場合、`widgets.ManyToManyWidget` で対応可能

**推奨実装:**

```python
from import_export import resources, fields, widgets

class PokemonCardResource(resources.ModelResource):
    favorite_flags = fields.Field(
        column_name='フラグ',
        attribute='favorite_flags',
        widget=widgets.ManyToManyWidget(FavoriteFlag, field='name', separator='|')
    )
```

**CSV例:**

```csv
名前,枚数,フラグ
ピカチュウ,3,デッキA|お気に入り
リザードン,1,デッキB
```

#### J. HTMX動作の互換性: **実装次第 ⚠️**

**懸念:** モーダル内でのフラグ設定がうまく動作しないのでは？

**調査結果:**
- 既存のHTMX実装パターン（枚数増減、編集モーダル）と同じ方式で対応可能
- フラグのオン/オフ切り替えを非同期で実装する場合、新しいビュー追加が必要

**推奨実装案:**

```python
# views.py
def toggle_favorite_flag(request, pk, flag_id):
    card = get_object_or_404(PokemonCard, pk=pk)
    flag = get_object_or_404(FavoriteFlag, pk=flag_id)

    if flag in card.favorite_flags.all():
        card.favorite_flags.remove(flag)
    else:
        card.favorite_flags.add(flag)

    # 更新後のカードHTMLを返す
    return render(request, 'cards/_card_item.html', {'card': card})
```

#### 総合リスク評価マトリクス

| 懸念カテゴリ            | リスク度 | 対策必要度 | 備考                             |
| ----------------------- | -------- | ---------- | -------------------------------- |
| A. データ整合性         | ⭐☆☆      | 不要       | ManyToMany追加は非破壊的         |
| B. デフォルト値強制     | ⭐☆☆      | 不要       | blank=Trueで関連なし状態が初期値 |
| C. 参照破壊             | ⭐☆☆      | 不要       | 独立したテーブル追加のみ         |
| D. クエリ性能           | ⭐⭐☆      | 低         | prefetch_related追加で対応       |
| E. マイグレーション失敗 | ⭐☆☆      | 低         | バックアップ推奨                 |
| F. UI/UX一貫性          | ⭐⭐☆      | 中         | 既存パターン踏襲が重要           |
| G. フィルタ整合性       | ⭐⭐☆      | 低         | 既存パターンで実装可能           |
| H. 管理画面互換性       | ⭐☆☆      | 不要       | filter_horizontal追加のみ        |
| I. CSV入出力            | ⭐⭐⭐      | 中～高     | ManyToManyWidget設定必要         |
| J. HTMX動作             | ⭐⭐☆      | 中         | 新ビュー追加が必要               |

**全体評価: 低～中リスク** （既存データ保護は確実、UI実装に注意が必要）

#### 推奨実装順序

**フェーズ1: 基盤構築（既存データ保護重視）**

1. `FavoriteFlag` モデル作成
2. マイグレーション実行（**バックアップ必須**）
3. 管理画面で5つのフラグを手動登録（デッキA～E等）

**フェーズ2: UI統合（段階的リリース）**

4. フォーム（`_card_form.html`）にチェックボックス追加
5. カード表示（`_card_item.html`）にバッジ表示追加
6. フィルタ（`filters.py`）にフラグ絞り込み追加

**フェーズ3: 高度な機能（オプション）**

7. HTMXによるフラグトグル機能
8. CSV入出力対応（Step15実装時に同時対応推奨）
9. 設定画面でのフラグ名/色カスタマイズ

#### 結論

**安心してStep16を実装して問題ありません。** 主な理由：

1. **データ上書きなし**: ManyToManyフィールド追加は既存レコードに影響しない
2. **自動フラグ設定なし**: ユーザーが明示的に設定するまでフラグは立たない
3. **マイグレーション実績**: 同様のパターンで過去に成功している（0011: CardCategory追加時）
4. **段階的実装可能**: 基盤→UI→高度機能の順で、リスクを分散できる

**唯一の必須対策:** マイグレーション前のデータベースバックアップ

```bash
docker-compose exec db pg_dump -U pokeapp_user pokeapp_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Step 19: 接続URL固定 (Network)

- **目的**: サーバーPCのIPアドレスが変動しても、毎回URLを打ち直すことなく、固定されたURLでアプリケーションにアクセスできるようにする。
- **やること**: 以下のいずれかの方式を比較検討し選択する。
  - ルーターのDHCP設定によるIPアドレス固定を検討する。
  - mDNS (Multicast DNS) を利用した `.local` ドメインでのアクセスを検討する。
  - (上級者向け) プライベートDNSサーバーの構築を検討する。
- **ゴール**: ユーザーが、固定された名前やIPアドレスで、より便利にアプリケーションにアクセスできるようになること。

## その他メモ: DOING

- ユーザー情報の編集
- カード統計情報の表示
- 生成AIによるデッキ提案機能の追加
- 名前から公式情報を検索できるようにする: DONE
