from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType, CardCategory
from .filters import PokemonCardFilter, TrainersCardFilter
from .forms import PokemonCardForm
from .utils import find_evolution_root, collect_evolution_line
from .ai_analyzer import CardAnalyzer
from .data_mapper import CardDataMapper
from django.http import JsonResponse
import json
import logging
import uuid

logger = logging.getLogger(__name__)

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

def related_cards_modal(request, pk):
    """関連カード（進化系統）をモーダルで表示"""
    # 起点となるカードを取得
    card = get_object_or_404(PokemonCard, pk=pk, category__slug='pokemon')

    # 進化系統の根元を探す
    root_name = find_evolution_root(card.name)

    # 進化系統の全カード名を収集
    evolution_line_names = collect_evolution_line(root_name)

    # カード名リストからPokemonCardオブジェクトを取得
    related_cards = PokemonCard.objects.filter(
        name__in=evolution_line_names,
        category__slug='pokemon'
    ).select_related(
        'evolution_stage'
    ).prefetch_related(
        'types', 'special_features'
    )

    # 進化段階ごとにグルーピング
    evolution_stages = EvolutionStage.objects.all().order_by('display_order')

    # 各進化段階ごとのカードリストを作成
    stages_with_cards = []
    for stage in evolution_stages:
        cards_in_stage = [c for c in related_cards if c.evolution_stage == stage]
        stages_with_cards.append({
            'stage': stage,
            'cards': cards_in_stage
        })

    context = {
        'origin_card': card,
        'stages_with_cards': stages_with_cards
    }

    return render(request, 'cards/_related_cards_modal.html', context)


# ==========================================
# 一括登録機能 (Bulk Registration)
# ==========================================

def bulk_register_upload(request):
    """一括登録用アップロードモーダルを表示"""
    return render(request, 'cards/_bulk_register_modal.html')

@require_POST
def bulk_register_analyze(request):
    """
    アップロードされた画像を解析し、プレビューを表示する
    """
    if 'image' not in request.FILES:
        return HttpResponse("画像が選択されていません", status=400)

    image_file = request.FILES['image']
    
    # 一時ファイルとして保存
    # 注意: 本番運用ではS3や専用ストレージへの保存、および定期的なクリーンアップが必要
    # ここではメディアディレクトリ内の bulk_register/originals に保存
    import os
    from django.conf import settings
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile

    save_dir = os.path.join(settings.MEDIA_ROOT, 'bulk_register', 'originals')
    os.makedirs(save_dir, exist_ok=True)
    
    # ユニークなファイル名を生成
    ext = os.path.splitext(image_file.name)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(save_dir, filename)
    
    # ファイル保存
    with open(file_path, 'wb+') as destination:
        for chunk in image_file.chunks():
            destination.write(chunk)

    try:
        # AI解析実行
        analyzer = CardAnalyzer()
        analysis_result = analyzer.analyze_image(file_path)
        
        raw_items = []
        try:
            # Geminiのレスポンス(JSON文字列)をパース
            # Markdownコードブロックが含まれている場合のクリーニング
            raw_json = analysis_result['raw_response']
            if "```json" in raw_json:
                raw_json = raw_json.split("```json")[1].split("```")[0]
            elif "```" in raw_json:
                raw_json = raw_json.split("```")[1].split("```")[0]
            
            raw_items = json.loads(raw_json)
        except json.JSONDecodeError as e:
            logger.error(f"JSON Parse Error: {e}")
            logger.error(f"Raw Response: {analysis_result['raw_response']}")
            return HttpResponse("AI解析結果の読み取りに失敗しました", status=500)

        # データマッピング
        mapper = CardDataMapper()
        mapped_items = []
        
        # クロップ画像との紐付け (ID順前提)
        cropped_images = analysis_result.get('cropped_images', [])
        
        for i, raw_item in enumerate(raw_items):
            mapped = mapper.map_item(raw_item)
            mapped['id'] = str(uuid.uuid4()) # 一時ID
            
            # クロップ画像のURLを紐付ける (インデックスが一致すると仮定)
            if i < len(cropped_images):
                mapped['image_url'] = cropped_images[i]['media_url']
            else:
                mapped['image_url'] = None # 画像がない場合
                
            mapped_items.append(mapped)

        # セッションに保存
        request.session['bulk_register_items'] = mapped_items
        
        # プレビュー画面を描画
        return render(request, 'cards/_bulk_register_preview.html', {
            'items': mapped_items,
            'original_image_url': f"{settings.MEDIA_URL}bulk_register/originals/{filename}"
        })

    except Exception as e:
        logger.exception("Bulk Analyze Error")
        return HttpResponse(f"解析中にエラーが発生しました: {str(e)}", status=500)

