from django import forms
from .models import Ausleihe, BuchExemplar, Schüler

class AusleiheForm(forms.ModelForm):
    class Meta:
        model = Ausleihe
        fields = ['exemplar', 'schüler', 'fälligkeitsdatum']
        widgets = {
            'fälligkeitsdatum': forms.DateInput(attrs={'type': 'date'}),
        }
