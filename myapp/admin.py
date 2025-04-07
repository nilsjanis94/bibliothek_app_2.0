from django.contrib import admin
from .models import Buch, BuchExemplar, Schueler, Ausleihe, Rechnung, Mahnung
# Register your models here.
admin.site.register(Buch)
admin.site.register(BuchExemplar)
admin.site.register(Schueler)
admin.site.register(Ausleihe)
admin.site.register(Rechnung)
admin.site.register(Mahnung)
