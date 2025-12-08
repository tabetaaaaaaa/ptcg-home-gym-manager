from django.db import models

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

    def __str__(self):
        return self.name

class PokemonCard(models.Model):
    """ポケモンカード"""
    name = models.CharField("カード名称", max_length=100)
    quantity = models.PositiveIntegerField("所持枚数", default=0)
    image = models.ImageField("画像", upload_to='cards/', null=True, blank=True)
    memo = models.TextField("メモ", null=True, blank=True)
    evolves_from = models.CharField("進化元カード", max_length=100, null=True, blank=True)
    # 外部キー (Foreign Key)
    evolution_stage = models.ForeignKey(EvolutionStage, on_delete=models.PROTECT, verbose_name="進化段階", default=1)

    # 多対多 (Many-to-Many)
    types = models.ManyToManyField(Type, verbose_name="タイプ", blank=False)
    special_features = models.ManyToManyField(SpecialFeature, verbose_name="特別", blank=True)
    move_types = models.ManyToManyField(MoveType, verbose_name="わざのエネルギータイプ", blank=True)

    # 日時
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']