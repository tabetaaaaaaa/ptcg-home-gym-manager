from django.db import models

class Type(models.Model):
    """カードのタイプ (例: 炎, 水)"""
    name = models.CharField("属性名", max_length=50, unique=True)

    def __str__(self):
        return self.name

class EvolutionStage(models.Model):
    """進化段階 (例: たね, 1進化)"""
    name = models.CharField("進化段階", max_length=50, unique=True)

    def __str__(self):
        return self.name

class SpecialFeature(models.Model):
    """特徴 (例: ex, V)"""
    name = models.CharField("特徴", max_length=50, unique=True)

    def __str__(self):
        return self.name

class MoveType(models.Model):
    """わざの属性 (例: 炎, 水, 無色)"""
    name = models.CharField("わざの属性名", max_length=50, unique=True)

    def __str__(self):
        return self.name

class PokemonCard(models.Model):
    """ポケモンカード"""
    name = models.CharField("カード名称", max_length=100)
    quantity = models.PositiveIntegerField("所持枚数", default=0)
    image_path = models.CharField("画像ファイルパス", max_length=255, null=True, blank=True)
    memo = models.TextField("メモ", null=True, blank=True)
    
    # 外部キー (Foreign Key)
    evolution_stage = models.ForeignKey(EvolutionStage, on_delete=models.PROTECT, verbose_name="進化段階")
    evolves_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="進化元カード")

    # 多対多 (Many-to-Many)
    types = models.ManyToManyField(Type, verbose_name="タイプ")
    special_features = models.ManyToManyField(SpecialFeature, verbose_name="特徴", blank=True)
    move_types = models.ManyToManyField(MoveType, verbose_name="わざの属性", blank=True)

    # 日時
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    def __str__(self):
        return self.name