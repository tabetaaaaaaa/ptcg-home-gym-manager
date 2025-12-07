from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType
from .filters import PokemonCardFilter
from .forms import PokemonCardForm

def card_create(request):
    if request.method == 'POST':
        form = PokemonCardForm(request.POST, request.FILES)
        if form.is_valid():
            card = form.save()
            # データベースからリレーションを再取得
            card = PokemonCard.objects.select_related(
                'evolution_stage'
            ).prefetch_related(
                'types', 'special_features', 'move_types'
            ).get(pk=card.pk)

            # 表示モードに応じて適切なテンプレートを返す
            view_mode = request.session.get('view_mode', 'card')
            if view_mode == 'table':
                response = render(request, 'cards/_card_table_row.html', {'card': card})
            else:
                response = render(request, 'cards/_card_item.html', {'card': card})

            response['HX-Trigger'] = 'closeModal'
            return response
        else:
            # バリデーション失敗時はフォームを再描画
            view_mode = request.session.get('view_mode', 'card')
            return render(request, 'cards/_card_form.html', {'form': form, 'view_mode': view_mode})
    else: # GET request
        form = PokemonCardForm()
        view_mode = request.session.get('view_mode', 'card')
        return render(request, 'cards/_card_form.html', {'form': form, 'view_mode': view_mode})

@require_http_methods(["GET", "POST"])
def card_edit(request, pk):
    card = get_object_or_404(PokemonCard, pk=pk)
    if request.method == 'POST':
        form = PokemonCardForm(request.POST, request.FILES, instance=card)
        if form.is_valid():
            card = form.save()
            # データベースからリレーションを再取得
            card = PokemonCard.objects.select_related(
                'evolution_stage'
            ).prefetch_related(
                'types', 'special_features', 'move_types'
            ).get(pk=card.pk)

            # 表示モードに応じて適切なテンプレートを返す
            view_mode = request.session.get('view_mode', 'card')
            if view_mode == 'table':
                response = render(request, 'cards/_card_table_row.html', {'card': card})
            else:
                response = render(request, 'cards/_card_item.html', {'card': card})

            response['HX-Trigger'] = 'closeModal'
            return response
        else:
            # バリデーション失敗時はフォームを再描画
            view_mode = request.session.get('view_mode', 'card')
            return render(request, 'cards/_card_form.html', {'form': form, 'card': card, 'view_mode': view_mode})
    else: # GET request
        form = PokemonCardForm(instance=card)
        view_mode = request.session.get('view_mode', 'card')
        return render(request, 'cards/_card_form.html', {'form': form, 'card': card, 'view_mode': view_mode})


class CardListView(ListView):
    model = PokemonCard
    template_name = 'cards/card_list.html'
    context_object_name = 'card_list'

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'evolution_stage'
        ).prefetch_related(
            'types', 'special_features', 'move_types'
        )
        self.filterset = PokemonCardFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['view_mode'] = self.request.session.get('view_mode', 'card')
        return context

    def get_template_names(self):
        if self.request.htmx:
            return ['cards/_card_list_content.html']
        return ['cards/card_list.html']

@require_POST
def increase_card_quantity(request, pk):
    card = get_object_or_404(
        PokemonCard.objects.select_related('evolution_stage')
        .prefetch_related('types', 'special_features', 'move_types'),
        pk=pk
    )
    card.quantity += 1
    card.save()

    # 表示モードに応じて適切なテンプレートを返す
    view_mode = request.session.get('view_mode', 'card')
    if view_mode == 'table':
        return render(request, 'cards/_card_table_row.html', {'card': card})
    else:
        return render(request, 'cards/_card_item.html', {'card': card})

@require_POST
def decrease_card_quantity(request, pk):
    card = get_object_or_404(
        PokemonCard.objects.select_related('evolution_stage')
        .prefetch_related('types', 'special_features', 'move_types'),
        pk=pk
    )
    if card.quantity > 0:
        card.quantity -= 1
        card.save()

    # 表示モードに応じて適切なテンプレートを返す
    view_mode = request.session.get('view_mode', 'card')
    if view_mode == 'table':
        return render(request, 'cards/_card_table_row.html', {'card': card})
    else:
        return render(request, 'cards/_card_item.html', {'card': card})

@require_http_methods(["GET", "DELETE"])
def card_delete(request, pk):
    card = get_object_or_404(PokemonCard, pk=pk)

    if request.method == 'GET':
        # 確認モーダルのHTMLを返す
        return render(request, 'cards/_card_confirm_delete.html', {'card': card})

    elif request.method == 'DELETE':
        # カードを削除
        card.delete()
        # htmxがこのレスポンスを受け取ると、hx-targetで指定された要素をDOMから削除する
        # さらに、HX-Triggerヘッダーでモーダルを閉じるようフロントエンドに指示する
        response = HttpResponse("")
        response['HX-Trigger'] = 'closeModal'
        return response

def card_name_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = PokemonCard.objects.filter(name__icontains=query).order_by('name')[:5]
    context = {'suggestions': [s.name for s in suggestions]}
    return render(request, 'cards/_card_suggestions.html', context)

@require_POST
def toggle_view_mode(request):
    """表示モード(card/table)を切り替える"""
    current_mode = request.session.get('view_mode', 'card')
    new_mode = 'table' if current_mode == 'card' else 'card'
    request.session['view_mode'] = new_mode
    return redirect('cards:card_list')

def card_detail_modal(request, pk):
    """カード詳細をモーダルで表示"""
    card = get_object_or_404(
        PokemonCard.objects.select_related('evolution_stage')
        .prefetch_related('types', 'special_features', 'move_types'),
        pk=pk
    )
    return render(request, 'cards/_card_detail_modal.html', {'card': card})