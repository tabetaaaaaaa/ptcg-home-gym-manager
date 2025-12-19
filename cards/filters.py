import django_filters
from django import forms
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType, TrainerType, SpecialTrainer

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
        widget=django_filters.widgets.RangeWidget(attrs={'class': 'input input-bordered input-sm w-full'})
    )

    retreat_cost = django_filters.RangeFilter(
        field_name='retreat_cost',
        label='にげる',
        widget=django_filters.widgets.RangeWidget(attrs={'class': 'input input-bordered input-sm w-full'})
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

