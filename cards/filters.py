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
        label='特徴',
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'})
    )

    move_types = django_filters.ModelChoiceFilter(
        queryset=MoveType.objects.all(),
        label='わざの属性',
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'})
    )

    class Meta:
        model = PokemonCard
        # fields の指定により、GETパラメータのキー名とフィルタのフィールド名が一致する
        fields = ['name', 'types', 'evolution_stage', 'special_features', 'move_types']
