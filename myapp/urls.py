from django.urls import path
from . import views

app_name = 'myapp'  # Namespace für die URLs

urlpatterns = [
    path('', views.index, name='index'),
    path('buecher/', views.buch_liste, name='buch_liste'),
    path('buecher/<int:buch_id>/', views.buch_detail, name='buch_detail'),
    path('buch/neu/', views.buch_neu, name='buch_neu'),
    path('buch/<int:buch_id>/bearbeiten/', views.buch_bearbeiten, name='buch_bearbeiten'),
    path('schueler/', views.schueler_liste, name='schueler_liste'),
    path('schueler/<int:schueler_id>/', views.schueler_detail, name='schueler_detail'),
    path('schueler/neu/', views.schueler_neu, name='schueler_neu'),
    path('schueler/<int:schueler_id>/bearbeiten/', views.schueler_bearbeiten, name='schueler_bearbeiten'),
    path('ausleihen/', views.ausleihe_liste, name='ausleihe_liste'),
    path('ausleihe/<int:ausleihe_id>/', views.ausleihe_detail, name='ausleihe_detail'),
    path('ausleihe/neu/', views.ausleihe_neu, name='ausleihe_neu'),
    path('ausleihe/<int:ausleihe_id>/rueckgabe/', views.ausleihe_rueckgabe, name='ausleihe_rueckgabe'),
    path('exemplar/neu/', views.exemplar_neu, name='exemplar_neu'),
]
