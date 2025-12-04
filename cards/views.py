from django.shortcuts import render
from django.views.generic import ListView
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType
from .filters import PokemonCardFilter

class CardListView(ListView):
    model = PokemonCard
    template_name = 'cards/card_list.html'
    context_object_name = 'card_list'

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'evolution_stage', 'evolves_from'
        ).prefetch_related(
            'types', 'special_features', 'move_types'
        )
        self.filterset = PokemonCardFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context