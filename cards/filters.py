import django_filters
from django import forms
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType

class PokemonCardFilter(django_filters.FilterSet):
    """ポケモンカードの絞り込みを行うためのFilterSet"""
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='カード名',
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )

    types = django_filters.ModelChoiceFilter(
        queryset=Type.objects.all(),
        label='タイプ',
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'})
    )

    evolution_stage = django_filters.ModelChoiceFilter(
        queryset=EvolutionStage.objects.all(),
        label='進化段階',
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'})
    )

    special_features = django_filters.ModelChoiceFilter(
        queryset=SpecialFeature.objects.all(),
        label='特別',
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'})
    )

    move_types = django_filters.ModelChoiceFilter(
        queryset=MoveType.objects.all(),
        label='わざのエネルギータイプ',
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'})
    )

    CHOICES = (
        ('name', '名前 (昇順)'),
        ('-name', '名前 (降順)'),
        ('quantity', '枚数 (少ない順)'),
        ('-quantity', '枚数 (多い順)'),
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
            'evolution_stage__display_order',
            'created_at',
        ),
        choices=CHOICES,
        empty_label=None,
    )

    class Meta:
        model = PokemonCard
        # fields の指定により、GETパラメータのキー名とフィルタのフィールド名が一致する
        fields = ['name', 'types', 'evolution_stage', 'special_features', 'move_types', 'ordering']
