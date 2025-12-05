# 遷移図 (HTMX利用)

このドキュメントは、`htmx` を利用して画面遷移なしに操作を完結させる場合の画面フローを定義します。

## 新規登録フロー

一覧画面のボタンクリックからモーダルウィンドウ（ポップアップ）で新規カードを登録し、画面をリロードせずに一覧に反映されるまでの一連の流れです。

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Page as ブラウザ (一覧画面)
    participant Server as サーバー (Django)

    Note over User, Server: ユーザーが一覧画面を閲覧中

    User->>Page: ① 新規登録ボタンをクリック
    Page->>Server: ② フォーム用HTMLをリクエスト (htmx: GET /cards/new/)
    Server-->>Page: ③ フォーム部品のHTMLを返す
    Page->>User: ④ モーダル内にフォームを表示

    User->>Page: ⑤ 情報を入力し、登録ボタンをクリック
    Page->>Server: ⑥ フォームデータを非同期で送信 (htmx: POST /cards/new/)
    
    alt バリデーション成功
        Server->>Server: ⑦-A DBにデータを保存
        Server-->>Page: ⑧-A 新カード1件分のHTMLを返す
        Page->>Page: ⑨-A モーダルを閉じ、一覧の先頭に新カードを追加
        Page->>User: 新しいカードが追加された一覧が表示される
    else バリデーション失敗
        Server-->>Page: ⑦-B エラー情報付きのフォームHTMLを返す
        Page->>Page: ⑧-B モーダル内のフォームをエラー付きのものに差し替え
        Page->>User: ⑨-B エラーメッセージが表示される
    end
```

## 削除フロー

一覧画面の削除ボタンクリックから、確認モーダルを経て、対象のカードが画面上から削除されるまでの一連の流れです。

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Page as ブラウザ (一覧画面)
    participant Server as サーバー (Django)

    Note over User, Server: ユーザーが一覧画面を閲覧中

    User->>Page: ① カードの削除ボタンをクリック
    Page->>Server: ② 削除確認モーダル用のHTMLをリクエスト (htmx: GET /cards/PK/delete/)
    Server-->>Page: ③ 確認モーダル用のHTMLを返す
    Page->>User: ④ 削除確認モーダルを表示

    User->>Page: ⑤ 「はい、削除します」ボタンをクリック
    Page->>Server: ⑥ 削除リクエストを送信 (htmx: DELETE /cards/PK/delete/)
    Server->>Server: ⑦ DBから対象カードを削除
    Server-->>Page: ⑧ HTTP 200 (OK) レスポンスを返す
    
    Page->>Page: ⑨ モーダルを閉じ、一覧から該当カードの要素を削除
    Page->>User: カードが削除された一覧が表示される
```
