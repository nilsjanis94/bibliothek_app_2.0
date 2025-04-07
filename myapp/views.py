from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Buch, BuchExemplar, Schueler, Ausleihe, Mahnung, Rechnung
from .forms import AusleiheForm, BuchForm, BuchExemplarForm, SchuelerForm, MahnungForm
from datetime import datetime, timedelta, date
from django.contrib import messages
from django.utils import timezone

def index(request):
    return render(request, 'myapp/index.html')

def buch_liste(request):
    buecher = Buch.objects.all()
    return render(request, 'myapp/buch_liste.html', {'buecher': buecher})

def buch_detail(request, buch_id):
    buch = get_object_or_404(Buch, id=buch_id)
    exemplare = buch.buchexemplare.all()
    return render(request, 'myapp/buch_detail.html', {'buch': buch, 'exemplare': exemplare})

def schueler_liste(request):
    schueler = Schueler.objects.all()
    return render(request, 'myapp/schueler_liste.html', {'schueler': schueler})

def schueler_detail(request, schueler_id):
    schueler = get_object_or_404(Schueler, id=schueler_id)
    ausleihen = schueler.ausleihen.all()
    return render(request, 'myapp/schueler_detail.html', {'schueler': schueler, 'ausleihen': ausleihen})

def ausleihe_liste(request):
    ausleihen = Ausleihe.objects.filter(istZurueckgegeben=False).select_related('exemplar__buch', 'schueler')
    return render(request, 'myapp/ausleihe_liste.html', {'ausleihen': ausleihen})

def ausleihe_detail(request, ausleihe_id):
    ausleihe = get_object_or_404(Ausleihe, id=ausleihe_id)
    return render(request, 'myapp/ausleihe_detail.html', {'ausleihe': ausleihe})

def ausleihe_neu(request):
    if request.method == 'POST':
        form = AusleiheForm(request.POST)
        if form.is_valid():
            ausleihe = form.save(commit=False)
            ausleihe.ausleihdatum = date.today()
            ausleihe.save()
            ausleihe.exemplar.setStatusAusgeliehen()
            messages.success(request, 'Ausleihe wurde erfolgreich erstellt.')
            return redirect('myapp:ausleihe_detail', ausleihe_id=ausleihe.id)
    else:
        form = AusleiheForm()
    return render(request, 'myapp/ausleihe_form.html', {'form': form})

def ausleihe_rueckgabe(request, ausleihe_id):
    ausleihe = get_object_or_404(Ausleihe, id=ausleihe_id)
    if not ausleihe.istZurueckgegeben:
        ausleihe.istZurueckgegeben = True
        ausleihe.exemplar.setStatusVerfügbar()
        ausleihe.save()
        messages.success(request, 'Buch wurde erfolgreich zurückgegeben.')
    return redirect('myapp:ausleihe_detail', ausleihe_id=ausleihe.id)

def exemplar_neu(request):
    if request.method == 'POST':
        form = BuchExemplarForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exemplar wurde erfolgreich erstellt.')
            return redirect('myapp:exemplar_liste')
    else:
        form = BuchExemplarForm()
    return render(request, 'myapp/exemplar_form.html', {'form': form})

def buch_neu(request):
    if request.method == 'POST':
        form = BuchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Buch wurde erfolgreich erstellt.')
            return redirect('myapp:buch_liste')
    else:
        form = BuchForm()
    return render(request, 'myapp/buch_form.html', {'form': form})

