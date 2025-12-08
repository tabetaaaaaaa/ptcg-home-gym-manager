from django import forms
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType

class PokemonCardForm(forms.ModelForm):
    class Meta:
        model = PokemonCard
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered input-primary w-full'}),
            'quantity': forms.NumberInput(attrs={'class': 'input input-bordered input-primary w-full'}),
            'evolution_stage': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'evolves_from': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': '例: ピカチュウ'}),
            'types': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-primary'}),
            'special_features': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-secondary'}),
            'move_types': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-accent'}),
            'trainer_type': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'special_trainers': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-secondary'}),
            'memo': forms.Textarea(attrs={'class': 'textarea textarea-bordered textarea-primary w-full', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered file-input-primary w-full'}),
            'category': forms.HiddenInput(),
        }
