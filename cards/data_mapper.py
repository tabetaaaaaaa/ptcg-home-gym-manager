from .models import (
    CardCategory, Type, EvolutionStage, TrainerType,
    SpecialFeature, SpecialTrainer, MoveType
)
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class CardDataMapper:
    """Gemini抽出データをDjangoモデル用データに変換するクラス"""

    def __init__(self):
        # キャッシュ用の辞書 (DBアクセスの削減)
        self._categories = {}
        self._types = {}
        self._evolution_stages = {}
        self._trainer_types = {}
        self._special_features = {}
        self._special_trainers = {}
        self._move_types = {}
        
        # 初期ロード
        self._load_master_data()

    def _load_master_data(self):
        """マスタデータをメモリにロードする"""
        for obj in CardCategory.objects.all():
            self._categories[obj.name] = obj
            self._categories[obj.slug] = obj # slugでも引けるように

        for obj in Type.objects.all():
            self._types[obj.name] = obj

        for obj in EvolutionStage.objects.all():
            self._evolution_stages[obj.name] = obj

        for obj in TrainerType.objects.all():
            self._trainer_types[obj.name] = obj
            
        for obj in SpecialFeature.objects.all():
            self._special_features[obj.name] = obj
            
        for obj in SpecialTrainer.objects.all():
            self._special_trainers[obj.name] = obj
            
        for obj in MoveType.objects.all():
            self._move_types[obj.name] = obj

    def map_item(self, raw_item: dict) -> dict:
        """
        1件の抽出データをマッピングする
        
        Args:
            raw_item (dict): Geminiからの生の辞書データ
            
        Returns:
            dict: マッピング済みデータ。
                  DBに存在しない選択肢は、元の文字列のまま(またはNone)で返し、
                  フロントエンド側で「未登録」として扱うか、新規登録を促す。
        """
        mapped = {
            'name': raw_item.get('name', ''),
            'evolves_from': raw_item.get('evolves_from'),
            'card_number': raw_item.get('card_number'),
            'memo': "", # 後で構築
        }

        # カテゴリ (必須)
        cat_raw = raw_item.get('category', '').lower()
        if cat_raw == 'pokemon':
            mapped['category'] = self._get_category_by_slug_or_name('pokemon', 'ポケモン')
        elif cat_raw == 'trainers' or cat_raw == 'trainer':
            mapped['category'] = self._get_category_by_slug_or_name('trainers', 'トレーナーズ')
        else:
            # Other など
            mapped['category'] = None

        # タイプ (多対多)
        type_raw = raw_item.get('type', [])
        mapped['types'] = self._map_many_to_many(type_raw, self._types)
        
        # わざのエネルギータイプ (多対多)
        move_types_raw = raw_item.get('move_types', [])
        mapped['move_types'] = self._map_many_to_many(move_types_raw, self._move_types)

        # 弱点 (多対多)
        weakness_raw = raw_item.get('weakness', [])
        mapped['weakness'] = self._map_many_to_many(weakness_raw, self._types)

        # 抵抗力 (多対多)
        resistance_raw = raw_item.get('resistance', [])
        mapped['resistance'] = self._map_many_to_many(resistance_raw, self._types)

        # HP / にげるコスト
        mapped['hp'] = raw_item.get('hp')
        mapped['retreat_cost'] = raw_item.get('retreat_cost')

        # 進化段階 (外部キー)
        # プロンプトの例では "evolution_stage" だが、出力例では "evolves_stage" になっている可能性も考慮
        evo_raw = raw_item.get('evolution_stage') or raw_item.get('evolves_stage')
        mapped['evolution_stage'] = self._evolution_stages.get(evo_raw)
        mapped['evolution_stage_raw'] = evo_raw

        # トレーナーズタイプ (外部キー)
        trainer_type_raw = raw_item.get('trainer_type')
        mapped['trainer_type'] = self._trainer_types.get(trainer_type_raw)
        mapped['trainer_type_raw'] = trainer_type_raw

        # 特別ルール / 特殊分類
        mapped['special_features'] = []
        mapped['special_trainers'] = []

        # 1. ACE SPEC (is_ace_spec フラグ または special_trainers 文字列)
        is_ace_spec = raw_item.get('is_ace_spec')
        special_trainers_raw = raw_item.get('special_trainers')
        
        # フラグまたは文字列で検知
        if is_ace_spec is True or special_trainers_raw == "ACE SPEC":
            ace_spec = self._special_trainers.get('ACE SPEC')
            if ace_spec:
                mapped['special_trainers'].append(ace_spec)

        # 2. ポケモンの特殊分類 (special または special_features)
        special_raw = raw_item.get('special') or raw_item.get('special_features', [])
        if isinstance(special_raw, str):
            special_raw = [special_raw]
            
        if special_raw:
            for s in special_raw:
                if s in self._special_features:
                    mapped['special_features'].append(self._special_features[s])

        # メモ欄の構築 (カード番号など、専用フィールドがないもの)
        memo_parts = []
        if mapped['card_number']:
            memo_parts.append(f"No:{mapped['card_number']}")
        
        mapped['memo'] = "\n".join(memo_parts)

        return mapped

    def _get_category_by_slug_or_name(self, slug, name):
        """スラッグまたは名前でカテゴリを検索"""
        if slug in self._categories:
            return self._categories[slug]
        if name in self._categories:
            return self._categories[name]
        return None

    def _map_many_to_many(self, raw_value, master_dict):
        """
        多対多フィールドのマッピング
        
        Args:
            raw_value: 文字列 または 文字列のリスト
            master_dict: 名前をキーとするマスタ辞書
            
        Returns:
            list: マッチしたモデルインスタンスのリスト
        """
        if not raw_value:
            return []
        
        if isinstance(raw_value, str):
            items = [raw_value]
        elif isinstance(raw_value, list):
            items = raw_value
        else:
            return []
            
        result = []
        for item in items:
            if item in master_dict:
                result.append(master_dict[item])
        return result
