# Bibliothek 2.0

Eine Django-Anwendung zur Verwaltung einer Schulbibliothek mit Buchausleih- und Verwaltungsfunktionen.

## Beschreibung

Diese Webanwendung unterstützt die Verwaltung des Buchbestands einer Schulbibliothek. Sie ermöglicht die Registrierung von Büchern und deren Exemplaren, die Verwaltung von Schülern sowie das Ausleihen und Zurückgeben von Büchern. Die Anwendung behält automatisch den Überblick über fällige Rückgaben und kann Mahnungen und Rechnungen erstellen.

## Funktionen

- Buchverwaltung (Hinzufügen, Bearbeiten, Löschen)
- Buchexemplarverwaltung mit Inventarnummern und Zustandserfassung
- Schülerverwaltung mit Sperr- und Mahnfunktionen
- Ausleihprozess (Buch ausleihen, zurückgeben)
- Automatische Status-Updates bei Ausleihe und Rückgabe
- Überfälligkeitsverfolgung für nicht zurückgegebene Bücher
- Mahnungsverwaltung
- Rechnungserstellung für verlorene oder beschädigte Bücher

## Technologien

- Python 3.x
- Django 4.x
- HTML, CSS
- Bootstrap 5 für die Benutzeroberfläche
- SQLite für die Datenbankunterstützung

## Installation

1. Repository klonen:
```bash
git clone https://github.com/dein-benutzername/bibliothek2.0.git
cd bibliothek2.0
```

2. Virtuelle Umgebung erstellen und aktivieren:
```bash
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
```

3. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

4. Datenbankmigrationen ausführen:
```bash
python manage.py migrate
```

5. Superuser erstellen:
```bash
python manage.py createsuperuser
```

6. Server starten:
```bash
python manage.py runserver
```

## Nutzung

1. Öffne im Browser die Adresse: http://127.0.0.1:8000/
2. Admin-Bereich unter: http://127.0.0.1:8000/admin/
3. Über die Admin-Oberfläche können Bücher, Exemplare und Schüler angelegt werden
4. Die Hauptnavigation erlaubt Zugriff auf alle Funktionen

## Modellstruktur

- **Buch**: Grundlegende Buchinformationen (ISBN, Titel, Autor...)
- **BuchExemplar**: Physische Exemplare eines Buches mit Inventarnummer
- **Schüler**: Informationen über ausleihberechtigte Schüler
- **Ausleihe**: Verbindung zwischen Exemplaren und Schülern
- **Mahnung**: Mahnungen für überfällige Ausleihen
- **Rechnung**: Zahlungsforderungen für verlorene/beschädigte Bücher

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
