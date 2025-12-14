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

logger = logging.getLogger(__name__)

class CardAnalyzer:
    """カード画像解析クラス"""
    
    # YOLO-World設定 (Notebookの検証結果に基づく)
    # ユーザー検証環境: testing_YOLO-World.ipynb
    YOLO_MODEL_NAME = 'yolov8s-worldv2.pt'
    DETECT_CLASSES = ["one card"]
    CONF_THRESHOLD = 0.01  # 低めに設定して取り漏らしを防ぐ
    IOU_THRESHOLD = 0.1    # 重複検出を防ぐため厳しめに設定
    MAX_DET = 30           # 20枚制限だが余裕を持たせる
    IMG_SIZE = 640

    # Gemini設定
    GEMINI_MODEL_NAME = 'gemini-2.0-flash-exp' # 実装計画に基づく
    
    # Geminiへのシステムプロンプト
    GEMINI_PROMPT = """
    あなたはポケモンカードの専門家です。
    画像内の要素を左上から順に読み取り、以下のJSON配列形式のみを出力してください。
    画像品質が悪くても推測して補完し、Markdown記法は一切含めないでください。

    # データ定義
    - 全ての項目は必須です。値がない場合は `null` (文字列) または `[]` (配列)、`false` (真偽値) を使用してください。
    - `category`: "pokemon", "trainers", "Other" (カード以外の場合)
    - `trainer_type`: "グッズ", "サポート", "スタジアム", "ポケモンのどうぐ" (pokemon/Otherの場合は null)
    - `special_trainers`: ACE SPECカードの場合のみ "ACE SPEC"
    - `special_features`: Pokemonの特殊分類("ポケモンex", "テラスタル"等)。trainers/Otherの場合は null
    - `type`, `move_types`, `weakness`: Pokemonの属性。trainers/Otherの場合は [] (空配列)。同一タイプは一度のみ記載。

    # 出力例
    [
    {
        "id": 1,
        "category": "pokemon",
        "name": "リザードンex",
        "trainer_type": null,
        "special_trainers": false,
        "evolves_from": "リザード",
        "evolution_stage": "2進化",
        "special_features": ["ポケモンex", "テラスタル"],
        "type": ["悪"],
        "move_types": ["炎", "無色"],
        "weakness": ["草"]
    },
    {
        "id": 2,
        "category": "trainers",
        "name": "プライムキャッチャー",
        "trainer_type": "グッズ",
        "is_ace_spec": true,
        "evolves_from": null,
        "evolves_stage": null,
        "special_features": null,
        "type": [],
        "move_types": [],
        "weakness": []
    },
    {
        "id": 3,
        "category": "Other",
        "name": null,
        "trainer_type": null,
        "special_trainers": false,
        "evolves_from": null,
        "evolves_stage": null,
        "special_features": null,
        "type": [],
        "move_types": [],
        "weakness": []
    }
    ]
    """

    def __init__(self):
        """
        CardAnalyzerクラスの初期化処理
        
        YOLO-WorldモデルとGemini APIクライアントのセットアップ、
        および画像保存用ディレクトリの作成を行います。
        """
        self._setup_yolo()
        self._setup_gemini()
        
        # 保存用ディレクトリの作成
        self.base_dir = settings.MEDIA_ROOT / 'bulk_register'
        self.original_dir = self.base_dir / 'originals'
        self.cropped_dir = self.base_dir / 'cropped'
        self.debug_dir = self.base_dir / 'debug'
        
        for d in [self.original_dir, self.cropped_dir, self.debug_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def _setup_yolo(self):
        """
        YOLOモデルのセットアップ
        
        パフォーマンス向上のため、検出クラス("one card")を設定済みの
        カスタムモデルを作成・保存し、再利用します。
        
        保存先: /root/.cache/ultralytics/custom_yolov8s_one_card.pt
        (docker-compose.ymlのyolo_modelsボリュームにより永続化)
        """
        # ultralyticsのデフォルトキャッシュディレクトリ
        # Docker環境では /root/.cache/ultralytics
        # docker-compose.ymlでボリュームマウントされているか確認すること
        cache_dir =  os.path.expanduser("~/.cache/ultralytics") 
        custom_model_name = "custom_yolov8s_one_card.pt"
        custom_model_path = os.path.join(cache_dir, custom_model_name)

        try:
            if os.path.exists(custom_model_path):
                # カスタムモデルが存在する場合はそれをロード (高速)
                logger.info(f"Loading cached custom model: {custom_model_path}")
                self.model = YOLO(custom_model_path)
            else:
                # 存在しない場合はベースモデルをロードしてクラス設定・保存
                logger.info(f"Creating custom model from {self.YOLO_MODEL_NAME}")
                self.model = YOLO(self.YOLO_MODEL_NAME)
                
                # 特定のクラス("one card")をセット
                # これによりCLIPモデルによるテキストエンベディング計算が走る
                self.model.set_classes(self.DETECT_CLASSES)
                
                # カスタムモデルとして保存 (次回以降の高速化)
                # 注: save()は現在の重みを保存する
                self.model.save(custom_model_path)
                logger.info(f"Saved custom model to {custom_model_path}")
                
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            # フォールバック: ベースモデルを毎回ロード
            self.model = YOLO(self.YOLO_MODEL_NAME)
            self.model.set_classes(self.DETECT_CLASSES)

    def _setup_gemini(self):
        """
        Gemini APIクライアントのセットアップ
        
        settings.pyからGEMINI_API_KEYを読み込み、
        指定されたモデル(gemini-2.0-flash-exp)で初期化します。
        
        Raises:
            ValueError: GEMINI_API_KEYが設定されていない場合
        """
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in settings")
        
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel(self.GEMINI_MODEL_NAME)

    def analyze_image(self, image_path: str) -> dict:
        """
        画像解析のメインプロセスを実行します。
        
        1. YOLO-Worldによるカード検出とクロッピング
        2. クロップ画像のグリッド画像への結合
        3. Gemini APIによるカード情報の抽出
        
        Args:
            image_path (str): 解析対象の画像ファイルの絶対パス
            
        Returns:
            dict: 以下のキーを含む解析結果辞書
                - timestamp (str): 処理実行時のタイムスタンプ
                - card_count (int): 検出されたカードの枚数
                - cropped_images (list): 各カードのクロップ画像情報(パス、ID等)のリスト
                - grid_image (str): 生成されたグリッド画像のパス
                - raw_response (str): Gemini APIからの生のJSONレスポンス
                - error (str, optional): エラー発生時のメッセージ
        
        Raises:
            ValueError: 画像の読み込みに失敗した場合
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(image_path)
        
        # 1. 画像読み込み
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
            
        # 2. YOLOによるカード検出
        # パラメータはNotebookでの検証結果(testing_YOLO-World.ipynb)に準拠
        logger.info(f"Running YOLO inference on {image_path}")
        results = self.model.predict(
            image_path,
            conf=self.CONF_THRESHOLD, # 0.01: 低閾値で検出漏れ防止
            iou=self.IOU_THRESHOLD,   # 0.1: 重複検出を厳しく抑制
            imgsz=self.IMG_SIZE,      # 640
            max_det=self.MAX_DET,     # 30
            save=True,                # デバッグ用に検出結果画像を保存
            project=str(self.debug_dir),
            name=f"detect_{timestamp}"
        )
        
        # 3. 検出結果からカード画像を切り出し
        cropped_images = []
        detections = results[0].boxes.data.cpu().numpy() # [x1, y1, x2, y2, conf, cls]
        
        # 座標でソート (上から下、左から右へ)
        # y座標で大まかにソートしてからx座標でソート
        detections = sorted(detections, key=lambda x: (x[1] // 100, x[0]))
        
        for i, det in enumerate(detections):
            x1, y1, x2, y2 = map(int, det[:4])
            
            # マージンを追加 (検出枠より少し広めに)
            h, w = img.shape[:2]
            margin = 10
            x1 = max(0, x1 - margin)
            y1 = max(0, y1 - margin)
            x2 = min(w, x2 + margin)
            y2 = min(h, y2 + margin)
            
            crop = img[y1:y2, x1:x2]
            
            # クロップ画像を一時保存 (プレビュー用)
            crop_filename = f"{timestamp}_{i:02d}.jpg"
            crop_path = self.cropped_dir / crop_filename
            cv2.imwrite(str(crop_path), crop)
            
            cropped_images.append({
                'id': i,
                'path': str(crop_path),
                'image': crop,
                'media_url': f"{settings.MEDIA_URL}bulk_register/cropped/{crop_filename}"
            })
            
        if not cropped_images:
            logger.warning("No cards detected by YOLO")
            return {'error': 'No cards detected', 'count': 0}

        # 4. グリッド画像の作成 (Gemini送信コスト削減のため)
        grid_image_path = self._create_grid_image(cropped_images, timestamp)
        
        # 5. Geminiへ問い合わせ
        gemini_response = self._query_gemini(grid_image_path)
        
        # 6. 生レスポンスの保存 (デバッグ用)
        response_log_path = self.debug_dir / f"response_{timestamp}.txt"
        with open(response_log_path, 'w', encoding='utf-8') as f:
            f.write(gemini_response)

        return {
            'timestamp': timestamp,
            'card_count': len(cropped_images),
            'cropped_images': cropped_images,
            'grid_image': str(grid_image_path),
            'raw_response': gemini_response
        }

    def _create_grid_image(self, cropped_images: list, timestamp: str) -> str:
        """
        複数のカード画像を1枚のグリッド画像に結合する
        
        Args:
            cropped_images: クロップ情報のリスト
            timestamp: タイムスタンプ
            
        Returns:
            保存されたグリッド画像のパス
        """
        # 画像サイズを統一 (幅を基準にリサイズ)
        target_width = 400
        resized_images = []
        
        for item in cropped_images:
            img = item['image']
            h, w = img.shape[:2]
            scale = target_width / w
            new_h = int(h * scale)
            resized = cv2.resize(img, (target_width, new_h))
            
            # 画像IDを描画
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
            
        # グリッド計算 (列数は固定ではないが、適当に計算)
        num_images = len(resized_images)
        cols = 4 # 4列固定
        rows = (num_images + cols - 1) // cols
        
        # 最大の高さを取得してキャンバス作成
        max_h = max(img.shape[0] for img in resized_images)
        grid_h = rows * max_h
        grid_w = cols * target_width
        
        # 白背景のキャンバス
        grid = np.full((grid_h, grid_w, 3), 255, dtype=np.uint8)
        
        for idx, img in enumerate(resized_images):
            r = idx // cols
            c = idx % cols
            
            y_offset = r * max_h
            x_offset = c * target_width
            
            h, w = img.shape[:2]
            grid[y_offset:y_offset+h, x_offset:x_offset+w] = img
            
        save_path = self.debug_dir / f"grid_{timestamp}.jpg"
        cv2.imwrite(str(save_path), grid)
        
        return save_path

    def _query_gemini(self, image_path: str) -> str:
        """
        Gemini APIに画像を送信して解析する
        
        Args:
            image_path: 画像パス
            
        Returns:
            テキストレスポンス
        """
        try:
            # Pillowで画像読み込み
            img = Image.open(image_path)
            
            # API送信
            response = self.gemini_model.generate_content([
                self.GEMINI_PROMPT,
                img
            ])
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            raise
