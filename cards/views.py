import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
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
from google.api_core.exceptions import ResourceExhausted
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
    file_url = os.path.join(settings.MEDIA_URL, 'bulk_register', 'originals', filename)
    
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
            
            # セッション保存のためにモデルインスタンスをIDに変換しつつ、表示用名称も保存
            if mapped.get('category'):
                mapped['category_name'] = mapped['category'].name
                mapped['category'] = mapped['category'].id
            else:
                mapped['category_name'] = '未設定'

            if mapped.get('evolution_stage'):
                mapped['evolution_stage_name'] = mapped['evolution_stage'].name
                mapped['evolution_stage'] = mapped['evolution_stage'].id
            
            if mapped.get('trainer_type'):
                mapped['trainer_type_name'] = mapped['trainer_type'].name
                mapped['trainer_type'] = mapped['trainer_type'].id
                
            # ManyToManyのリスト(オブジェクト)をIDのリストに変換 & 名称リスト作成
            for field in ['types', 'special_features', 'move_types', 'special_trainers']:
                if mapped.get(field):
                    # 表示用名称リスト (例: types_names)
                    mapped[f'{field}_names'] = [obj.name for obj in mapped[field]]
                    mapped[field] = [obj.id for obj in mapped[field]]

            # クロップ画像のURLを紐付ける (インデックスが一致すると仮定)
            if i < len(cropped_images):
                mapped['image_url'] = cropped_images[i]['media_url']
            else:
                mapped['image_url'] = None # 画像がない場合
                
            mapped_items.append(mapped)
            
        # セッションに保存
        request.session['bulk_register_items'] = mapped_items
        
        return render(request, 'cards/_bulk_register_preview.html', {
            'items': mapped_items,
            'original_image_url': file_url
        })

    except ResourceExhausted:
        logger.error("Gemini API Quota Exceeded")
        # エラーメッセージを含めてモーダルを再表示（またはエラー専用テンプレート）
        # ここでは簡易的にHTTPレスポンスでエラーを返す（HTMXがエラーハンドリングできる形にするのが理想だが、
        # モーダル内を置換するターゲット設定になっているため、エラーメッセージ付きのDIVを返すのがUX的に良い）
        error_html = """
        <div class="alert alert-error shadow-lg my-4">
            <div>
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <span>AIサービスが混雑しており利用制限にかかりました。申し訳ありませんが、しばらく時間を置いてから再試行してください。</span>
            </div>
        </div>
        <div class="text-center">
            <button class="btn" onclick="document.getElementById('bulk-modal-form').close()">閉じる</button>
        </div>
        """
        return HttpResponse(error_html)

    except Exception as e:
        logger.error(f"Bulk Register Analyze Error: {e}", exc_info=True)
        error_html = f"""
        <div class="alert alert-error shadow-lg my-4">
            <div>
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <span>エラーが発生しました: {str(e)}</span>
            </div>
        </div>
        <div class="text-center">
             <button class="btn" onclick="document.getElementById('bulk-modal-form').close()">閉じる</button>
        </div>
        """
        return HttpResponse(error_html)

