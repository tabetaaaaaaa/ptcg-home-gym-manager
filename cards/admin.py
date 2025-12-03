from django.contrib import admin
from import_export.admin import ImportExportModelAdmin # 追加
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType

# PokemonCardAdminを定義し、ImportExportModelAdminを継承させる
class PokemonCardAdmin(ImportExportModelAdmin):
    pass

admin.site.register(PokemonCard, PokemonCardAdmin) # 変更
admin.site.register(Type)
admin.site.register(EvolutionStage)
admin.site.register(SpecialFeature)
admin.site.register(MoveType)