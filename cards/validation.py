"""
Gemini APIレスポンスのバリデーションモジュール

このモジュールは、Gemini APIから返されるJSON形式のカード情報を検証し、
有効なカテゴリのみを抽出する機能を提供します。
"""

import json
import re
from typing import Dict, List, Any


class GeminiResponseValidator:
    """Gemini APIレスポンスのバリデーションクラス"""
    
    VALID_CATEGORIES = {'pokemon', 'trainers'}
    
    def validate_and_parse_json(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Gemini APIレスポンスからJSONを抽出してパースする
        
        Args:
            response_text: Gemini APIからのレスポンステキスト
            
        Returns:
            パースされたJSON配列
            
        Raises:
            ValueError: JSON形式が不正な場合
        """
        # Markdownコードブロックを除去
        cleaned_text = self._remove_markdown_code_blocks(response_text)
        
        # JSON形式チェックとパース
        try:
            parsed_data = json.loads(cleaned_text)
            
            # 配列であることを確認
            if not isinstance(parsed_data, list):
                raise ValueError("レスポンスはJSON配列である必要があります")
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON形式が不正です: {str(e)}")
    
    def _remove_markdown_code_blocks(self, text: str) -> str:
        """
        Markdownコードブロック(```json ... ```)を除去する
        
        Args:
            text: 処理対象のテキスト
            
        Returns:
            コードブロックを除去したテキスト
        """
        # ```json または ``` で囲まれた部分を抽出
        pattern = r'```(?:json)?\s*([\s\S]*?)```'
        matches = re.findall(pattern, text)
        
        if matches:
            # 最初のコードブロックの内容を返す
            return matches[0].strip()
        
        # コードブロックがない場合はそのまま返す
        return text.strip()
    
    def filter_valid_categories(self, card_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        有効なカテゴリ(pokemon, trainers)のみを抽出し、
        category="Other"とその関連クロップ画像データを除外する
        
        Args:
            card_data: カード情報のリスト
            
        Returns:
            有効なカテゴリのカード情報のみを含むリスト
        """
        valid_cards = []
        
        for card in card_data:
            category = card.get('category', '').lower()
            
            # 有効なカテゴリのみを追加
            if category in self.VALID_CATEGORIES:
                valid_cards.append(card)
        
        return valid_cards
    
    def validate_card_structure(self, card: Dict[str, Any]) -> bool:
        """
        カードデータの構造が正しいかを検証する
        
        Args:
            card: 検証するカードデータ
            
        Returns:
            構造が正しい場合True、そうでない場合False
        """
        required_fields = ['category']
        
        # 必須フィールドの存在チェック
        for field in required_fields:
            if field not in card:
                return False
        
        return True