def bulk_register_edit_item(request, item_id):
    """
    プレビューアイテムの編集 (GET: フォーム表示, POST: 更新)
    モーダルでの編集を行います。
    """
    items = request.session.get('bulk_register_items', [])
    target_index = next((i for i, item in enumerate(items) if item['id'] == item_id), None)
    
    if target_index is None:
        return HttpResponse("アイテムが見つかりません", status=404)
        
    item = items[target_index]
    
    # 既存フォームを利用するために初期データを準備
    initial_data = item.copy()
    
    if request.method == 'POST':
        # フォームバリデーションのためにカテゴリなどの必須フィールドが含まれているか確認
        form = PokemonCardForm(request.POST)
        
        # ファイル入力フィールド(image)はセッション編集では扱わないためrequiredから外す等の調整が必要かも知れないが、
        # ModelFormなのでデフォルトでバリデーションがかかる。
        # ただし、今回はインスタンスを保存しないので、is_valid()だけ通れば良い。
        # 画像フィールドのエラーは無視するか、request.FILESを渡さないことで空扱いにする。
        
        if form.is_valid():
            cleaned_data = form.cleaned_data
            
            # セッションデータを更新 (IDと画像URLは維持)
            for key, value in cleaned_data.items():
                if key == 'image': continue # 画像は変更しない
                
                # ModelオブジェクトはIDに変換、QuerySetはIDリストに変換して保存
                # 同時に表示用名称(_name)も更新する
                if hasattr(value, 'id'):
                    item[key] = value.id
                    # 表示用名称の更新 (category -> category_name)
                    if key in ['category', 'evolution_stage', 'trainer_type']:
                        item[f'{key}_name'] = value.name
                
                elif hasattr(value, '__iter__') and not isinstance(value, str):
                    # ManyToMany (QuerySet or list of objects)
                    item[key] = [v.id for v in value]
                    # 表示用名称リストの更新
                    if key in ['types', 'special_features', 'move_types', 'special_trainers']:
                        item[f'{key}_names'] = [v.name for v in value]
                elif value is None:
                    item[key] = None
                    # Noneになった場合の名称クリア
                    if key in ['category', 'evolution_stage', 'trainer_type']:
                        item[f'{key}_name'] = None
                else:
                    item[key] = value

            items[target_index] = item
            request.session['bulk_register_items'] = items
            request.session.modified = True
            
            # 更新された行をレンダリングして返す
            response = render(request, 'cards/_bulk_register_preview_row.html', {'item': item})
            response['HX-Trigger'] = 'closeModal'
            return response
        else:
            return render(request, 'cards/_bulk_edit_modal.html', {
                'form': form, 
                'item': item,
                'item_id': item_id
            })

    else:
        # GET: 編集モーダルを表示
        form = PokemonCardForm(initial=initial_data)
        return render(request, 'cards/_bulk_edit_modal.html', {
            'form': form, 
            'item': item,
            'item_id': item_id
        })

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
    
    for item in items:
        # バリデーション: 必須項目チェックなど
        if not item.get('name') or not item.get('category'):
            continue # 名前かカテゴリがないものはスキップ

        # 画像の処理 (一時URLから保存)
        image_content = None
        filename = None
        if item.get('image_url'):
            # 相対パスを取得 (/media/bulk_register/cropped/xxx.jpg -> bulk_register/cropped/xxx.jpg)
            relative_path = item['image_url'].replace(settings.MEDIA_URL, '')
            full_path = settings.MEDIA_ROOT / relative_path
            
            if full_path.exists():
                try:
                    with open(full_path, 'rb') as f:
                        image_content = ContentFile(f.read())
                        filename = full_path.name
                except Exception as e:
                    logger.warning(f"Failed to load image for saving: {e}")

        try:
            # ForeignKeyはIDで指定するために _id サフィックスを使用
            card = PokemonCard(
                name=item.get('name') or "名称不明",
                quantity=item.get('quantity', 1),
                memo=item.get('memo', ''),
                # ForeignKey fields (pass IDs directly)
                category_id=item.get('category'),
                evolution_stage_id=item.get('evolution_stage'),
                trainer_type_id=item.get('trainer_type'),
                # CharFields
                evolves_from=item.get('evolves_from'),
            )
            
            if image_content and filename:
                card.image.save(filename, image_content, save=False)
            
            card.save()
            
            # ManyToManyフィールドの設定
            if item.get('types'):
                card.types.set(item['types'])
                
            if item.get('special_features'):
                card.special_features.set(item['special_features'])
                
            if item.get('move_types'):
                card.move_types.set(item['move_types'])
                
            if item.get('special_trainers'):
                card.special_trainers.set(item['special_trainers'])

            registered_count += 1

        except Exception as e:
            logger.error(f"Failed to save card: {item.get('name')}, Error: {e}")
            continue # エラーが出ても他のカードは保存を試みる

    # セッションクリア (全ての処理が終わった後)
    if 'bulk_register_items' in request.session:
        del request.session['bulk_register_items']
    
    # 成功メッセージと共にモーダルを閉じる等のアクション
    # モーダルを閉じるためのJSを含める
    response = HttpResponse(f"""
        <div class='alert alert-success shadow-lg'>
            <div>
                <svg xmlns='http://www.w3.org/2000/svg' class='stroke-current flex-shrink-0 h-6 w-6' fill='none' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' /></svg>
                <span>{registered_count}件のカードを登録しました</span>
            </div>
        </div>
        <script>
            setTimeout(function() {{
                const modal = document.getElementById('bulk-preview-modal');
                if(modal) modal.close();
            }}, 1500);
        </script>
    """)
    response['HX-Trigger'] = 'cardCreated' # リスト更新
    return response