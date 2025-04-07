from django.urls import path
from . import views

app_name = 'myapp'  # Namespace für die URLs

urlpatterns = [
    path('', views.index, name='index'),
    path('buecher/', views.buch_liste, name='buch_liste'),
    path('buecher/<int:buch_id>/', views.buch_detail, name='buch_detail'),
    path('schueler/', views.schueler_liste, name='schueler_liste'),
    path('schueler/<int:schueler_id>/', views.schueler_detail, name='schueler_detail'),
    path('ausleihen/', views.ausleihe_liste, name='ausleihe_liste'),
    path('ausleihe/<int:ausleihe_id>/', views.ausleihe_detail, name='ausleihe_detail'),
    path('ausleihe/new/', views.ausleihe_neu, name='ausleihe_neu'),
    path('ausleihe/<int:ausleihe_id>/rueckgabe/', views.ausleihe_rueckgabe, name='ausleihe_rueckgabe'),
    path('exemplar/new/', views.exemplar_neu, name='exemplar_neu'),
]
