from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Buch, BuchExemplar, Schüler, Ausleihe
from .forms import AusleiheForm, BuchForm, BuchExemplarForm, SchülerForm
from datetime import datetime, timedelta, date
from django.contrib import messages

def index(request):
    anzahl_buecher = Buch.objects.count()
    anzahl_exemplare = BuchExemplar.objects.count()
    anzahl_schueler = Schüler.objects.count()
    anzahl_ausleihen = Ausleihe.objects.filter(istZurückgegeben=False).count()
    
    context = {
        'anzahl_buecher': anzahl_buecher,
        'anzahl_exemplare': anzahl_exemplare,
        'anzahl_schueler': anzahl_schueler,
        'anzahl_ausleihen': anzahl_ausleihen,
    }
    return render(request, 'myapp/index.html', context)

def buch_liste(request):
    buecher = Buch.objects.all()
    return render(request, 'myapp/buch_liste.html', {'buecher': buecher})

def buch_detail(request, buch_id):
    buch = get_object_or_404(Buch, id=buch_id)
    exemplare = buch.getBuchExemplare()
    return render(request, 'myapp/buch_detail.html', {'buch': buch, 'exemplare': exemplare})

def schueler_liste(request):
    schueler = Schüler.objects.all()
    return render(request, 'myapp/schueler_liste.html', {'schueler': schueler})

def schueler_detail(request, schueler_id):
    schueler = get_object_or_404(Schüler, id=schueler_id)
    ausleihen = schueler.getAktuelleAusleihen()
    return render(request, 'myapp/schueler_detail.html', {'schueler': schueler, 'ausleihen': ausleihen})

def ausleihe_liste(request):
    ausleihen = Ausleihe.objects.filter(istZurückgegeben=False)
    return render(request, 'myapp/ausleihe_liste.html', {'ausleihen': ausleihen})

def ausleihe_detail(request, ausleihe_id):
    ausleihe = get_object_or_404(Ausleihe, id=ausleihe_id)
    return render(request, 'myapp/ausleihe_detail.html', {'ausleihe': ausleihe})

def ausleihe_neu(request):
    # Vorausgewähltes Exemplar oder Schüler
    exemplar_id = request.GET.get('exemplar_id')
    schueler_id = request.GET.get('schueler_id')
    
    if request.method == 'POST':
        form = AusleiheForm(request.POST, exemplar_id=exemplar_id, schueler_id=schueler_id)
        if form.is_valid():
            ausleihe = form.save(commit=False)
            ausleihe.ausleihdatum = date.today()
            ausleihe.save()
            
            # Status des Exemplars aktualisieren
            ausleihe.exemplar.setStatusAusgeliehen()
            
            messages.success(request, 'Ausleihe erfolgreich erstellt.')
            return redirect('myapp:ausleihe_detail', ausleihe_id=ausleihe.id)
    else:
        form = AusleiheForm(exemplar_id=exemplar_id, schueler_id=schueler_id)
    
    return render(request, 'myapp/ausleihe_form.html', {'form': form})

def ausleihe_rueckgabe(request, ausleihe_id):
    ausleihe = get_object_or_404(Ausleihe, id=ausleihe_id)
    
    if ausleihe.istZurückgegeben:
        messages.error(request, 'Das Buch wurde bereits zurückgegeben.')
        return redirect('myapp:ausleihe_detail', ausleihe_id=ausleihe.id)
    
    ausleihe.zurueckgeben()
    
    messages.success(request, 'Rückgabe erfolgreich registriert.')
    return redirect('myapp:ausleihe_detail', ausleihe_id=ausleihe.id)

def exemplar_neu(request):
    buch_id = request.GET.get('buch_id')
    
    if request.method == 'POST':
        form = BuchExemplarForm(request.POST, buch_id=buch_id)
        if form.is_valid():
            exemplar = form.save()
            buch = exemplar.buch
            messages.success(request, f'Exemplar für "{buch.titel}" erfolgreich hinzugefügt.')
            return redirect('myapp:buch_detail', buch_id=buch.id)
    else:
        form = BuchExemplarForm(buch_id=buch_id)
    
    return render(request, 'myapp/exemplar_form.html', {'form': form})

def buch_neu(request):
    if request.method == 'POST':
        form = BuchForm(request.POST)
        if form.is_valid():
            buch = form.save()
            messages.success(request, f'Buch "{buch.titel}" erfolgreich hinzugefügt.')
            return redirect('myapp:buch_detail', buch_id=buch.id)
    else:
        form = BuchForm()
    
    return render(request, 'myapp/buch_form.html', {'form': form})

def buch_bearbeiten(request, buch_id):
    buch = get_object_or_404(Buch, id=buch_id)
    
    if request.method == 'POST':
        form = BuchForm(request.POST, instance=buch)
        if form.is_valid():
            buch = form.save()
            messages.success(request, f'Buch "{buch.titel}" erfolgreich aktualisiert.')
            return redirect('myapp:buch_detail', buch_id=buch.id)
    else:
        form = BuchForm(instance=buch)
    
    return render(request, 'myapp/buch_form.html', {'form': form, 'buch': buch})

def schueler_neu(request):
    if request.method == 'POST':
        form = SchülerForm(request.POST)
        if form.is_valid():
            schueler = form.save()
            messages.success(request, f'Schüler "{schueler.vorname} {schueler.name}" erfolgreich hinzugefügt.')
            return redirect('myapp:schueler_detail', schueler_id=schueler.id)
    else:
        form = SchülerForm()
    
    return render(request, 'myapp/schueler_form.html', {'form': form})

def schueler_bearbeiten(request, schueler_id):
    schueler = get_object_or_404(Schüler, id=schueler_id)
    
    if request.method == 'POST':
        form = SchülerForm(request.POST, instance=schueler)
        if form.is_valid():
            schueler = form.save()
            messages.success(request, f'Schüler "{schueler.vorname} {schueler.name}" erfolgreich aktualisiert.')
            return redirect('myapp:schueler_detail', schueler_id=schueler.id)
    else:
        form = SchülerForm(instance=schueler)
    
    return render(request, 'myapp/schueler_form.html', {'form': form, 'schueler': schueler})
