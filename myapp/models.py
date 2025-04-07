from django.db import models
from datetime import datetime, timedelta, date
from typing import List

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

class BuchExemplar(models.Model):
    STATUS_CHOICES = [
        ('verfügbar', 'Verfügbar'),
        ('ausgeliehen', 'Ausgeliehen'),
        ('reserviert', 'Reserviert'),
        ('reparatur', 'In Reparatur'),
        ('verloren', 'Verloren'),
    ]

    buch = models.ForeignKey(
        Buch, 
        on_delete=models.CASCADE,
        related_name='buchexemplare'
    )
    inventarnummer = models.CharField(max_length=200)
    anschaffungsdatum = models.DateField()
    zustand = models.CharField(max_length=200)
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='verfügbar')

    def istVerfügbar(self)->bool:
        return (self.status == 'verfügbar' and 
                not self.ausleihen.filter(istZurückgegeben=False).exists())
    
    def setStatusAusgeliehen(self)->None:
        self.status = 'ausgeliehen'
        self.save()
        
    def setStatusVerfügbar(self)->None:
        self.status = 'verfügbar'
        self.save()
    
    def getBuch(self)->"Buch":
        return self.buch

    def __str__(self):
        return self.inventarnummer

class Schüler(models.Model):
    schueler_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    vorname = models.CharField(max_length=200)
    klasse = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    gesperrtBis = models.DateField(default=datetime(2000, 1, 1))
    anzahlVerspätungen = models.IntegerField(default=0)

    def kannAusleihen(self)->bool:
        return self.anzahlVerspätungen < 3 and self.gesperrtBis < date.today()
    
    def getAktuelleAusleihen(self)->List["Ausleihe"]:
        return Ausleihe.objects.filter(schüler=self, istZurückgegeben=False)
    
    def sperrenFuerSechsMonate(self)->None:
        self.gesperrtBis = date.today() + timedelta(days=180)
        self.anzahlVerspätungen = 0
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
    schüler = models.ForeignKey(
        Schüler,
        on_delete=models.CASCADE,
        related_name='ausleihen'
    )
    ausleihdatum = models.DateField()
    rueckgabedatum = models.DateField(null=True, blank=True)
    fälligkeitsdatum = models.DateField()
    istZurückgegeben = models.BooleanField(default=False)
    erinnerungGesendet = models.BooleanField(default=False)
    mahnungGesendet = models.BooleanField(default=False)

    def istÜberfällig(self)->bool:
        return self.rueckgabedatum is None and self.fälligkeitsdatum < date.today()
    
    def istVierWochenÜberfällig(self)->bool:
        return self.rueckgabedatum is None and self.fälligkeitsdatum + timedelta(days=28) < date.today()
    
    def zurueckgeben(self)->None:
        self.rueckgabedatum = date.today()
        self.istZurückgegeben = True
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
    
    def makiereAlsBezahlt(self)->None:
        self.istBezahlt = True
        self.save()

    def __str__(self):
        return self.rechnungsNummer

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
        return Rechnung.objects.get(ausleihe=self)
    
    def erstelleRechnung(self)->"Rechnung":
        rechnung = Rechnung(
            ausleihe=self.ausleihe,
            rechnungsNummer=str(self.ausleihe.id),
            datum=date.today(),
            betrag=self.ausleihe.exemplar.buch.wiederbeschaffungswert
        )
        rechnung.save()
        return rechnung
    
    def __str__(self):
        return str(self.erstellungsdatum)
    
    
    
    
