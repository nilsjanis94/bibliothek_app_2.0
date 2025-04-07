from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Buch, BuchExemplar, Schüler, Ausleihe
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
    if request.method == 'POST':
        exemplar_id = request.POST.get('exemplar_id')
        schueler_id = request.POST.get('schueler_id')
        
        exemplar = get_object_or_404(BuchExemplar, id=exemplar_id)
        schueler = get_object_or_404(Schüler, id=schueler_id)
        
        # Prüfe, ob das Exemplar verfügbar ist
        if not exemplar.istVerfügbar():
            messages.error(request, 'Das Exemplar ist nicht verfügbar.')
            return redirect('myapp:ausleihe_neu')
        
        if not schueler.kannAusleihen():
            messages.error(request, 'Der Schüler kann keine Bücher ausleihen.')
            return redirect('myapp:ausleihe_neu')
        
        ausleihe = Ausleihe(
            exemplar=exemplar,
            schüler=schueler,
            ausleihdatum=date.today(),
            fälligkeitsdatum=date.today() + timedelta(days=14)
        )
        ausleihe.save()
        
        exemplar.setStatusAusgeliehen()
        
        messages.success(request, 'Ausleihe erfolgreich erstellt.')
        return redirect('myapp:ausleihe_detail', ausleihe_id=ausleihe.id)
    
    # Hole nur Exemplare, die wirklich verfügbar sind
    exemplare = BuchExemplar.objects.filter(status='verfügbar').exclude(
        ausleihen__istZurückgegeben=False
    )
    schueler = Schüler.objects.all()
    
    # Vorausgewähltes Exemplar oder Schüler
    vorausgewaehltes_exemplar = request.GET.get('exemplar_id')
    vorausgewaehlter_schueler = request.GET.get('schueler_id')
    
    context = {
        'exemplare': exemplare,
        'schueler': schueler,
        'vorausgewaehltes_exemplar': vorausgewaehltes_exemplar,
        'vorausgewaehlter_schueler': vorausgewaehlter_schueler
    }
    
    return render(request, 'myapp/ausleihe_neu.html', context)

def ausleihe_rueckgabe(request, ausleihe_id):
    ausleihe = get_object_or_404(Ausleihe, id=ausleihe_id)
    
    if ausleihe.istZurückgegeben:
        messages.error(request, 'Das Buch wurde bereits zurückgegeben.')
        return redirect('myapp:ausleihe_detail', ausleihe_id=ausleihe.id)
    
    ausleihe.zurueckgeben()
    
    messages.success(request, 'Rückgabe erfolgreich registriert.')
    return redirect('myapp:ausleihe_detail', ausleihe_id=ausleihe.id)

def exemplar_neu(request):
    if request.method == 'POST':
        buch_id = request.POST.get('buch_id')
        inventarnummer = request.POST.get('inventarnummer')
        anschaffungsdatum = request.POST.get('anschaffungsdatum')
        zustand = request.POST.get('zustand')
        
        buch = get_object_or_404(Buch, id=buch_id)
        
        exemplar = BuchExemplar(
            buch=buch,
            inventarnummer=inventarnummer,
            anschaffungsdatum=anschaffungsdatum,
            zustand=zustand,
            status='verfügbar'
        )
        exemplar.save()
        
        messages.success(request, f'Exemplar für "{buch.titel}" erfolgreich hinzugefügt.')
        return redirect('myapp:buch_detail', buch_id=buch.id)
    
    buecher = Buch.objects.all()
    vorausgewaehltes_buch = request.GET.get('buch_id')
    
    context = {
        'buecher': buecher,
        'vorausgewaehltes_buch': vorausgewaehltes_buch,
        'heute': date.today().strftime('%Y-%m-%d')
    }
    
    return render(request, 'myapp/exemplar_neu.html', context)
