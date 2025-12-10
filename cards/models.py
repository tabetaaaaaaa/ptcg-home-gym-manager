from django.db import models

class CardCategory(models.Model):
    """カードの大分類 (例: ポケモン, トレーナーズ)"""
    name = models.CharField("カテゴリ名", max_length=50, unique=True)
    slug = models.SlugField("URL用スラッグ", unique=True)
    display_order = models.PositiveIntegerField("表示順", default=0)
    bg_color = models.CharField("背景色", max_length=7, default="#6b7280", help_text="例: #ff0000")
    text_color = models.CharField("文字色", max_length=7, default="#ffffff", help_text="例: #000000")

    class Meta:
        ordering = ['display_order']
        verbose_name = "カードカテゴリ"
        verbose_name_plural = "カードカテゴリ"

    def __str__(self):
        return self.name

class Type(models.Model):
    """カードのタイプ (例: 炎, 水)"""
    name = models.CharField("属性名", max_length=50, unique=True)
    display_order = models.PositiveIntegerField("表示順", default=0)
    bg_color = models.CharField("背景色", max_length=7, default="#6b7280", help_text="例: #ff0000")
    text_color = models.CharField("文字色", max_length=7, default="#ffffff", help_text="例: #000000")

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name

class EvolutionStage(models.Model):
    """進化段階 (例: たね, 1進化)"""
    name = models.CharField("進化段階", max_length=50, unique=True)
    display_order = models.PositiveIntegerField("表示順", default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name

class SpecialFeature(models.Model):
    """特別 (例: ex, V)"""
    name = models.CharField("特別", max_length=50, unique=True)
    display_order = models.PositiveIntegerField("表示順", default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name

class MoveType(models.Model):
    """わざのタイプ (例: 炎, 水, 無色)"""
    name = models.CharField("わざのエネルギータイプ", max_length=50, unique=True)
    display_order = models.PositiveIntegerField("表示順", default=0)
    bg_color = models.CharField("背景色", max_length=7, default="#6b7280", help_text="例: #ff0000")
    text_color = models.CharField("文字色", max_length=7, default="#ffffff", help_text="例: #000000")

    class Meta:
        ordering = ['display_order']
        verbose_name = "わざのエネルギータイプ"
        verbose_name_plural = "わざのエネルギータイプ"

    def __str__(self):
        return self.name

class TrainerType(models.Model):
    """トレーナーズカードの種別 (例: 道具, サポート, スタジアム) - トレーナーズ専用"""
    name = models.CharField("トレーナーズ種別", max_length=50, unique=True)
    display_order = models.PositiveIntegerField("表示順", default=0)
    bg_color = models.CharField("背景色", max_length=7, default="#6b7280", help_text="例: #ff0000")
    text_color = models.CharField("文字色", max_length=7, default="#ffffff", help_text="例: #000000")

    class Meta:
        ordering = ['display_order']
        verbose_name = "トレーナーズ種別"
        verbose_name_plural = "トレーナーズ種別"

    def __str__(self):
        return self.name

class SpecialTrainer(models.Model):
    """トレーナーズカードの特別な分類 (例: ACE, 通常) - トレーナーズ専用"""
    name = models.CharField("特別な分類", max_length=50, unique=True)
    display_order = models.PositiveIntegerField("表示順", default=0)
    bg_color = models.CharField("背景色", max_length=7, default="#6b7280", help_text="例: #ff0000")
    text_color = models.CharField("文字色", max_length=7, default="#ffffff", help_text="例: #000000")

    class Meta:
        ordering = ['display_order']
        verbose_name = "特別な分類"
        verbose_name_plural = "特別な分類"

    def __str__(self):
        return self.name

class PokemonCard(models.Model):
    """ポケモンカード・トレーナーズカード統合モデル"""
    # === 共通フィールド ===
    name = models.CharField("カード名称", max_length=100)
    quantity = models.PositiveIntegerField("所持枚数", default=1)
    image = models.ImageField("画像", upload_to='cards/', null=True, blank=True)
    memo = models.TextField("メモ", null=True, blank=True)

    # === カテゴリ (新規追加) ===
    # default=1 を指定することで、マイグレーション時に既存データは自動的にID=1のカテゴリ（ポケモン）に設定される
    category = models.ForeignKey(
        CardCategory,
        on_delete=models.PROTECT,
        verbose_name="カテゴリ",
        default=1,  # マイグレーション時の既存データ保護用
        help_text="ポケモンまたはトレーナーズ"
    )

    # === ポケモン専用フィールド ===
    evolves_from = models.CharField("進化元カード", max_length=100, null=True, blank=True)
    # evolution_stageを null=True に変更（既存データは保持される）
    evolution_stage = models.ForeignKey(
        EvolutionStage,
        on_delete=models.PROTECT,
        verbose_name="進化段階",
        null=True,  # トレーナーズカードのため null 許可s
        blank=True
    )

    # === トレーナーズ専用フィールド (新規追加) ===
    trainer_type = models.ForeignKey(
        TrainerType,
        on_delete=models.PROTECT,
        verbose_name="トレーナーズ種別",
        null=True,  # ポケモンカードのため null 許可
        blank=True,
        related_name='cards'
    )

    # === 多対多 (既存) ===
    types = models.ManyToManyField(Type, verbose_name="タイプ", blank=True)
    special_features = models.ManyToManyField(SpecialFeature, verbose_name="特別", blank=True)
    move_types = models.ManyToManyField(MoveType, verbose_name="わざのエネルギータイプ", blank=True)

    # === 多対多 (新規追加) ===
    special_trainers = models.ManyToManyField(
        SpecialTrainer,
        verbose_name="特別な分類",
        blank=True,
        related_name='cards'
    )

    # === 日時 ===
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "カード"
        verbose_name_plural = "カード"