# Generated by Django 5.2 on 2025-04-07 10:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_ausleihe_exemplar'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Schüler',
            new_name='Schueler',
        ),
        migrations.RenameField(
            model_name='ausleihe',
            old_name='fälligkeitsdatum',
            new_name='faelligkeitsdatum',
        ),
        migrations.RenameField(
            model_name='ausleihe',
            old_name='istZurückgegeben',
            new_name='istZurueckgegeben',
        ),
        migrations.RenameField(
            model_name='ausleihe',
            old_name='schüler',
            new_name='schueler',
        ),
        migrations.RenameField(
            model_name='schueler',
            old_name='anzahlVerspätungen',
            new_name='anzahlVerspaetungen',
        ),
    ]
