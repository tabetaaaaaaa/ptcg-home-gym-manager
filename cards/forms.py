from django import forms
from .models import PokemonCard, Type, EvolutionStage, SpecialFeature, MoveType

class CustomClearableFileInput(forms.ClearableFileInput):
    clear_checkbox_label = '画像クリア'

class PokemonCardForm(forms.ModelForm):
    class Meta:
        model = PokemonCard
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered input-primary w-full'}),
            'quantity': forms.NumberInput(attrs={'class': 'input input-bordered input-primary w-full'}),
            'evolution_stage': forms.Select(attrs={'class': 'select select-bordered select-secondary w-full'}),
            'evolves_from': forms.TextInput(attrs={'class': 'input input-bordered input-secondary w-full', 'placeholder': '例: ピカチュウ'}),
            'types': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-primary'}),
            'special_features': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-secondary'}),
            'move_types': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-accent'}),
            'trainer_type': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'special_trainers': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-secondary'}),
            'memo': forms.Textarea(attrs={'class': 'textarea textarea-bordered textarea-neutral w-full', 'rows': 3}),
            'image': CustomClearableFileInput(attrs={'class': 'file-input file-input-bordered file-input-secondary w-full'}),
            'category': forms.HiddenInput(),
        }
