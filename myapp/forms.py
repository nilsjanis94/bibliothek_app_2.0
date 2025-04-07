from django import forms
from .models import Ausleihe, BuchExemplar, Schüler, Buch, Mahnung, Rechnung
from datetime import date, timedelta

class BuchForm(forms.ModelForm):
    class Meta:
        model = Buch
        fields = ['ISBN', 'titel', 'autor', 'verlag', 'verlagungsdatum', 'wiederbeschaffungswert']
        widgets = {
            'verlagungsdatum': forms.DateInput(attrs={'type': 'date'}),
        }

class BuchChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.titel} - {obj.autor} (ISBN: {obj.ISBN})"

class BuchExemplarForm(forms.ModelForm):
    buch = BuchChoiceField(queryset=Buch.objects.all())

    class Meta:
        model = BuchExemplar
        fields = ['buch', 'inventarnummer', 'anschaffungsdatum', 'zustand', 'status']
        widgets = {
            'anschaffungsdatum': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        buch_id = kwargs.pop('buch_id', None)
        super().__init__(*args, **kwargs)
        if buch_id:
            self.fields['buch'].initial = buch_id
            self.fields['buch'].widget = forms.HiddenInput()
        self.fields['status'].initial = 'verfügbar'
        self.fields['anschaffungsdatum'].initial = date.today()

class SchülerForm(forms.ModelForm):
    class Meta:
        model = Schüler
        fields = ['schueler_id', 'name', 'vorname', 'klasse', 'email', 'gesperrtBis', 'anzahlVerspätungen']
        widgets = {
            'gesperrtBis': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gesperrtBis'].initial = date(2000, 1, 1)
        self.fields['anzahlVerspätungen'].initial = 0

class ExemplarChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.buch.titel} - {obj.inventarnummer}"

class SchuelerChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.vorname} {obj.name} ({obj.klasse})"

class AusleiheForm(forms.ModelForm):
    exemplar = ExemplarChoiceField(queryset=BuchExemplar.objects.none())
    schüler = SchuelerChoiceField(queryset=Schüler.objects.none())

    class Meta:
        model = Ausleihe
        fields = ['exemplar', 'schüler', 'fälligkeitsdatum']
        widgets = {
            'fälligkeitsdatum': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        exemplar_id = kwargs.pop('exemplar_id', None)
        schueler_id = kwargs.pop('schueler_id', None)
        super().__init__(*args, **kwargs)
        
        # Nur verfügbare Exemplare anzeigen
        verfuegbare_exemplare = BuchExemplar.objects.filter(
            status='verfügbar'
        ).exclude(ausleihen__istZurückgegeben=False)
        
        # Bessere Darstellung im Dropdown
        self.fields['exemplar'].queryset = verfuegbare_exemplare
        
        # Nur Schüler anzeigen, die ausleihen können
        self.fields['schüler'].queryset = Schüler.objects.filter(
            anzahlVerspätungen__lt=3,
            gesperrtBis__lt=date.today()
        )
        
        # Vorausgewählte Werte setzen
        if exemplar_id:
            self.fields['exemplar'].initial = exemplar_id
        if schueler_id:
            self.fields['schüler'].initial = schueler_id
            
        # Standardwert für Fälligkeitsdatum
        self.fields['fälligkeitsdatum'].initial = date.today() + timedelta(days=14)
    
    def clean(self):
        cleaned_data = super().clean()
        exemplar = cleaned_data.get('exemplar')
        schüler = cleaned_data.get('schüler')
        
        if exemplar and not exemplar.istVerfügbar():
            raise forms.ValidationError("Dieses Exemplar ist nicht verfügbar.")
        
        if schüler and not schüler.kannAusleihen():
            raise forms.ValidationError("Dieser Schüler kann keine Bücher ausleihen.")
            
        return cleaned_data

class MahnungForm(forms.ModelForm):
    class Meta:
        model = Mahnung
        fields = ['ausleihe', 'mahnungsTyp']
    
    def __init__(self, *args, **kwargs):
        ausleihe_id = kwargs.pop('ausleihe_id', None)
        super().__init__(*args, **kwargs)
        
        # Nur überfällige Ausleihen anzeigen
        self.fields['ausleihe'].queryset = Ausleihe.objects.filter(
            istZurückgegeben=False,
            fälligkeitsdatum__lt=date.today()
        )
        
        if ausleihe_id:
            self.fields['ausleihe'].initial = ausleihe_id
            self.fields['ausleihe'].widget = forms.HiddenInput()

class RechnungForm(forms.ModelForm):
    class Meta:
        model = Rechnung
        fields = ['ausleihe', 'rechnungsNummer', 'betrag']
    
    def __init__(self, *args, **kwargs):
        ausleihe_id = kwargs.pop('ausleihe_id', None)
        super().__init__(*args, **kwargs)
        
        # Nur überfällige Ausleihen anzeigen
        self.fields['ausleihe'].queryset = Ausleihe.objects.filter(
            istZurückgegeben=False,
            fälligkeitsdatum__lt=date.today()
        )
        
        if ausleihe_id:
            ausleihe = Ausleihe.objects.get(id=ausleihe_id)
            self.fields['ausleihe'].initial = ausleihe_id
            self.fields['ausleihe'].widget = forms.HiddenInput()
            
            if ausleihe.exemplar and ausleihe.exemplar.buch:
                self.fields['betrag'].initial = ausleihe.exemplar.buch.wiederbeschaffungswert
