from django.contrib import admin
from import_export.admin import ImportExportModelAdmin # 追加
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType

# PokemonCardAdminを定義し、ImportExportModelAdminを継承させる
class PokemonCardAdmin(ImportExportModelAdmin):
    pass

@admin.register(EvolutionStage)
class EvolutionStageAdmin(admin.ModelAdmin):
    """EvolutionStageモデルの管理画面設定"""
    list_display = ('name', 'display_order')
    list_editable = ('display_order',)

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    """Typeモデルの管理画面設定"""
    list_display = ('name', 'display_order')
    list_editable = ('display_order',)

@admin.register(SpecialFeature)
class SpecialFeatureAdmin(admin.ModelAdmin):
    """SpecialFeatureモデルの管理画面設定"""
    list_display = ('name', 'display_order')
    list_editable = ('display_order',)

@admin.register(MoveType)
class MoveTypeAdmin(admin.ModelAdmin):
    """MoveTypeモデルの管理画面設定"""
    list_display = ('name', 'display_order')
    list_editable = ('display_order',)

admin.site.register(PokemonCard, PokemonCardAdmin)