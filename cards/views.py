from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType
from .filters import PokemonCardFilter
from .forms import PokemonCardForm

def card_create(request):
    if request.method == 'POST':
        form = PokemonCardForm(request.POST)
        if form.is_valid():
            card = form.save()
            # データベースからリレーションを再取得
            card = PokemonCard.objects.select_related(
                'evolution_stage', 'evolves_from'
            ).prefetch_related(
                'types', 'special_features', 'move_types'
            ).get(pk=card.pk)
            response = render(request, 'cards/_card_item.html', {'card': card})
            response['HX-Trigger'] = 'closeModal'
            return response
        else:
            # バリデーション失敗時はフォームを再描画
            return render(request, 'cards/_card_form.html', {'form': form})
    else: # GET request
        form = PokemonCardForm()
        return render(request, 'cards/_card_form.html', {'form': form})


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

@require_POST
def increase_card_quantity(request, pk):
    card = get_object_or_404(PokemonCard, pk=pk)
    card.quantity += 1
    card.save()
    return render(request, 'cards/_card_item.html', {'card': card})

@require_POST
def decrease_card_quantity(request, pk):
    card = get_object_or_404(PokemonCard, pk=pk)
    if card.quantity > 0:
        card.quantity -= 1
        card.save()
    return render(request, 'cards/_card_item.html', {'card': card})