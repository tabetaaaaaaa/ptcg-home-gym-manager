# ER図

## 概要

このドキュメントは、ポケモンカード管理アプリケーションのデータベース設計をER図 (Entity-Relationship Diagram) で示します。
ダイアグラムはMermaid形式で記述されています。

## データモデルのポイント

- **カード本体 (`PokemonCard`)**: カードの基本情報（名称、枚数など）と、他のマスタへの参照を持ちます。
- **マスタデータ**:
  - `Type` (タイプ: 炎, 水など)
  - `EvolutionStage` (進化度合い: たね, 1進化など)
  - `SpecialFeature` (特徴: ex, Vなど)
  - `MoveType` (わざの属性: 炎, 水など)
  これらをマスタ化することで、選択肢の一貫性を保ち、将来的な追加・変更を容易にします。
- **多対多の関係**:
  - カードの「タイプ」「特徴」「わざの属性」は複数持つ可能性があるため、それぞれ中間テーブル (`CardType`, `CardSpecialFeature`, `CardMoveType`) を用いて表現します。
- **自己参照**:
  - カードの進化ライン（例: フシギダネ → フシギソウ）は、`PokemonCard` テーブル内の自己参照 `evolves_from_id` によって表現します。

## ER Diagram

```mermaid
erDiagram
    PokemonCard {
        int id PK "ユニークID"
        string name "カード名称"
        int quantity "所持枚数"
        string image_path "画像ファイルパス (任意)"
        text memo "メモ (任意)"
        int evolution_stage_id FK "進化度合いID"
        int evolves_from_id FK "進化元カードID (任意)"
        datetime created_at "作成日時"
        datetime updated_at "更新日時"
    }

    Type {
        int id PK "ユニークID"
        string name UK "属性名 (例: 炎, 水)"
    }

    EvolutionStage {
        int id PK "ユニークID"
        string name UK "進化段階 (例: たね, 1進化)"
    }

    SpecialFeature {
        int id PK "ユニークID"
        string name UK "特徴 (例: ex, V, 古代)"
    }

    MoveType {
        int id PK "ユニークID"
        string name UK "わざの属性名 (例: 炎, 水, 無色)"
    }

    CardType {
        int card_id PK, FK
        int type_id PK, FK
    }

    CardSpecialFeature {
        int card_id PK, FK
        int special_feature_id PK, FK
    }

    CardMoveType {
        int card_id PK, FK
        int move_type_id PK, FK
    }

    PokemonCard ||--o{ PokemonCard : "evolves from"
    PokemonCard }o--|| EvolutionStage : "is"

    PokemonCard ||--|{ CardType : "links to"
    Type ||--|{ CardType : "links to"

    PokemonCard ||--|{ CardSpecialFeature : "links to"
    SpecialFeature ||--|{ CardSpecialFeature : "links to"

    PokemonCard ||--|{ CardMoveType : "links to"
    MoveType ||--|{ CardMoveType : "links to"

```