def bulk_register_edit_item(request, item_id):
    """
    プレビューアイテムの編集 (GET: フォーム表示, POST: 更新)
    """
    items = request.session.get('bulk_register_items', [])
    target_index = next((i for i, item in enumerate(items) if item['id'] == item_id), None)
    
    if target_index is None:
        return HttpResponse("アイテムが見つかりません", status=404)
        
    item = items[target_index]

    if request.method == 'POST':
        # フォームからのデータを反映 (簡易的な実装)
        # 本来はDjango Formを使うのが望ましいが、動的なフィールドが多いため辞書操作で対応
        item['name'] = request.POST.get('name')
        item['hp'] = request.POST.get('hp')
        # ... 他のフィールドの更新処理 ...
        
        # DBルックアップの再実行等のロジックが必要な場合はここに追加
        
        # セッション更新
        items[target_index] = item
        request.session['bulk_register_items'] = items
        request.session.modified = True
        
        # 更新された行だけ再描画
        return render(request, 'cards/_bulk_register_preview_row.html', {'item': item})

    else:
        # 編集フォーム（行内編集用）を返す
        # ここでは簡易的に、現在の行をinputタグに置き換えたHTMLを返す想定
        # 実際には _bulk_register_edit_row.html などのテンプレートを使用
        return render(request, 'cards/_bulk_register_edit_row.html', {'item': item})

def bulk_register_delete_item(request, item_id):
    """プレビューアイテムの削除"""
    items = request.session.get('bulk_register_items', [])
    items = [item for item in items if item['id'] != item_id]
    request.session['bulk_register_items'] = items
    request.session.modified = True
    return HttpResponse("") # 行を削除

@require_POST
def bulk_register_submit(request):
    """一括登録の実行"""
    items = request.session.get('bulk_register_items', [])
    if not items:
        return HttpResponse("登録するデータがありません", status=400)
    
    registered_count = 0
    try:
        for item_data in items:
            # バリデーション: 必須項目チェックなど
            if not item_data.get('name') or not item_data.get('category'):
                continue # 名前かカテゴリがないものはスキップ
            
            # モデルインスタンス作成
            card = PokemonCard(
                name=item_data['name'],
                category=item_data['category'], # CardDataMapperですでにモデルインスタンス化されているかIDになっている前提
                evolution_stage=item_data.get('evolution_stage'),
                evolves_from=item_data.get('evolves_from'),
                trainer_type=item_data.get('trainer_type'),
                memo=item_data.get('memo', ''),
                quantity=1
            )
            card.save()
            
            # ManyToManyフィールドの設定
            if item_data.get('types'):
                card.types.set(item_data['types'])
                
            if item_data.get('special_features'):
                card.special_features.set(item_data['special_features'])
                
            if item_data.get('special_trainers'):
                card.special_trainers.set(item_data['special_trainers'])
                
            # move_typesの保存
            if item_data.get('move_types'):
                card.move_types.set(item_data['move_types'])
            
            # 画像の保存処理 (必要であればクロップ画像を永続化)
            # 現在は一時ファイルのURLを持っているだけなので、
            # 本格実装ではFileFieldに保存し直す処理が必要
            
            registered_count += 1
            
        # セッションクリア
        del request.session['bulk_register_items']
        
        # 成功メッセージと共にモーダルを閉じる等のアクション
        response = HttpResponse(f"<div class='alert alert-success'>{registered_count}件のカードを登録しました</div>")
        response['HX-Trigger'] = 'cardCreated' # リスト更新
        return response

    except Exception as e:
        logger.exception("Bulk Submit Error")
        return HttpResponse(f"登録中にエラーが発生しました: {str(e)}", status=500)