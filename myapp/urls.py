from django.urls import path
from . import views

app_name = 'myapp'  # Namespace für die URLs

urlpatterns = [
    path('', views.index, name='index'),
    path('buecher/', views.buch_liste, name='buch_liste'),
    path('buecher/<int:buch_id>/', views.buch_detail, name='buch_detail'),
    path('buecher/neu/', views.buch_neu, name='buch_neu'),
    path('buecher/<int:buch_id>/bearbeiten/', views.buch_bearbeiten, name='buch_bearbeiten'),
    path('buecher/<int:buch_id>/loeschen/', views.buch_loeschen, name='buch_loeschen'),
    path('exemplare/', views.exemplar_liste, name='exemplar_liste'),
    path('exemplare/<int:exemplar_id>/', views.exemplar_detail, name='exemplar_detail'),
    path('exemplare/neu/', views.exemplar_neu, name='exemplar_neu'),
    path('exemplare/<int:exemplar_id>/bearbeiten/', views.exemplar_bearbeiten, name='exemplar_bearbeiten'),
    path('exemplare/<int:exemplar_id>/loeschen/', views.exemplar_loeschen, name='exemplar_loeschen'),
    path('schueler/', views.schueler_liste, name='schueler_liste'),
    path('schueler/<int:schueler_id>/', views.schueler_detail, name='schueler_detail'),
    path('schueler/neu/', views.schueler_neu, name='schueler_neu'),
    path('schueler/<int:schueler_id>/bearbeiten/', views.schueler_bearbeiten, name='schueler_bearbeiten'),
    path('schueler/<int:schueler_id>/loeschen/', views.schueler_loeschen, name='schueler_loeschen'),
    path('ausleihen/', views.ausleihe_liste, name='ausleihe_liste'),
    path('ausleihen/<int:ausleihe_id>/', views.ausleihe_detail, name='ausleihe_detail'),
    path('ausleihen/neu/', views.ausleihe_neu, name='ausleihe_neu'),
    path('ausleihen/<int:ausleihe_id>/rueckgabe/', views.ausleihe_rueckgabe, name='ausleihe_rueckgabe'),
    path('mahnungen/', views.mahnung_liste, name='mahnung_liste'),
    path('mahnungen/<int:mahnung_id>/', views.mahnung_detail, name='mahnung_detail'),
    path('ausleihe/<int:ausleihe_id>/mahnung/erstellen/', views.mahnung_erstellen, name='mahnung_erstellen'),
    path('rechnungen/', views.rechnung_liste, name='rechnung_liste'),
    path('rechnungen/<int:rechnung_id>/', views.rechnung_detail, name='rechnung_detail'),
    path('rechnungen/<int:rechnung_id>/bezahlen/', views.rechnung_bezahlen, name='rechnung_bezahlen'),
]
