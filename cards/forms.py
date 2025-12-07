from django import forms
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType

class PokemonCardForm(forms.ModelForm):
    class Meta:
        model = PokemonCard
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'quantity': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'evolution_stage': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'evolves_from': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'types': forms.SelectMultiple(attrs={'class': 'select select-bordered w-full'}),
            'special_features': forms.SelectMultiple(attrs={'class': 'select select-bordered w-full'}),
            'move_types': forms.SelectMultiple(attrs={'class': 'select select-bordered w-full'}),
            'memo': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
        }
