from django import forms
from .models import Ausleihe, BuchExemplar, Schueler, Buch, Mahnung, Rechnung
from datetime import date, timedelta

class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.EmailInput, forms.DateInput)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})

class BuchForm(BaseForm):
    class Meta:
        model = Buch
        fields = ['titel', 'autor', 'ISBN', 'verlag', 'verlagungsdatum', 'wiederbeschaffungswert']
        widgets = {
            'verlagungsdatum': forms.DateInput(attrs={'type': 'date'}),
            'wiederbeschaffungswert': forms.NumberInput(attrs={'step': '0.01'}),
        }

class BuchChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.titel} - {obj.autor} (ISBN: {obj.ISBN})"

class BuchExemplarForm(BaseForm):
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

class SchuelerForm(BaseForm):
    class Meta:
        model = Schueler
        fields = ['vorname', 'name', 'klasse', 'email', 'gesperrtBis', 'anzahlVerspaetungen']
        widgets = {
            'gesperrtBis': forms.DateInput(attrs={'type': 'date'}),
            'anzahlVerspaetungen': forms.NumberInput(attrs={'min': 0}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gesperrtBis'].initial = date(2000, 1, 1)
        self.fields['anzahlVerspaetungen'].initial = 0

class ExemplarChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.buch.titel} - {obj.inventarnummer}"

class SchuelerChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.vorname} {obj.name} ({obj.klasse})"

class AusleiheForm(BaseForm):
    exemplar = ExemplarChoiceField(queryset=BuchExemplar.objects.none())
    schueler = SchuelerChoiceField(queryset=Schueler.objects.none())

    class Meta:
        model = Ausleihe
        fields = ['exemplar', 'schueler', 'faelligkeitsdatum']
        widgets = {
            'faelligkeitsdatum': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        exemplar_id = kwargs.pop('exemplar_id', None)
        schueler_id = kwargs.pop('schueler_id', None)
        super().__init__(*args, **kwargs)
        
        # Filtere verfügbare Exemplare
        self.fields['exemplar'].queryset = BuchExemplar.objects.filter(status=BuchExemplar.STATUS_VERFUEGBAR)
        
        # Filtere Schüler, die ausleihen dürfen
        self.fields['schueler'].queryset = Schueler.objects.filter(
            gesperrtBis__lt=date.today(),
            anzahlVerspaetungen__lt=3
        )
        
        # Setze vorausgewählte Werte
        if exemplar_id:
            self.fields['exemplar'].initial = exemplar_id
        if schueler_id:
            self.fields['schueler'].initial = schueler_id
            
        # Setze Standardwert für Fälligkeitsdatum (14 Tage ab heute)
        self.fields['faelligkeitsdatum'].initial = date.today() + timedelta(days=14)

    def clean(self):
        cleaned_data = super().clean()
        exemplar = cleaned_data.get('exemplar')
        schueler = cleaned_data.get('schueler')
        
        if exemplar and not exemplar.istVerfügbar():
            raise forms.ValidationError('Das Exemplar ist nicht verfügbar.')
            
        if schueler and not schueler.kannAusleihen():
            raise forms.ValidationError('Der Schüler ist gesperrt und darf keine Bücher ausleihen.')
            
        return cleaned_data

class MahnungForm(BaseForm):
    class Meta:
        model = Mahnung
        fields = ['mahnungsTyp']

class RechnungForm(forms.ModelForm):
    class Meta:
        model = Rechnung
        fields = ['ausleihe', 'rechnungsNummer', 'betrag']
    
    def __init__(self, *args, **kwargs):
        ausleihe_id = kwargs.pop('ausleihe_id', None)
        super().__init__(*args, **kwargs)
        
        # Nur überfällige Ausleihen anzeigen
        self.fields['ausleihe'].queryset = Ausleihe.objects.filter(
            istZurueckgegeben=False,
            faelligkeitsdatum__lt=date.today()
        )
        
        if ausleihe_id:
            ausleihe = Ausleihe.objects.get(id=ausleihe_id)
            self.fields['ausleihe'].initial = ausleihe_id
            self.fields['ausleihe'].widget = forms.HiddenInput()
            
            if ausleihe.exemplar and ausleihe.exemplar.buch:
                self.fields['betrag'].initial = ausleihe.exemplar.buch.wiederbeschaffungswert
