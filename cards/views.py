from django.shortcuts import render
from django.views.generic import ListView
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType

class CardListView(ListView):
    model = PokemonCard
    template_name = 'cards/card_list.html'
    context_object_name = 'card_list'

    def get_queryset(self):
        # 関連するType, EvolutionStage, SpecialFeature, MoveTypeを事前にフェッチ
        return PokemonCard.objects.select_related(
            'evolution_stage', 'evolves_from'
        ).prefetch_related(
            'types', 'special_features', 'move_types'
        ).all()