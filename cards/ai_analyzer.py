"""
AI画像解析モジュール

このモジュールは、YOLO-Worldを使用したカード検出と、
Gemini APIを使用した詳細なカード情報の抽出機能を提供します。
"""

import os
import cv2
import numpy as np
from PIL import Image
import google.generativeai as genai
from ultralytics import YOLO
from django.conf import settings
from datetime import datetime
import json
import logging
from pathlib import Path
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

class CardAnalyzer:
    """カード画像解析クラス"""
    
    # YOLO-World設定 (Notebookの検証結果に基づく)
    YOLO_MODEL_NAME = 'yolov8s-worldv2.pt'
    DETECT_CLASSES = ["one card"]
    CONF_THRESHOLD = 0.014
    IOU_THRESHOLD = 0.1
    MAX_DET = 30
    IMG_SIZE = 640

    # Gemini設定
    GEMINI_MODEL_NAME = 'gemini-2.5-flash' 
    
    GEMINI_PROMPT = """
    # Role
    あなたはポケモンカード（旧裏、新裏、海外版含む全シリーズ）の視覚解析に特化した、精密な画像解析AIスペシャリストです。
    イラストの色彩や画質に惑わされず、カード内に配置された微細な「タイプマーク」を幾何学的な形状から1つも漏らさず特定する能力を持っています。

    # Task
    添付画像は、**赤字のID番号**に従って、ポケモンカードに限らず、長方形の画像要素をgrid形式で並べたものです。
    画像内の**赤字でidが振られた長方形要素**を**必ず左上から右下へ順に**読み取り、以下のデータ定義を用いた【解析プロトコル】に従って構成要素を抽出、JSON形式で出力してください。
    画像品質が悪くても推測して補完してください。
    Markdown記法は一切含めないでください。
    **idは必ず0始まりとしてください**

    # データ定義
    - 全ての項目は必須です。値がない場合は `null` (文字列, 数値) または `[]` (配列)、`false` (真偽値)、を使用してください。
    - `id`: 画像内の**赤字のid**
    - `category`: "pokemon", "trainers", "Other" (ポケモンカード以外の場合)
    - `trainer_type`: "グッズ", "サポート", "スタジアム", "ポケモンのどうぐ" (pokemon/Otherの場合は null)
    - `special_trainers`: `category`が"trainers"でカード色が蛍光ピンクの場合のみ"ACE SPEC"
    - `evolves_from`, `evolution_stage`: Pokemonの進化元・進化段階を表す。カード左上に記載されていることが多い。**画像品質が悪くても推測して補完**すること。
    - `special_features`: Pokemonの特殊分類("ポケモンex", "テラスタル"等)。trainers/Otherの場合は null
    - `hp`, `type`, `move_types`: Pokemonの属性。trainers/Otherの場合は [] (空配列)。同一types, move_typesは一度のみ記載。
    - `weakness`, `resistance`: Pokemonの属性。trainers/Otherの場合は [] (空配列)。カード下部に記載されていることが多い。
    - `retreat_cost`: Pokemonの属性で、にげるためのコストを指す。trainers/Otherの場合は"null"。カード右下に星マークの数として記載される。

    # 【解析プロトコル】
    各IDのカードに対し、以下の順序で思考（Reasoning）を展開してください。

    1. **データ定義の全検出**:
    カードを以下の3つのエリアに分割して注視してください。
    - 【上部】HP付近にある「本体の属性」を特定
    - 【中央】ワザ名の左側にある「行動コスト」を全てリストアップ
    - 【下部】「弱点」「抵抗力」「にげる（撤退コスト）」の各セクションにあるマークを確認。

    2. **形状ベースの識別 (Shape-First Recognition)**:
    背景色に依存せず、円の中の「シンボルの形状」を最優先に判定してください。
    - **草**: 三つ葉のような葉の形
    - **炎**: 上に伸びる揺らめく炎の形（「闘」と混同注意）
    - **水**: 下に膨らむ滴（しずく）の形
    - **雷**: 鋭角な稲妻の形
    - **超**: 中央に丸みのある瞳（目）の形（「悪」と混同注意）
    - **闘**: 突き出した拳（こぶし）の形（「炎」と混同注意）
    - **悪**: 右側が欠けた三日月の形（「超」と混同注意）
    - **鋼**: 六角形（ボルト/ナット）の形（「無色」と混同注意）
    - **妖 (フェアリー)**: 蝶のような、あるいは翼の生えたハートの形
    - **龍 (ドラゴン)**: 爪の跡、あるいは龍の頭部のような複雑な形
    - **無色**: 六芒星（黒い星）の形
    - その他のタイプもポケモンのプロフェッショナルとして漏らさず判定してください。

    3. **コンテキスト分類**:
    - **move_types**: すべてのワザに含まれるエネルギーマークを統合し、重複を除いたユニークなリストを作成してください。
    - **retreat_cost**: 「にげる」エリアにあるエネルギーマークの「総数」を整数でカウントしてください。

    4. **検証 (Self-Correction)**:
    - 弱点や抵抗力の横にある「×2」や「-20」などの数値は無視し、マークの有無と種類のみを確認したか？
    - 非常に小さい「にげる」のエネルギー個数を見落としていないか？

    # Output Format
    JSON配列のみを出力してください。`reasoning`には各エリア（上部・中央・下部）で何を根拠に判断したかを必ず記述してください。

    ## 出力例 (Example)

    [
    {
        "id": 0,
        "category": "pokemon",
        "name": "リザードンex",
        "trainer_type": null,
        "special_trainers": false,
        "evolves_from": "リザード",
        "evolution_stage": "2進化",
        "special_features": ["ポケモンex", "テラスタル"],
        "type": ["悪"],
        "move_types": ["炎", "無色"],
        "weakness": ["草"],
        "resistance": ["水"],
        "retreat_cost": 2,
        "hp": 170,
        "reasoning": "【上部】瞳の形状を確認し『超』と判定。【中央】1段目のワザに瞳1、2段目に瞳1/星1を確認。種類として『超, 無色』を抽出。【下部】左に三日月（悪）、中央に葉（草）、右に星2つを確認。"
    },
    {
        "id": 1,
        "category": "trainers",
        "name": "プライムキャッチャー",
        "trainer_type": "グッズ",
        "is_ace_spec": true,
        "evolves_from": null,
        "evolves_stage": null,
        "special_features": null,
        "type": [],
        "move_types": [],
        "weakness": [],
        "resistance": [],
        "retreat_cost": null,
        "hp": null,
        "reasoning": "【上部】右上にグッズの文字を確認。【中央】蛍光ピンクで全体が縁取られている。【下部】蛍光ピンクで全体が縁取られている。"
    },
    {
        "id": 2,
        "category": "Other",
        "name": null,
        "trainer_type": null,
        "special_trainers": false,
        "evolves_from": null,
        "evolves_stage": null,
        "special_features": null,
        "type": [],
        "move_types": [],
        "weakness": [],
        "resistance": [],
        "retreat_cost": null,
        "hp": null,
        "reasoning": ""
    }
    ]
    """

    def __init__(self):
        """CardAnalyzerクラスの初期化処理"""
        self._setup_yolo()
        self.api_keys = self._load_api_keys()
        # Geminiの初期化はanalyze_image内で動的に行う

    def _setup_yolo(self):
        """YOLOモデルのセットアップ"""
        cache_dir =  os.path.expanduser("~/.cache/ultralytics") 
        custom_model_name = "custom_yolov8s_one_card.pt"
        custom_model_path = os.path.join(cache_dir, custom_model_name)

        try:
            if os.path.exists(custom_model_path):
                logger.info(f"Loading cached custom model: {custom_model_path}")
                self.model = YOLO(custom_model_path)
            else:
                logger.info(f"Creating custom model from {self.YOLO_MODEL_NAME}")
                self.model = YOLO(self.YOLO_MODEL_NAME)
                self.model.set_classes(self.DETECT_CLASSES)
                self.model.save(custom_model_path)
                logger.info(f"Saved custom model to {custom_model_path}")
                
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = YOLO(self.YOLO_MODEL_NAME)
            self.model.set_classes(self.DETECT_CLASSES)

    def _load_api_keys(self) -> list:
        """設定から複数のAPI KEYを読み込む"""
        api_keys = settings.GEMINI_API_KEYS
        if not api_keys:
            raise ValueError("No GEMINI_API_KEYS configured in settings")
        logger.info(f"Loaded {len(api_keys)} Gemini API keys")
        return api_keys

    @transaction.atomic
    def _get_current_api_key(self) -> tuple[str, int]:
        """
        現在使用すべきAPI KEYを取得し、使用回数を管理

        Returns:
            tuple[str, int]: (API KEY文字列, キーインデックス)
        """
        from .models import GeminiApiKeyUsage

        today = timezone.now().date()
        num_keys = len(self.api_keys)

        # 全キーの状態を確認・初期化
        for i in range(num_keys):
            usage, created = GeminiApiKeyUsage.objects.select_for_update().get_or_create(
                key_index=i,
                defaults={'usage_count': 0, 'last_reset_date': today}
            )

            # 日付が変わっていたらリセット
            if usage.last_reset_date < today:
                usage.usage_count = 0
                usage.last_reset_date = today
                usage.save()

        # 使用可能なキーを検索（使用回数が20未満）
        for i in range(num_keys):
            usage = GeminiApiKeyUsage.objects.select_for_update().get(key_index=i)
            if usage.usage_count < 20:
                logger.info(f"Using API key {i + 1}: {usage.usage_count}/20 used today")
                return self.api_keys[i], i

        # 全キーが上限に達している場合
        logger.error("All Gemini API keys have reached daily limit (20 requests each)")
        raise Exception("RESOURCE_EXHAUSTED: All API keys reached daily quota")

    @transaction.atomic
    def _increment_usage(self, key_index: int):
        """使用回数をインクリメント"""
        from .models import GeminiApiKeyUsage

        usage = GeminiApiKeyUsage.objects.select_for_update().get(key_index=key_index)
        usage.usage_count += 1
        usage.save()
        logger.info(f"Incremented API key {key_index + 1} usage: {usage.usage_count}/20")

    def _setup_gemini(self, api_key: str):
        """指定されたAPI KEYでGemini APIクライアントをセットアップ"""
        if not api_key:
            raise ValueError("API key is required for Gemini setup")

        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel(self.GEMINI_MODEL_NAME)

    def analyze_image(self, image_path: str) -> dict:
        """
        画像解析のメインプロセスを実行します。
        成果物は入力画像と同じディレクトリに保存されます。
        """
        # 入力画像のディレクトリを基準とする
        img_path_obj = Path(image_path)
        base_dir = img_path_obj.parent
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 画像読み込み
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
            
        # 2. YOLOによるカード検出
        logger.info(f"Running YOLO inference on {image_path}")
        results = self.model.predict(
            image_path,
            conf=self.CONF_THRESHOLD,
            iou=self.IOU_THRESHOLD,
            imgsz=self.IMG_SIZE,
            max_det=self.MAX_DET,
            save=False, # 自動保存無効
        )
        
        # 検出結果の保存 (detection.jpg)
        plot_img = results[0].plot()
        detection_save_path = base_dir / "detection.jpg"
        cv2.imwrite(str(detection_save_path), plot_img)
        
        # 3. カード画像の切り出し
        cropped_images = []
        detections = results[0].boxes.data.cpu().numpy()
        
        # 座標ソート
        detections = sorted(detections, key=lambda x: (x[1] // 100, x[0]))
        
        # クロップ画像用ディレクトリ (散らばらないようにサブフォルダ推奨だが、今回は直下には置かないでおく)
        # 要望: "timestampフォルダの中に...すべて格納" -> base_dir/crops/crop_xx.jpg とする
        crops_dir = base_dir / "crops"
        crops_dir.mkdir(exist_ok=True)
        
        # MEDIA_URLからの相対パス計算用
        # base_dir は .../media/bulk_register/2024/...
        # settings.MEDIA_ROOT は .../media/
        try:
            relative_base_path = base_dir.relative_to(settings.MEDIA_ROOT)
        except ValueError:
            # 万が一MEDIA_ROOT外ならそのまま使う等の対抗措置（通常はありえない）
            relative_base_path = Path("bulk_register") 

        for i, det in enumerate(detections):
            x1, y1, x2, y2 = map(int, det[:4])
            
            h, w = img.shape[:2]
            margin = 10
            x1 = max(0, x1 - margin)
            y1 = max(0, y1 - margin)
            x2 = min(w, x2 + margin)
            y2 = min(h, y2 + margin)
            
            crop = img[y1:y2, x1:x2]
            
            crop_filename = f"crop_{i:02d}.jpg"
            crop_path = crops_dir / crop_filename
            cv2.imwrite(str(crop_path), crop)
            
            # URL生成: /media/bulk_register/2024/.../crops/crop_xx.jpg
            media_url = f"{settings.MEDIA_URL}{relative_base_path}/crops/{crop_filename}"
            
            cropped_images.append({
                'id': i,
                'path': str(crop_path),
                'image': crop,
                'media_url': media_url
            })
            
        if not cropped_images:
            logger.warning("No cards detected by YOLO")
            return {'error': 'No cards detected', 'count': 0}

        # 4. グリッド画像の作成
        grid_save_path = base_dir / "grid.jpg"
        self._create_grid_image(cropped_images, grid_save_path)

        # 5. Gemini API KEYの取得と初期化
        current_key, key_index = self._get_current_api_key()
        self._setup_gemini(current_key)

        # 6. Geminiへ問い合わせ
        gemini_response = self._query_gemini(str(grid_save_path))

        # 7. 成功したら使用回数をインクリメント
        self._increment_usage(key_index)

        # 8. 生レスポンス保存
        response_log_path = base_dir / "gemini_response.txt"
        with open(response_log_path, 'w', encoding='utf-8') as f:
            f.write(gemini_response)

        return {
            'timestamp': timestamp,
            'card_count': len(cropped_images),
            'cropped_images': cropped_images,
            'grid_image': str(grid_save_path),
            'raw_response': gemini_response
        }

    def _create_grid_image(self, cropped_images: list, save_path: Path) -> Path:
        """
        複数のカード画像を1枚のグリッド画像に結合して保存する
        """
        # 画像サイズを統一
        target_width = 400
        resized_images = []
        
        for item in cropped_images:
            img = item['image']
            h, w = img.shape[:2]
            scale = target_width / w
            new_h = int(h * scale)
            resized = cv2.resize(img, (target_width, new_h))
            
            cv2.putText(
                resized, 
                f"ID: {item['id']}", 
                (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1.0, 
                (0, 0, 255), 
                2
            )
            resized_images.append(resized)
            
        num_images = len(resized_images)
        cols = 4 # 4列固定
        rows = (num_images + cols - 1) // cols
        
        if resized_images:
            max_h = max(img.shape[0] for img in resized_images)
        else:
            max_h = 100 # ダミー
            
        grid_h = rows * max_h
        grid_w = cols * target_width
        
        grid = np.full((grid_h, grid_w, 3), 255, dtype=np.uint8)
        
        for idx, img in enumerate(resized_images):
            r = idx // cols
            c = idx % cols
            
            y_offset = r * max_h
            x_offset = c * target_width
            
            h, w = img.shape[:2]
            grid[y_offset:y_offset+h, x_offset:x_offset+w] = img
            
        cv2.imwrite(str(save_path), grid)
        return save_path

    def _query_gemini(self, image_path: str) -> str:
        """Gemini APIに画像を送信して解析する"""
        try:
            img = Image.open(image_path)
            response = self.gemini_model.generate_content([
                self.GEMINI_PROMPT,
                img
            ])
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            raise