def buch_bearbeiten(request, buch_id):
    buch = get_object_or_404(Buch, id=buch_id)
    if request.method == 'POST':
        form = BuchForm(request.POST, instance=buch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Buch wurde erfolgreich aktualisiert.')
            return redirect('myapp:buch_detail', buch_id=buch.id)
    else:
        form = BuchForm(instance=buch)
    return render(request, 'myapp/buch_form.html', {'form': form, 'buch': buch})

def schueler_neu(request):
    if request.method == 'POST':
        form = SchuelerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schüler wurde erfolgreich erstellt.')
            return redirect('myapp:schueler_liste')
    else:
        form = SchuelerForm()
    return render(request, 'myapp/schueler_form.html', {'form': form})

def schueler_bearbeiten(request, schueler_id):
    schueler = get_object_or_404(Schueler, id=schueler_id)
    if request.method == 'POST':
        form = SchuelerForm(request.POST, instance=schueler)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schüler wurde erfolgreich aktualisiert.')
            return redirect('myapp:schueler_detail', schueler_id=schueler.id)
    else:
        form = SchuelerForm(instance=schueler)
    return render(request, 'myapp/schueler_form.html', {'form': form, 'schueler': schueler})

def schueler_loeschen(request, schueler_id):
    schueler = get_object_or_404(Schueler, id=schueler_id)
    if Ausleihe.objects.filter(schueler=schueler, istZurueckgegeben=False).exists():
        messages.error(request, 'Der Schüler kann nicht gelöscht werden, da er noch Bücher ausgeliehen hat.')
        return redirect('myapp:schueler_detail', schueler_id=schueler.id)
    if request.method == 'POST':
        schueler.delete()
        messages.success(request, 'Schüler wurde erfolgreich gelöscht.')
        return redirect('myapp:schueler_liste')
    return render(request, 'myapp/schueler_loeschen.html', {'schueler': schueler})

def mahnung_liste(request):
    mahnungen = Mahnung.objects.filter(istBearbeitet=False).select_related('ausleihe__exemplar__buch', 'ausleihe__schueler')
    return render(request, 'myapp/mahnung_liste.html', {'mahnungen': mahnungen})

def mahnung_detail(request, mahnung_id):
    mahnung = get_object_or_404(Mahnung, id=mahnung_id)
    return render(request, 'myapp/mahnung_detail.html', {'mahnung': mahnung})

def mahnung_erstellen(request, ausleihe_id):
    ausleihe = get_object_or_404(Ausleihe, id=ausleihe_id)
    if request.method == 'POST':
        form = MahnungForm(request.POST)
        if form.is_valid():
            mahnung = form.save(commit=False)
            mahnung.ausleihe = ausleihe
            mahnung.save()
            rechnung = mahnung.erstelleRechnung()
            if rechnung:
                messages.success(request, 'Mahnung und Rechnung wurden erfolgreich erstellt.')
            else:
                messages.success(request, 'Mahnung wurde erfolgreich erstellt.')
            return redirect('myapp:mahnung_detail', mahnung_id=mahnung.id)
    else:
        form = MahnungForm()
    return render(request, 'myapp/mahnung_form.html', {'form': form, 'ausleihe': ausleihe})

def rechnung_liste(request):
    rechnungen = Rechnung.objects.filter(istBezahlt=False).select_related('ausleihe__exemplar__buch', 'ausleihe__schueler')
    return render(request, 'myapp/rechnung_liste.html', {'rechnungen': rechnungen})

def rechnung_detail(request, rechnung_id):
    rechnung = get_object_or_404(Rechnung, id=rechnung_id)
    return render(request, 'myapp/rechnung_detail.html', {'rechnung': rechnung})

def rechnung_bezahlen(request, rechnung_id):
    rechnung = get_object_or_404(Rechnung, id=rechnung_id)
    if not rechnung.istBezahlt:
        rechnung.markiereAlsBezahlt()
        messages.success(request, 'Rechnung wurde als bezahlt markiert.')
    return redirect('myapp:rechnung_detail', rechnung_id=rechnung.id)

def buch_loeschen(request, buch_id):
    buch = get_object_or_404(Buch, id=buch_id)
    if buch.exemplare.exists():
        messages.error(request, 'Das Buch kann nicht gelöscht werden, da noch Exemplare vorhanden sind.')
        return redirect('myapp:buch_detail', buch_id=buch.id)
    if request.method == 'POST':
        buch.delete()
        messages.success(request, 'Buch wurde erfolgreich gelöscht.')
        return redirect('myapp:buch_liste')
    return render(request, 'myapp/buch_loeschen.html', {'buch': buch})

def exemplar_liste(request):
    exemplare = BuchExemplar.objects.all().select_related('buch')
    return render(request, 'myapp/exemplar_liste.html', {'exemplare': exemplare})

def exemplar_detail(request, exemplar_id):
    exemplar = get_object_or_404(BuchExemplar, id=exemplar_id)
    return render(request, 'myapp/exemplar_detail.html', {'exemplar': exemplar})

def exemplar_bearbeiten(request, exemplar_id):
    exemplar = get_object_or_404(BuchExemplar, id=exemplar_id)
    if request.method == 'POST':
        form = BuchExemplarForm(request.POST, instance=exemplar)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exemplar wurde erfolgreich aktualisiert.')
            return redirect('myapp:exemplar_detail', exemplar_id=exemplar.id)
    else:
        form = BuchExemplarForm(instance=exemplar)
    return render(request, 'myapp/exemplar_form.html', {'form': form, 'exemplar': exemplar})

def exemplar_loeschen(request, exemplar_id):
    exemplar = get_object_or_404(BuchExemplar, id=exemplar_id)
    if Ausleihe.objects.filter(exemplar=exemplar, istZurueckgegeben=False).exists():
        messages.error(request, 'Das Exemplar kann nicht gelöscht werden, da es noch ausgeliehen ist.')
        return redirect('myapp:exemplar_detail', exemplar_id=exemplar.id)
    if request.method == 'POST':
        exemplar.delete()
        messages.success(request, 'Exemplar wurde erfolgreich gelöscht.')
        return redirect('myapp:exemplar_liste')
    return render(request, 'myapp/exemplar_loeschen.html', {'exemplar': exemplar})
