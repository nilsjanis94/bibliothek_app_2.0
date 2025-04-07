from django.db import models
from datetime import datetime, timedelta, date
from typing import List
from django.utils import timezone

class StatusMixin:
    STATUS_VERFUEGBAR = 'verfügbar'
    STATUS_AUSGELIEHEN = 'ausgeliehen'
    STATUS_VERLOREN = 'verloren'
    STATUS_BESCHAEDIGT = 'beschädigt'
    
    STATUS_CHOICES = [
        (STATUS_VERFUEGBAR, 'Verfügbar'),
        (STATUS_AUSGELIEHEN, 'Ausgeliehen'),
        (STATUS_VERLOREN, 'Verloren'),
        (STATUS_BESCHAEDIGT, 'Beschädigt'),
    ]

class Buch(models.Model):
    ISBN = models.CharField(max_length=13, unique=True)
    titel = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    verlag = models.CharField(max_length=200)
    verlagungsdatum = models.DateField()
    wiederbeschaffungswert = models.DecimalField(max_digits=10, decimal_places=2)

    def getBuchExemplare(self)->List["BuchExemplar"]:
        return BuchExemplar.objects.filter(buch=self)

    def __str__(self):
        return self.titel

class BuchExemplar(StatusMixin, models.Model):
    buch = models.ForeignKey(
        Buch, 
        on_delete=models.CASCADE,
        related_name='buchexemplare'
    )
    inventarnummer = models.CharField(max_length=200)
    anschaffungsdatum = models.DateField()
    zustand = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=StatusMixin.STATUS_CHOICES, default=StatusMixin.STATUS_VERFUEGBAR)

    def istVerfügbar(self)->bool:
        return (self.status == self.STATUS_VERFUEGBAR and 
                not self.ausleihen.filter(istZurueckgegeben=False).exists())
    
    def setStatusAusgeliehen(self)->None:
        self.status = self.STATUS_AUSGELIEHEN
        self.save()
        
    def setStatusVerfügbar(self)->None:
        self.status = self.STATUS_VERFUEGBAR
        self.save()
    
    def getBuch(self)->"Buch":
        return self.buch

    def __str__(self):
        return self.inventarnummer

class Schueler(models.Model):
    schueler_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    vorname = models.CharField(max_length=200)
    klasse = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    gesperrtBis = models.DateField(default=datetime(2000, 1, 1))
    anzahlVerspaetungen = models.IntegerField(default=0)

    def kannAusleihen(self)->bool:
        return self.anzahlVerspaetungen < 3 and self.gesperrtBis < date.today()
    
    def getAktuelleAusleihen(self)->List["Ausleihe"]:
        return Ausleihe.objects.filter(schueler=self, istZurueckgegeben=False)
    
    def sperrenFuerSechsMonate(self)->None:
        self.gesperrtBis = date.today() + timedelta(days=180)
        self.anzahlVerspaetungen = 0
        self.save()

    def __str__(self):
        return self.name

class Ausleihe(models.Model):
    exemplar = models.ForeignKey(
        BuchExemplar,
        on_delete=models.SET_NULL,
        related_name='ausleihen',
        null=True,
        blank=True
    )
    schueler = models.ForeignKey(
        Schueler,
        on_delete=models.CASCADE,
        related_name='ausleihen'
    )
    ausleihdatum = models.DateField()
    rueckgabedatum = models.DateField(null=True, blank=True)
    faelligkeitsdatum = models.DateField()
    istZurueckgegeben = models.BooleanField(default=False)
    erinnerungGesendet = models.BooleanField(default=False)
    mahnungGesendet = models.BooleanField(default=False)

    def istUeberfaellig(self)->bool:
        return self.rueckgabedatum is None and self.faelligkeitsdatum < date.today()
    
    def istVierWochenUeberfaellig(self)->bool:
        return self.rueckgabedatum is None and self.faelligkeitsdatum + timedelta(days=28) < date.today()
    
    def zurueckgeben(self)->None:
        self.rueckgabedatum = date.today()
        self.istZurueckgegeben = True
        exemplar = self.exemplar
        self.exemplar = None
        self.save()
        if exemplar:
            exemplar.setStatusVerfügbar()
    
    def __str__(self):
        return str(self.ausleihdatum)

class Rechnung(models.Model):
    ausleihe = models.ForeignKey(
        Ausleihe,
        on_delete=models.CASCADE,
        related_name='rechnungen'
    )
    rechnungsNummer = models.CharField(max_length=200)
    datum = models.DateField()
    betrag = models.DecimalField(max_digits=10, decimal_places=2)
    istBezahlt = models.BooleanField(default=False)

    def berechneBetrag(self)->None:
        self.betrag = self.ausleihe.exemplar.buch.wiederbeschaffungswert
        self.save()
    
    def markiereAlsBezahlt(self)->None:
        self.istBezahlt = True
        self.save()

    def __str__(self):
        return f"Rechnung {self.rechnungsNummer} über {self.betrag}€"

class Mahnung(models.Model):
    ausleihe = models.ForeignKey(
        Ausleihe,
        on_delete=models.CASCADE,
        related_name='mahnungen'
    )
    erstellungsdatum = models.DateField()
    mahnungsTyp = models.CharField(max_length=200)
    istBearbeitet = models.BooleanField(default=False)

    def getRechnung(self)->"Rechnung":
        return Rechnung.objects.get(ausleihe=self.ausleihe)
    
    def erstelleRechnung(self)->"Rechnung":
        rechnung = Rechnung(
            ausleihe=self.ausleihe,
            rechnungsNummer=f"R{self.ausleihe.id}-{date.today().strftime('%Y%m%d')}",
            datum=date.today(),
            betrag=self.ausleihe.exemplar.buch.wiederbeschaffungswert
        )
        rechnung.save()
        return rechnung
    
    def __str__(self):
        return f"Mahnung für Ausleihe #{self.ausleihe.id} vom {self.erstellungsdatum}"
    
    
    
    
