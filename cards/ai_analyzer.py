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

logger = logging.getLogger(__name__)

class CardAnalyzer:
    """カード画像解析クラス"""
    
    # YOLO-World設定 (Notebookの検証結果に基づく)
    YOLO_MODEL_NAME = 'yolov8s-worldv2.pt'
    DETECT_CLASSES = ["one card"]
    CONF_THRESHOLD = 0.01
    IOU_THRESHOLD = 0.1
    MAX_DET = 30
    IMG_SIZE = 640

    # Gemini設定
    GEMINI_MODEL_NAME = 'gemini-2.5-flash' 
    
    GEMINI_PROMPT = """
    あなたはポケモンカードの専門家です。
    画像内の要素を左上から順に読み取り、以下のJSON配列形式のみを出力してください。
    画像品質が悪くても推測して補完してください。
    Markdown記法は一切含めないでください。

    # データ定義
    - 全ての項目は必須です。値がない場合は `null` (文字列, 数値) または `[]` (配列)、`false` (真偽値)、を使用してください。
    - `category`: "pokemon", "trainers", "Other" (ポケモンカード以外の場合)
    - `trainer_type`: "グッズ", "サポート", "スタジアム", "ポケモンのどうぐ" (pokemon/Otherの場合は null)
    - `special_trainers`: `category`が"trainers"でカード色が蛍光ピンクの場合のみ"ACE SPEC"
    - `evolves_from`, `evolution_stage`: Pokemonの進化元・進化段階を表す。カード右上に記載されていることが多い。**画像品質が悪くても推測して補完**すること。
    - `special_features`: Pokemonの特殊分類("ポケモンex", "テラスタル"等)。trainers/Otherの場合は null
    - `hp`, `type`, `move_types`: Pokemonの属性。trainers/Otherの場合は [] (空配列)。同一types, move_typesは一度のみ記載。
    - `weakness`, `resistance`: Pokemonの属性。trainers/Otherの場合は [] (空配列)。カード下部に記載されていることが多い。
    - `retreat_cost`: Pokemonの属性で、にげるためのコストを指す。trainers/Otherの場合は"null"。カード右下に星マークの数として記載される。


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
        "weakness": ["草"].
        "resistance": ["水"],
        "retreat_cost": 2,
        "hp": 170
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
        "weakness": [],
        "resistance": [],
        "retreat_cost": null,
        "hp": null
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
        "weakness": [],
        "resistance": [],
        "retreat_cost": null,
        "hp": null
    }
    ]
    """

    def __init__(self):
        """CardAnalyzerクラスの初期化処理"""
        self._setup_yolo()
        self._setup_gemini()
        # 固定ディレクトリの作成は廃止し、analyze_imageで動的に決定する

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

    def _setup_gemini(self):
        """Gemini APIクライアントのセットアップ"""
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in settings")
        
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
        
        # 5. Geminiへ問い合わせ
        gemini_response = self._query_gemini(str(grid_save_path))
        
        # 6. 生レスポンス保存
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
