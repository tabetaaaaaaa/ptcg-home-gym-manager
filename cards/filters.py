import django_filters
from django import forms
from django.db.models import Q
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType, TrainerType, SpecialTrainer
from .widgets import RangeSliderWidget

class PokemonCardFilter(django_filters.FilterSet):
    """ポケモンカードの絞り込みを行うためのFilterSet"""
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='カード名',
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )

    types = django_filters.ModelMultipleChoiceFilter(
        queryset=Type.objects.all(),
        label='タイプ',
        widget=forms.CheckboxSelectMultiple
    )

    evolution_stage = django_filters.ModelMultipleChoiceFilter(
        queryset=EvolutionStage.objects.all(),
        label='進化段階',
        widget=forms.CheckboxSelectMultiple
    )

    special_features = django_filters.ModelMultipleChoiceFilter(
        queryset=SpecialFeature.objects.all(),
        label='特別',
        widget=forms.CheckboxSelectMultiple
    )

    move_types = django_filters.ModelMultipleChoiceFilter(
        queryset=MoveType.objects.all(),
        label='わざのエネルギータイプ',
        widget=forms.CheckboxSelectMultiple
    )

    weakness = django_filters.ModelMultipleChoiceFilter(
        queryset=Type.objects.all(),
        label='弱点',
        widget=forms.CheckboxSelectMultiple
    )

    resistance = django_filters.ModelMultipleChoiceFilter(
        queryset=Type.objects.all(),
        label='抵抗力',
        widget=forms.CheckboxSelectMultiple
    )

    hp = django_filters.RangeFilter(
        field_name='hp',
        label='HP',
        widget=RangeSliderWidget(min_val=0, max_val=400, step=10),
        method='filter_range_with_null'
    )

    retreat_cost = django_filters.RangeFilter(
        field_name='retreat_cost',
        label='にげるエネルギー',
        widget=RangeSliderWidget(min_val=0, max_val=5, step=1),
        method='filter_range_with_null'
    )

    CHOICES = (
        ('name', '名前 (昇順)'),
        ('-name', '名前 (降順)'),
        ('quantity', '枚数 (少ない順)'),
        ('-quantity', '枚数 (多い順)'),
        ('hp', 'HP (少ない順)'),
        ('-hp', 'HP (多い順)'),
        ('retreat_cost', 'にげる (少ない順)'),
        ('-retreat_cost', 'にげる (多い順)'),
        ('evolution_stage__display_order', '進化度合い (昇順)'),
        ('-evolution_stage__display_order', '進化度合い (降順)'),
        ('-created_at', '登録日時 (新しい順)'),
        ('created_at', '登録日時 (古い順)'),
    )

    ordering = django_filters.OrderingFilter(
        label='並び替え',
        fields=(
            'name',
            'quantity',
            'hp',
            'retreat_cost',
            'evolution_stage__display_order',
            'created_at',
        ),
        choices=CHOICES,
                    empty_label=None,
                )
    class Meta:
        model = PokemonCard
        # fields の指定により、GETパラメータのキー名とフィルタのフィールド名が一致する
        fields = ['name', 'types', 'evolution_stage', 'special_features', 'move_types', 'weakness', 'resistance', 'hp', 'retreat_cost', 'ordering']

    def filter_range_with_null(self, queryset, name, value):
        """
        null（未設定）の値を 0 として扱い、指定された範囲に含まれる場合に表示するカスタムフィルタ。
        また、選択された上限が最大値（HPなら400、にげるなら5）の場合は、上限なしとして処理する。
        """
        if value:
            start = value.start
            stop = value.stop

            # フィルタ対象に応じた最大リミットの設定
            max_limit = 400 if name == 'hp' else 5 if name == 'retreat_cost' else None

            # フィルタ条件の構築
            q_objects = Q()

            # 下限の設定
            if start is not None:
                if start <= 0:
                    # 0を含む場合はnull（未設定）も対象に含める
                    q_objects &= (Q(**{f"{name}__gte": 0}) | Q(**{f"{name}__isnull": True}))
                else:
                    q_objects &= Q(**{f"{name}__gte": start})

            # 上限の設定
            if stop is not None:
                # 最大値に達している場合は、上限フィルタを適用しない（400+ の意味を持たせる）
                if max_limit is not None and stop >= max_limit:
                    pass
                else:
                    q_objects &= Q(**{f"{name}__lte": stop})

            return queryset.filter(q_objects)
        return queryset


class TrainersCardFilter(django_filters.FilterSet):
    """トレーナーズカードの絞り込みを行うためのFilterSet"""
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='カード名',
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )

    trainer_type = django_filters.ModelMultipleChoiceFilter(
        queryset=TrainerType.objects.all(),
        label='トレーナーズ種別',
        widget=forms.CheckboxSelectMultiple
    )

    special_trainers = django_filters.ModelMultipleChoiceFilter(
        queryset=SpecialTrainer.objects.all(),
        label='特別な分類',
        widget=forms.CheckboxSelectMultiple
    )

    memo = django_filters.CharFilter(
        field_name='memo',
        lookup_expr='icontains',
        label='メモ',
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )

    CHOICES = (
        ('name', '名前 (昇順)'),
        ('-name', '名前 (降順)'),
        ('quantity', '枚数 (少ない順)'),
        ('-quantity', '枚数 (多い順)'),
        ('trainer_type__display_order', '種別 (昇順)'),
        ('-trainer_type__display_order', '種別 (降順)'),
        ('-created_at', '登録日時 (新しい順)'),
        ('created_at', '登録日時 (古い順)'),
    )

    ordering = django_filters.OrderingFilter(
        label='並び替え',
        fields=(
            'name',
            'quantity',
            'trainer_type__display_order',
            'created_at',
        ),
        choices=CHOICES,
        empty_label=None,
    )

    class Meta:
        model = PokemonCard
        fields = ['name', 'trainer_type', 'special_trainers', 'memo', 'ordering']

