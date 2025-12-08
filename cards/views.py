from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType, CardCategory
from .filters import PokemonCardFilter, TrainersCardFilter
from .forms import PokemonCardForm

def card_create(request, category_slug):
    category = get_object_or_404(CardCategory, slug=category_slug)
    if request.method == 'POST':
        form = PokemonCardForm(request.POST, request.FILES)
        if form.is_valid():
            card = form.save()
            # データベースからリレーションを再取得
            card = PokemonCard.objects.select_related(
                'evolution_stage', 'trainer_type', 'category'
            ).prefetch_related(
                'types', 'special_features', 'move_types', 'special_trainers'
            ).get(pk=card.pk)

            # 表示モードとカードのカテゴリに応じて適切なテンプレートを返す
            view_mode = request.session.get('view_mode', 'card')
            if view_mode == 'table':
                template_name = f'cards/_{card.category.slug}_card_table_row.html'
                card_html = render(request, template_name, {'card': card}).content.decode('utf-8')
                # <tr>要素を正しいHTML構造でラップ
                card_html = f'<table id="temp-card-container" style="display:none;"><tbody>{card_html}</tbody></table>'
            else:
                template_name = 'cards/_card_item.html'
                card_html = render(request, template_name, {'card': card}).content.decode('utf-8')

            # 空のフォームを生成してOOBスワップで返す
            new_form = PokemonCardForm(initial={'category': category})
            form_html = render(request, 'cards/_card_form.html', {
                'form': new_form,
                'view_mode': view_mode,
                'show_success': True,
                'category_slug': category_slug, # カテゴリ情報をフォームに渡す
            }).content.decode('utf-8')

            # カードのHTMLとフォームのHTMLを結合して返す
            response = HttpResponse(card_html + form_html)
            # カスタムイベントでリスト更新をトリガー
            response['HX-Trigger'] = 'cardCreated'
            return response
        else:
            # バリデーション失敗時はフォームを再描画
            view_mode = request.session.get('view_mode', 'card')
            return render(request, 'cards/_card_form.html', {'form': form, 'view_mode': view_mode, 'category_slug': category_slug})
    else: # GET request
        form = PokemonCardForm(initial={'category': category})
        view_mode = request.session.get('view_mode', 'card')
        return render(request, 'cards/_card_form.html', {'form': form, 'view_mode': view_mode, 'category_slug': category_slug})

@require_http_methods(["GET", "POST"])
def card_edit(request, pk):
    card = get_object_or_404(PokemonCard, pk=pk)
    if request.method == 'POST':
        form = PokemonCardForm(request.POST, request.FILES, instance=card)
        if form.is_valid():
            card = form.save()
            # データベースからリレーションを再取得
            card = PokemonCard.objects.select_related(
                'evolution_stage', 'trainer_type', 'category'
            ).prefetch_related(
                'types', 'special_features', 'move_types', 'special_trainers'
            ).get(pk=card.pk)

            # 表示モードとカードのカテゴリに応じて適切なテンプレートを返す
            view_mode = request.session.get('view_mode', 'card')
            if view_mode == 'table':
                template_name = f'cards/_{card.category.slug}_card_table_row.html'
            else:
                template_name = 'cards/_card_item.html'
            response = render(request, template_name, {'card': card})

            response['HX-Trigger'] = 'closeModal'
            return response
        else:
            # バリデーション失敗時はフォームを再描画
            view_mode = request.session.get('view_mode', 'card')
            category_slug = card.category.slug if card.category else None
            return render(request, 'cards/_card_form.html', {'form': form, 'card': card, 'view_mode': view_mode, 'category_slug': category_slug})
    else: # GET request
        form = PokemonCardForm(instance=card)
        view_mode = request.session.get('view_mode', 'card')
        # 編集対象のカテゴリ情報をテンプレートに渡す
        category_slug = card.category.slug if card.category else None
        return render(request, 'cards/_card_form.html', {'form': form, 'card': card, 'view_mode': view_mode, 'category_slug': category_slug})


class PokemonCardListView(ListView):
    model = PokemonCard
    template_name = 'cards/pokemon_card_list.html'
    context_object_name = 'card_list'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().filter(category__slug='pokemon').select_related(
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
        return ['cards/pokemon_card_list.html']


class TrainersCardListView(PokemonCardListView):
    template_name = 'cards/trainers_card_list.html'

    def get_queryset(self):
        queryset = super(PokemonCardListView, self).get_queryset().filter(
            category__slug='trainers'
        ).select_related(
            'trainer_type'
        ).prefetch_related(
            'special_trainers'
        )
        self.filterset = TrainersCardFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_template_names(self):
        if self.request.htmx:
            return ['cards/_card_list_content.html']
        return ['cards/trainers_card_list.html']

@require_POST
def increase_card_quantity(request, pk):
    card = get_object_or_404(
        PokemonCard.objects.select_related(
            'evolution_stage', 'trainer_type', 'category'
        ).prefetch_related(
            'types', 'special_features', 'move_types', 'special_trainers'
        ),
        pk=pk
    )
    card.quantity += 1
    card.save() 
    # 表示モードとカードのカテゴリに応じて適切なテンプレートを返す
    view_mode = request.session.get('view_mode', 'card')
    if view_mode == 'table':
        template_name = f'cards/_{card.category.slug}_card_table_row.html'
    else:
        template_name = 'cards/_card_item.html'
    return render(request, template_name, {'card': card})

@require_POST
def decrease_card_quantity(request, pk):
    card = get_object_or_404(
        PokemonCard.objects.select_related(
            'evolution_stage', 'trainer_type', 'category'
        ).prefetch_related(
            'types', 'special_features', 'move_types', 'special_trainers'
        ),
        pk=pk
    )
    if card.quantity > 0:
        card.quantity -= 1
        card.save()

    # 表示モードとカードのカテゴリに応じて適切なテンプレートを返す
    view_mode = request.session.get('view_mode', 'card')
    if view_mode == 'table':
        template_name = f'cards/_{card.category.slug}_card_table_row.html'
    else:
        template_name = 'cards/_card_item.html'
    return render(request, template_name, {'card': card})

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


@require_POST
def toggle_view_mode(request):
    """表示モード(card/table)を切り替える"""
    current_mode = request.session.get('view_mode', 'card')
    new_mode = 'table' if current_mode == 'card' else 'card'
    request.session['view_mode'] = new_mode

    # リファラをチェックして、適切なリストビューにリダイレクトする
    referer = request.META.get('HTTP_REFERER')
    if referer and 'trainers' in referer:
        return redirect('cards:trainer_card_list')
    return redirect('cards:pokemon_card_list')

def card_detail_modal(request, pk):
    """カード詳細をモーダルで表示"""
    card = get_object_or_404(
        PokemonCard.objects.select_related(
            'evolution_stage', 'trainer_type', 'category'
        ).prefetch_related(
            'types', 'special_features', 'move_types', 'special_trainers'
        ),
        pk=pk
    )
    if card.category.slug == 'pokemon':
        template_name = 'cards/_pokemon_card_detail_modal.html'
    else:
        template_name = 'cards/_trainers_card_detail_modal.html'
    return render(request, template_name, {'card': card})