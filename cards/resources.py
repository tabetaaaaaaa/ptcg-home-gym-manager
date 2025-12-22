from import_export import resources, fields, widgets
from .models import (
    PokemonCard, CardCategory, Type, EvolutionStage, 
    SpecialFeature, MoveType, TrainerType, SpecialTrainer
)

class PokemonCardResource(resources.ModelResource):
    name = fields.Field(attribute='name', column_name='名前')
    quantity = fields.Field(attribute='quantity', column_name='枚数')
    category = fields.Field(
        column_name='カテゴリ',
        attribute='category',
        widget=widgets.ForeignKeyWidget(CardCategory, field='name')
    )
    hp = fields.Field(attribute='hp', column_name='HP')
    retreat_cost = fields.Field(attribute='retreat_cost', column_name='にげる')
    evolves_from = fields.Field(attribute='evolves_from', column_name='進化元')
    evolution_stage = fields.Field(
        column_name='進化段階',
        attribute='evolution_stage',
        widget=widgets.ForeignKeyWidget(EvolutionStage, field='name')
    )
    trainer_type = fields.Field(
        column_name='トレーナーズ種別',
        attribute='trainer_type',
        widget=widgets.ForeignKeyWidget(TrainerType, field='name')
    )
    types = fields.Field(
        column_name='タイプ',
        attribute='types',
        widget=widgets.ManyToManyWidget(Type, field='name', separator='|')
    )
    weakness = fields.Field(
        column_name='弱点',
        attribute='weakness',
        widget=widgets.ManyToManyWidget(Type, field='name', separator='|')
    )
    resistance = fields.Field(
        column_name='抵抗力',
        attribute='resistance',
        widget=widgets.ManyToManyWidget(Type, field='name', separator='|')
    )
    special_features = fields.Field(
        column_name='特別な分類_ポケモン',
        attribute='special_features',
        widget=widgets.ManyToManyWidget(SpecialFeature, field='name', separator='|')
    )
    move_types = fields.Field(
        column_name='わざのエネルギータイプ',
        attribute='move_types',
        widget=widgets.ManyToManyWidget(MoveType, field='name', separator='|')
    )
    special_trainers = fields.Field(
        column_name='特別な分類_トレーナーズ',
        attribute='special_trainers',
        widget=widgets.ManyToManyWidget(SpecialTrainer, field='name', separator='|')
    )
    memo = fields.Field(attribute='memo', column_name='メモ')

    class Meta:
        model = PokemonCard
        # idをインポート時のキーとして明示
        import_id_fields = ('id',)
        # 値に変更がない場合はスキップする
        skip_unchanged = True
        report_skipped = True
        # 出力する順番を制御
        fields = (
            'id', 'name', 'quantity', 'category', 'hp', 'retreat_cost', 
            'evolves_from', 'evolution_stage', 'trainer_type', 'types', 
            'weakness', 'resistance', 'special_features', 'move_types', 
            'special_trainers', 'memo'
        )
        export_order = fields

    def before_import_row(self, row, **kwargs):
        """
        インポート前に各行のデータをクレンジングする
        """
        # 数値フィールドが空文字の場合はデフォルト値を設定
        if '枚数' in row and row['枚数'] == '':
            row['枚数'] = '1'
        
        if 'HP' in row and row['HP'] == '':
            row['HP'] = None # NullableなのでNoneをセット
            
        if 'にげる' in row and row['にげる'] == '':
            row['にげる'] = None # NullableなのでNoneをセット
            
        # idが空文字や空の場合はNoneに変換（新規登録として扱うため）
        if 'id' in row and not row['id']:
            row['id'] = None
            
        return super().before_import_row(row, **kwargs)
