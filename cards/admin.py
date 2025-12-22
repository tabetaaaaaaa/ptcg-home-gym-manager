from django.contrib import admin
from import_export.admin import ImportExportModelAdmin # 追加
from .models import PokemonCard, CardCategory, Type, EvolutionStage, SpecialFeature, MoveType, TrainerType, SpecialTrainer, GeminiApiKeyUsage

# PokemonCardAdminを定義し、ImportExportModelAdminを継承させる
class PokemonCardAdmin(ImportExportModelAdmin):
    pass

@admin.register(CardCategory)
class CardCategoryAdmin(admin.ModelAdmin):
    """CardCategoryモデルの管理画面設定"""
    list_display = ('name', 'slug', 'display_order', 'bg_color', 'text_color')
    list_editable = ('display_order', 'bg_color', 'text_color')
    prepopulated_fields = {'slug': ('name',)}  # nameから自動的にslugを生成

@admin.register(EvolutionStage)
class EvolutionStageAdmin(admin.ModelAdmin):
    """EvolutionStageモデルの管理画面設定"""
    list_display = ('name', 'display_order')
    list_editable = ('display_order',)

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    """Typeモデルの管理画面設定"""
    list_display = ('name', 'display_order', 'bg_color', 'text_color')
    list_editable = ('display_order', 'bg_color', 'text_color')

@admin.register(SpecialFeature)
class SpecialFeatureAdmin(admin.ModelAdmin):
    """SpecialFeatureモデルの管理画面設定"""
    list_display = ('name', 'display_order')
    list_editable = ('display_order',)

@admin.register(MoveType)
class MoveTypeAdmin(admin.ModelAdmin):
    """MoveTypeモデルの管理画面設定"""
    list_display = ('name', 'display_order', 'bg_color', 'text_color')
    list_editable = ('display_order', 'bg_color', 'text_color')

@admin.register(TrainerType)
class TrainerTypeAdmin(admin.ModelAdmin):
    """TrainerTypeモデルの管理画面設定"""
    list_display = ('name', 'display_order')
    list_editable = ('display_order',)

@admin.register(SpecialTrainer)
class SpecialTrainerAdmin(admin.ModelAdmin):
    """SpecialTrainerモデルの管理画面設定"""
    list_display = ('name', 'display_order', 'bg_color', 'text_color')
    list_editable = ('display_order', 'bg_color', 'text_color')

@admin.register(GeminiApiKeyUsage)
class GeminiApiKeyUsageAdmin(admin.ModelAdmin):
    """GeminiApiKeyUsageモデルの管理画面設定"""
    list_display = ['key_index', 'usage_count', 'last_reset_date', 'updated_at']
    readonly_fields = ['key_index', 'updated_at']
    ordering = ['key_index']

admin.site.register(PokemonCard, PokemonCardAdmin)