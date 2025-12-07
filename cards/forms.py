from django import forms
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType

class PokemonCardForm(forms.ModelForm):
    class Meta:
        model = PokemonCard
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(),
            'quantity': forms.NumberInput(),
            'evolution_stage': forms.Select(),
            'evolves_from': forms.TextInput(),
            'types': forms.CheckboxSelectMultiple(),
            'special_features': forms.CheckboxSelectMultiple(),
            'move_types': forms.CheckboxSelectMultiple(),
            'memo': forms.Textarea(attrs={'rows': 3}),
            'image': forms.ClearableFileInput(),
        }
