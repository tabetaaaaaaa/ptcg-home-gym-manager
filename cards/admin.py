from django.contrib import admin
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType

admin.site.register(PokemonCard)
admin.site.register(Type)
admin.site.register(EvolutionStage)
admin.site.register(SpecialFeature)
admin.site.register(MoveType)